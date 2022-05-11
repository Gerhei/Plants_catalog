from django.core.management.base import BaseCommand, CommandError
from plants.models import *
from django.db import models
from django.utils.encoding import force_str, smart_bytes

class Command(BaseCommand):

    def handle(self, *args, **options):
        pass