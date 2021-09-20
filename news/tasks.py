import asyncio
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from .async_script import get_latest


executors = {
    'default': ThreadPoolExecutor(20),
    'processpool': ProcessPoolExecutor(5)
}

job_defaults = {
    'coalesce': True,
    'max_instances': 3
}


def main():
    try:
        asyncio.run(get_latest())
    except Exception as err:
        print(err)


def start():
    scheduler = BackgroundScheduler(executors=executors, job_defaults=job_defaults)
    scheduler.add_job(main, 'interval', minutes=5)
    scheduler.start()
