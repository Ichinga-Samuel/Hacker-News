import asyncio

from django.core.management.base import BaseCommand, CommandError

from ...api import API


class Command(BaseCommand):
    help = 'Walk back from the maximum item'

    def add_arguments(self, parser):
        parser.add_argument('timeout', nargs='?', type=int, default=120)
        parser.add_argument('end', nargs='?', type=int, default=0)

    def handle(self, *args, **options):
        timeout = options['timeout']
        end = options['end']
        api = API(timeout=timeout)
        try:
            asyncio.run(api.walk_back(end=end))
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS('Successfully closed'))
            api.close()
        except Exception as e:
            api.close()
            raise CommandError(e)
