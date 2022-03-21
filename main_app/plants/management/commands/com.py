from django.core.management.base import BaseCommand, CommandError
from plants.models import *
from django.db import models

import requests
import urllib3
from django.core.files import File
from django.core.files.images import ImageFile

class Command(BaseCommand):

    def handle(self, *args, **options):
        plants=Plants.objects.all()
        path=r'C:\Users\USER\Desktop\plants_image'

        iter=0
        for plant in plants:
            if plant.image:
                iter+=1
        self.stdout.write(str(iter))