import asyncio
import concurrent.futures
from django.core.management.base import BaseCommand, CommandError
from news.script import get_latest_jobs


def main():

    asyncio.run(get_latest_jobs())


class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
                executor.submit(main)
        except Exception as err:
            executor.shutdown(wait=False, cancel_futures=True)
            print(err)
            self.stderr.write()
