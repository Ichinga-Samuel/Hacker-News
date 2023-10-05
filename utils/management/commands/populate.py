import asyncio

from django.core.management.base import BaseCommand, CommandError

from ...api import API


class Command(BaseCommand):
    help = 'Populate database with data from Hacker News API'

    def add_arguments(self, parser):
        parser.add_argument('timeout', nargs='?', type=int, default=60)
        parser.add_argument('size', nargs='?', type=int, default=2000)

    def handle(self, *args, **options):
        timeout = options['timeout']
        size = options['size']
        api = API(timeout=timeout, size=size)
        try:
            asyncio.run(api.initiate())
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS('Successfully closed'))
            api.close()
        except Exception as e:
            api.close()
            raise CommandError(e)
