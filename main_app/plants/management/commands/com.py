from django.core.management.base import BaseCommand, CommandError
from plants.models import *

class Command(BaseCommand):

    def handle(self, *args, **options):
        categories=Categories.objects.all()
        for cat in categories:
            cat.save()
        #self.stdout.write(plant.name.replace(' (растение)',''))