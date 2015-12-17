"""
Django AppConfig module for the Gating app
"""
from django.apps import AppConfig


class GatingConfig(AppConfig):
    name = 'openedx.core.djangoapps.gating'

    def ready(self):
        from openedx.core.djangoapps.gating import signals
