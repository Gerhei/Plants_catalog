import requests
import json

from django.core.management.base import BaseCommand, CommandError

from main_app.settings import HEADERS
from news.parsers.RIA_parser import RIA_Parser


class Command(BaseCommand):

    def handle(self, *args, **options):
        parser = RIA_Parser(HEADERS)
        data = parser.parse_page('https://ria.ru/20220418/derevya-1784098633.html')
        with open('news.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)