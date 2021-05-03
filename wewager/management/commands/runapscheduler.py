# runapscheduler.py
import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from ingest import runner


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        runner.run()