import json

from django.core.management.base import BaseCommand, CommandError
from django.db.models import ObjectDoesNotExist

from main_app.settings import HEADERS
from news.parsers.RIA_parser import RIA_Parser
from news.models import News

import dateparser


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

        news_parser = RIA_Parser(headers=HEADERS, verbosity='debug', timeout=5, pause_between_requests=0.5)

        while True:
            self.parse_to_database(news_parser)
            break
            # parse data from all sites
            # sleep(options['pause']*60)


    def parse_to_database(self, news_parser):
        """
         For a given site (which is represented by a separate parser class)
         collects all articles and saves them to the model.
        """
        # get links on all articles
        list_links = news_parser.collect_list_urls(parse_for_days=self.parse_for_days)
        # parse only not stored data
        list_links = self.remove_stored_links(list_links)
        # parse pages
        json_data = news_parser.parse(list_links)

        for key, item in json_data.items():
            self.save_to_model(item, key)

    def save_to_model(self, json_data, source_url):
        """ Save given json data to News model. """
        news = News()
        news.title = json_data['title']
        news.publication_date = self.convert_to_datetime(json_data['publication_date'])
        news.source_url = source_url
        news.content = self.convert_to_html(json_data['content'])
        news.save()

    def remove_stored_links(self, list_links):
        """
         For a given a list of article links, checks if these articles are stored in the database.
         Returns links to articles that are not yet stored in the database
        """
        new_list_links = []
        for link in list_links:
            try:
                news = News.objects.get(source_url=link)
            except ObjectDoesNotExist:
                new_list_links.append(link)
        return new_list_links

    def convert_to_html(self, json_data):
        """
         Convert json data to html and adds own css styles
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
                    content += '<blockquote class="%s">%s</blockquote>' % (style, item)

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

    def convert_to_datetime(self, json_data):
        date_string = str(json_data['year']) + '-' + str(json_data['month']) + '-' + str(json_data['day']) \
                      + ' ' +  str(json_data['hour']) + ':' + str(json_data['minute'])
        publication_date = dateparser.parse(date_string, date_formats=['%Y %m %d %H %M'])
        return publication_date
