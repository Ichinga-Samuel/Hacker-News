from django.core.management.base import BaseCommand, CommandError
from news.script import NewsApi


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--comments', action='store_true', help='recursively load comments')

    def handle(self, *args, **options):
        try:
            api = NewsApi()
            value = options['comments']
            api.get_latest(with_comments=value)
        except Exception as err:
            print(err)
            self.stderr.write('error')
