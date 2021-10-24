from django.core.management.base import BaseCommand, CommandError
import concurrent.futures
import asyncio
from news.async_script import get_latest_stories


def main(value):
    asyncio.run(get_latest_stories("https://hacker-news.firebaseio.com/v0/topstories.json", with_comments=value))


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--comments', action='store_true', help='recursively load comments')

    def handle(self, *args, **options):
        try:
            value = options['comments']
            with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
                executor.map(main, [value])
        except Exception as err:
            print(err)
            self.stderr.write('error')
