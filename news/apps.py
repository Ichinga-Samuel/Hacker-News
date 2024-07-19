from django.apps import AppConfig
from django.conf import settings

# os.environ.get('RUN_MAIN')


class NewsConfig(AppConfig):
    name = 'news'

    def ready(self):
        from .tasks import start
        start()

