"""
Views related to EdxNotes.
"""
import json
import logging
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest, Http404
from django.conf import settings
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_GET
from edxmako.shortcuts import render_to_response
from opaque_keys.edx.keys import CourseKey
from courseware.courses import get_course_with_access
from courseware.model_data import FieldDataCache
from courseware.module_render import get_module_for_descriptor
from util.json_request import JsonResponse, JsonResponseBadRequest
from edxnotes.exceptions import EdxNotesParseError, EdxNotesServiceUnavailable
from edxnotes.helpers import (
    get_edxnotes_id_token,
    get_notes,
    is_feature_enabled,
    get_course_position,
    DEFAULT_PAGE,
    DEFAULT_PAGE_SIZE,
)


log = logging.getLogger(__name__)


@login_required
def edxnotes(request, course_id):
    """
    Displays the EdxNotes page.

    Arguments:
        request: HTTP request object
        course_id: course id

    Returns:
        Rendered HTTP response.
    """
    course_key = CourseKey.from_string(course_id)
    course = get_course_with_access(request.user, "load", course_key)

    if not is_feature_enabled(course):
        raise Http404

    try:
        notes_info = get_notes(request, course)
    except EdxNotesServiceUnavailable:
        raise Http404

    context = {
        "course": course,
        "notes_endpoint": reverse("notes", kwargs={"course_id": course_id}),
        "notes": notes_info,
        "debug": json.dumps(settings.DEBUG),
        'position': None,
    }

    if len(json.loads(notes_info)['results']) == 0:
        field_data_cache = FieldDataCache.cache_for_descriptor_descendents(
            course.id, request.user, course, depth=2
        )
        course_module = get_module_for_descriptor(
            request.user, request, course, field_data_cache, course_key, course=course
        )
        position = get_course_position(course_module)
        if position:
            context.update({
                'position': position,
            })

    return render_to_response("edxnotes/edxnotes.html", context)


@require_GET
@login_required
def notes(request, course_id):
    """
    Notes view to handle list and search requests for pagination.

    Query parameters:
        page: requested or default page number
        page_size: requested or default page size
        text: text string to search. If `text` param is missing then get all the
              notes for the current user for this course else get only those notes
              which contain the `text` value.

    Arguments:
        request: HTTP request object
        course_id: course id

    Returns:
        Paginated response as JSON
    """
    course_key = CourseKey.from_string(course_id)
    course = get_course_with_access(request.user, 'load', course_key)

    if not is_feature_enabled(course):
        raise Http404

    page = request.GET.get('page') or DEFAULT_PAGE
    page_size = request.GET.get('page_size') or DEFAULT_PAGE_SIZE
    text = request.GET.get('text')

    try:
        notes_info = get_notes(
            request,
            course,
            page=page,
            page_size=page_size,
            text=text
        )
    except (EdxNotesParseError, EdxNotesServiceUnavailable) as err:
        return JsonResponseBadRequest({"error": err.message}, status=500)

    return HttpResponse(notes_info, content_type="application/json")


# pylint: disable=unused-argument
@login_required
def get_token(request, course_id):
    """
    Get JWT ID-Token, in case you need new one.
    """
    return HttpResponse(get_edxnotes_id_token(request.user), content_type='text/plain')


@login_required
def edxnotes_visibility(request, course_id):
    """
    Handle ajax call from "Show notes" checkbox.
    """
    course_key = CourseKey.from_string(course_id)
    course = get_course_with_access(request.user, "load", course_key)
    field_data_cache = FieldDataCache([course], course_key, request.user)
    course_module = get_module_for_descriptor(
        request.user, request, course, field_data_cache, course_key, course=course
    )

    if not is_feature_enabled(course):
        raise Http404

    try:
        visibility = json.loads(request.body)["visibility"]
        course_module.edxnotes_visibility = visibility
        course_module.save()
        return JsonResponse(status=200)
    except (ValueError, KeyError):
        log.warning(
            "Could not decode request body as JSON and find a boolean visibility field: '%s'", request.body
        )
        return JsonResponseBadRequest()
