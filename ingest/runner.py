import logging
import subprocess
from datetime import datetime, timedelta

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from .spiders import *


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


def execute_cmd(cmd, job_name):
    subprocess.run(cmd, shell=True)
    logger.info(f"Finished job {job_name}")


def run():

    scheduler = BlockingScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")

    scheduler.add_job(
        execute_cmd,
        args=["scrapy crawl datafeeds", "fetch_odds"],
        trigger=CronTrigger(minute="*/15"),
        id="fetch_odds",
        max_instances=1,
        replace_existing=True,
        next_run_time=datetime.now(),
    )
    logger.info("Added job 'fetch_odds'.")

    cmd = "scrapy list | grep -v datafeeds | xargs -n 1 scrapy crawl"
    scheduler.add_job(
        execute_cmd,
        args=[cmd, "fetch_sports"],
        trigger=CronTrigger(second="*/30"),
        id="fetch_sports",
        max_instances=1,
        next_run_time=datetime.now() + timedelta(seconds=10),
        replace_existing=True,
    )
    logger.info("Added job 'fetch_sports'.")

    scheduler.add_job(
        delete_old_job_executions,
        trigger=CronTrigger(
            day_of_week="mon", hour="00", minute="00"
        ),  # Midnight on Monday, before start of the next work week.
        id="delete_old_job_executions",
        max_instances=1,
        replace_existing=True,
    )
    logger.info("Added weekly job: 'delete_old_job_executions'.")

    try:
        logger.info("Starting scheduler...")
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("Stopping scheduler...")
        scheduler.shutdown()
        logger.info("Scheduler shut down successfully!")
