from django.core.management.base import BaseCommand, CommandError
from plants.models import Plants

class Command(BaseCommand):

    def handle(self, *args, **options):
        pass
        #self.stdout.write(plant.name.replace(' (растение)',''))