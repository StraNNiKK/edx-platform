"""
Defines common methods shared by Teams classes
"""

from django.conf import settings


TEAM_DISCUSSION_CONTEXT = 'standalone'


def is_feature_enabled(course):
    """
    Returns True if the teams feature is enabled.
    """
    print settings.FEATURES.get('ENABLE_TEAMS', False)
    print course.teams_enabled
    return settings.FEATURES.get('ENABLE_TEAMS', False) and course.teams_enabled
