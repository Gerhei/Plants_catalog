from django.core.management.base import BaseCommand, CommandError
from plants.models import *

class Command(BaseCommand):

    def handle(self, *args, **options):
        categories=Taxons.objects.all()
        for cat in categories:
            cat.save()
        #self.stdout.write(plant.name.replace(' (растение)',''))