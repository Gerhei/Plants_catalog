import requests
import json
from time import sleep
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db.models import ObjectDoesNotExist

from main_app.settings import HEADERS
from news.parsers.RIA_parser import RIA_Parser
from news.models import News

from dateutil import parser as date_parser


url = 'https://ria.ru/20220407/malina-1782398350.html'

class Command(BaseCommand):
    help = 'Starts the process of collecting new news from predefined pages'

    def add_arguments(self, parser):
        parser.add_argument('--pause', type=int, default=30,
                            help='Frequency in minutes with which the parser checks sites for new news')
        parser.add_argument('--parse_for_days', type=int, default=-1,
                            help='For what period (in days) '
                                      'the parser collects information. -1 means parse all news.')

    def handle(self, *args, **options):
        self.parse_for_days = options['parse_for_days']

        news_parser = RIA_Parser(HEADERS, 'Parse_logs.txt')
        # with open('news.json', 'w', encoding='utf-8') as file:
        #     json.dump(json_data, file, indent=4, ensure_ascii=False)
        while True:
            self.current_date = datetime.now()
            self.page_list_processing(news_parser)
            break
            # parse data from all sites
            #sleep(options['pause']*60)


    def page_list_processing(self, news_parser):
        self.stdout.write(f'Start parsing {news_parser.url_page_with_list_articles}')
        list_links = news_parser.get_list_urls_pages()
        list_links = self.get_links_for_non_exist_data_in_db(list_links)
        json_data = news_parser.get_json_list_pages(list_links)
        for key, item in json_data.items():
            self.save_to_model(item, key)

    def save_to_model(self, json_data, source_url=None):
        # For some reason the page was not parsed
        if not json_data:
            return

        # TODO Check date condition before page parsing
        publication_date = date_parser.parse(json_data['publication_date'], dayfirst=True)
        if self.parse_for_days != -1:
            # skip news if it is old
            if (self.current_date - publication_date) >= timedelta(days=self.parse_for_days):
                return
        #if timedelta(days=self.options[''])
        news = News()
        news.title = json_data['title']
        news.publication_date = publication_date
        news.source_url = source_url
        news.content = self.convert_to_html(json_data['content'])
        news.save()

    # TODO normal name
    def get_links_for_non_exist_data_in_db(self, list_links):
        new_list_links = []
        for link in list_links:
            try:
                news = News.objects.get(source_url=link)
            except ObjectDoesNotExist:
                new_list_links.append(link)
        return new_list_links

    def convert_to_html(self, json_data):
        """
         Convert json to html doc and add own css styles
        """
        content = ""
        header_tags = ['h1', 'h2', 'h3', 'h4', 'h5']
        for block in json_data:
            for key, item in block.items():
                if key in header_tags:
                    style = 'news-header'
                    content += '<%s class="%s">%s</%s>' % (key, style, item, key)

                elif key == 'text':
                    style = 'news-text'
                    content += '<div class="%s">%s</div>' % (style, item)

                elif key == 'list':
                    style = 'news-list'
                    list_items = ""
                    for list_item in item:
                        list_items += '<li>%s</li>' % (list_item)
                    content += '<ul class="%s">%s</ul>' % (style, list_items)

                elif key == 'image':
                    style = 'news-image'
                    content += '<img class="%s" src="%s" title="%s">' % (style, item['source'], item['title'])

                elif key == 'quote':
                    style = 'news-quote'
                    content += '<q class="%s">%s</q>' % (style, item)

                elif key == 'table':
                    style = 'news-table'
                    head = item['head']
                    body = item['body']

                    head_data = ''
                    for row in head:
                        if type(row) != list:
                            column_data = '<td>%s</td>' % row
                            head_data += column_data
                        else:
                            row_data = ''
                            for column in row:
                                row_data += '<td>%s</td>' % column
                            head_data += '<tr>%s</tr>' % row_data

                    body_data = ''
                    for row in body:
                        if type(row) != list:
                            column_data = '<td>%s</td>' % row
                            body_data += column_data
                        else:
                            row_data = ''
                            for column in row:
                                row_data += '<td>%s</td>' % column
                            body_data += '<tr>%s</tr>' % row_data

                    content += '<table class="%s">' \
                                   '<thead>%s</thead>' \
                                   '<tbody>%s</tbody>' \
                               '</table>' % (style, head_data, body_data)

        return content