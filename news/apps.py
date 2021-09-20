from django.apps import AppConfig
import os


class NewsConfig(AppConfig):
    name = 'news'

    def ready(self):
        res = os.environ.get('RUN_MAIN')
        if res:
            from .tasks import start
            start()

