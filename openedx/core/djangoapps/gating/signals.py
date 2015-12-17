from django.dispatch import receiver

from opaque_keys.edx.keys import CourseKey

from xmodule.modulestore.django import modulestore, SignalHandler

from openedx.core.djangoapps.gating import api as gating_api

from courseware.models import SCORE_CHANGED


@receiver(SCORE_CHANGED)
def handle_score_changed(sender, **kwargs):
    course = modulestore().get_course(CourseKey.from_string(kwargs.get('course_id')))
    if course.enable_subsection_gating:
        gating_api.fulfill_prerequisite(
            kwargs.get('user_id'),
            course,
            kwargs.get('usage_id')
        )


@receiver(SignalHandler.item_deleted)
def handle_item_deleted(sender, **kwargs):
    gating_api.remove_prerequisite(kwargs.get('usage_key'))
