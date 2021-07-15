from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from .script import NewsApi


def start():
    scheduler = BackgroundScheduler()
    inst = NewsApi()
    job = inst.get_latest
    scheduler.add_job(job, 'interval', minutes=10)
    scheduler.start()
