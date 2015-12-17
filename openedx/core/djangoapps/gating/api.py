import logging

from django.conf import settings
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User

from opaque_keys.edx.keys import CourseKey, UsageKey

from xmodule.modulestore.django import modulestore
from xmodule.util.xblock import get_xblock_parent

from milestones import api as milestones_api

from openedx.core.djangoapps.gating.exceptions import GatingValidationError


log = logging.getLogger(__name__)

GATING_NAMESPACE_QUALIFIER = '.gating'


def _get_prerequisite_milestone(prereq_content_key):
    milestones = milestones_api.get_milestones("{usage_key}{qualifier}".format(
        usage_key=prereq_content_key,
        qualifier=GATING_NAMESPACE_QUALIFIER
    ))

    if not milestones:
        log.warning("Could not find gating milestone for prereq UsageKey {}".format(prereq_content_key))
        return None

    if len(milestones) > 1:
        # We should only ever have one gating milestone per UsageKey
        # Log a warning here and pick the first one
        log.warning("Multiple gating milestones found for prereq UsageKey {}".format(prereq_content_key))

    return milestones[0]


def _find_gating_course_content_milestones(course_key, content_key, relationship):
    return [
        m for m in milestones_api.get_course_content_milestones(course_key, content_key, relationship)
        if GATING_NAMESPACE_QUALIFIER in m.get('namespace')
    ]


def _get_gating_course_content_milestone(course_key, content_key, relationship):
    try:
        return _find_gating_course_content_milestones(course_key, content_key, relationship)[0]
    except IndexError:
        return None


def _validate_min_score(min_score):
    message = "{min_score} is not a valid grade percentage"
    if min_score:
        try:
            min_score = int(min_score)
        except ValueError:
            raise GatingValidationError(message.format(min_score=min_score))

        if min_score < 0 or min_score > 100:
            raise GatingValidationError(message.format(min_score=min_score))


def milestones_active(default=None):
    """
    Decorator that checks the MILESTONES_APP feature flag to
    see if the milestones feature is active. If not, calls to
    the decorated function return the specified default value.

    Arguments:
        default (ANY): The value to return if the MILESTONES_APP feature flag is False

    Returns:
        ANY: The specified default value if the milestones feature is off,
        otherwise the result of the decorated function
    """
    def wrap(f):
        def function_wrapper(*args):
            if not settings.FEATURES.get('MILESTONES_APP', False):
                return default
            return f(*args)
        return function_wrapper
    return wrap


@milestones_active(default=[])
def get_prerequisites(course_key):
    """
    Find all the gating milestones associated with a course and the
    XBlock info associated with those gating milestones.

    Arguments:
        course_key (CourseKey): CourseKey of the course

    Returns:
        list: A list of dicts containing the milestone and associated XBlock info
    """
    course_content_milestones = milestones_api.get_course_content_milestones(course_key=unicode(course_key))

    ccm_by_id = {}
    block_ids = []
    for ccm in course_content_milestones:
        prereq_content_key = ccm['namespace'].replace(GATING_NAMESPACE_QUALIFIER, '')
        block_id = UsageKey.from_string(prereq_content_key).block_id
        block_ids.append(block_id)
        ccm_by_id[block_id] = ccm

    result = []
    for block in modulestore().get_items(course_key, qualifiers={'name': block_ids}):
        ccm = ccm_by_id.get(block.location.block_id)
        if ccm:
            ccm['block_display_name'] = block.display_name
            ccm['block_usage_key'] = unicode(block.location)
            result.append(ccm)

    return result


@milestones_active()
def add_prerequisite(course_key, prereq_content_key):
    """
    Creates a new Milestone and CourseContentMilestone indicating that
    the given course content fulfills a prerequisite for gating

    Arguments:
        course_key (CourseKey): CourseKey of the course
        prereq_content_key (UsageKey): UsageKey of the course content

    Returns:
        None
    """
    milestone = milestones_api.add_milestone(
        {
            'name': _('Gating milestone for {usage_key}').format(usage_key=unicode(prereq_content_key)),
            'namespace': "{usage_key}{qualifier}".format(
                usage_key=prereq_content_key,
                qualifier=GATING_NAMESPACE_QUALIFIER
            ),
            'description': _('System defined milestone'),
        },
        propagate=False
    )
    milestones_api.add_course_content_milestone(course_key, prereq_content_key, 'fulfills', milestone)


@milestones_active()
def remove_prerequisite(prereq_content_key):
    """
    Removes the Milestone and CourseContentMilestones related to the gating
    prerequisite which the given course content fulfills

    Arguments:
        prereq_content_key (UsageKey): UsageKey of the course content

    Returns:
        None
    """
    milestones = milestones_api.get_milestones("{usage_key}{qualifier}".format(
        usage_key=prereq_content_key,
        qualifier=GATING_NAMESPACE_QUALIFIER
    ))
    for milestone in milestones:
        milestones_api.remove_milestone(milestone.get('id'))


@milestones_active(default=False)
def is_prerequisite(course_key, prereq_content_key):
    """
    Returns True if there is at least one CourseContentMilestone
    which the given course content fulfills

    Arguments:
        course_key (CourseKey): CourseKey of the course
        prereq_content_key (UsageKey): UsageKey of the course content

    Returns:
        bool: True if the course content fulfills a CourseContentMilestone, otherwise False
    """
    return _get_gating_course_content_milestone(
        unicode(course_key),
        unicode(prereq_content_key),
        'fulfills'
    ) is not None


@milestones_active()
def set_required_content(course_key, gated_content_key, prereq_content_key, min_score):
    milestone = None
    for m in _find_gating_course_content_milestones(course_key, gated_content_key, 'requires'):
        if not prereq_content_key or prereq_content_key not in m.get('namespace'):
            milestones_api.remove_course_content_milestone(course_key, gated_content_key, m)
        else:
            milestone = m

    if prereq_content_key:
        _validate_min_score(min_score)
        if not milestone:
            milestone = _get_prerequisite_milestone(prereq_content_key)
        milestones_api.add_course_content_milestone(course_key, gated_content_key, 'requires', milestone, min_score)


@milestones_active(default=('', ''))
def get_required_content(course_key, gated_content_key):
    milestone = _get_gating_course_content_milestone(course_key, gated_content_key, 'requires')
    if milestone:
        return milestone.get('namespace', '').replace(GATING_NAMESPACE_QUALIFIER, ''), milestone.get('requirement', '')
    else:
        return None, None


@milestones_active(default=[])
def get_gated_content(course_key, user):
    """
    Queries milestones subsystem to see if the specified course is gated on one or more milestones,
    and if those milestones can be fulfilled via completion of a particular course content module
    """
    # Get the unfulfilled gating milestones for this course, for this user
    return [
        m['content_id'] for m in milestones_api.get_course_content_milestones(
            unicode(course_key),
            None,
            'requires',
            {'id': user.id}
        )
    ]


@milestones_active(default=False)
def fulfill_prerequisite(user_id, course, prereq_content_key):
    """
    Fulfills the gating prerequisite for the given user, if the grade
    for the given prereq exceeds the minimum grading requirement.

    Arguments:
        user_id (int): ID of User who is fulfilling the prerequisite
        course_key (CourseKey): CourseKey of the course
        prereq_content_key (UsageKey): UsageKey of the prerequisite course content

    Returns:
        None
    """
    xblock = modulestore().get_item(UsageKey.from_string(prereq_content_key))
    sequential = get_xblock_parent(xblock, 'sequential')
    if sequential:
        prereq_milestone = _get_gating_course_content_milestone(
            course.id,
            sequential.location.for_branch(None),
            'fulfills'
        )
        if prereq_milestone:
            gated_content_milestones = {}
            for m in _find_gating_course_content_milestones(course.id, None, 'requires'):
                milestone_id = m['id']
                gated_content = gated_content_milestones.get(milestone_id)
                if not gated_content:
                    gated_content = []
                    gated_content_milestones[milestone_id] = gated_content
                gated_content.append(m)

            gated_content = gated_content_milestones.get(prereq_milestone['id'])
            if gated_content:
                from courseware.grades import get_module_score
                user = User.objects.get(id=user_id)
                score = get_module_score(user, course, sequential) * 100
                for m in gated_content:
                    requirement = m['requirement']
                    try:
                        min_grade = int(requirement)
                    except (ValueError, TypeError):
                        min_grade = 100

                    if score >= min_grade:
                        milestones_api.add_user_milestone({'id': user_id}, prereq_milestone)
                    else:
                        milestones_api.remove_user_milestone({'id': user_id}, prereq_milestone)
