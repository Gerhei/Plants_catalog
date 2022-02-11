from django.core.management.base import BaseCommand, CommandError
from plants.models import *
from django.db import models

class Command(BaseCommand):

    def handle(self, *args, **options):
        plants=Plants.objects.filter(pk__lte=130)
        pk_set=[]
        for plant in plants:
            pk_set.append(plant.pk)

        descriptions=Descriptions.objects.filter(plant__pk__in=pk_set,category='')

        desc_set=[]
        for desc in descriptions:
            desc_set.append(desc.plant.pk)

        self.stdout.write('Plant id\tDesc id')
        for i in range(len(descriptions)):
            self.stdout.write(str(plants[i].pk)+'\t\t'+str(descriptions[i].plant.pk))