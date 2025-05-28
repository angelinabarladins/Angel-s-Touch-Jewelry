
from django.apps import AppConfig
from django.conf import settings
from django.contrib import admin


class Veb1Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'veb1'

    def ready(self):
        admin.site.site_header = settings.ADMIN_SITE_HEADER
