# runapscheduler.py
import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from ingest import runner


logger = logging.getLogger(__name__)

"""
def delete_old_job_executions(max_age=604_800):
    This job deletes all apscheduler job executions older than `max_age` from the database.
    DjangoJobExecution.objects.delete_old_job_executions(max_age)
"""

class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        # scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        runner.run()