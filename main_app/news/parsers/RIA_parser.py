import re

from bs4 import BeautifulSoup

from news.parsers.base import BaseParser

class RIA_Parser(BaseParser):
    url_page_with_list_articles = 'https://ria.ru/tag_rastenija/'

    def _process_parse_list_pages(self, html_data):
        soup = BeautifulSoup(html_data, 'lxml')
        links_to_articles = []
        for article in soup.find('div', {'class': 'list'}).find_all('div', {'class': 'list-item'}):
            links_to_articles.append(article.find('a', {'class': 'list-item__title'}).attrs['href'])
        return links_to_articles

    def _process_parse_page(self, html_data):
        soup = BeautifulSoup(html_data, 'lxml')
        json_data = {'content': []}
        article_header = soup.find('div', {'class': 'article__header'})
        article_body = soup.find('div', {'class': 'article__body'})

        announce = article_header.find('div', {'class': 'article__announce'})
        # Skip news with podcast
        if announce.find('div', {'class': 'audioplayer'}):
            return None

        announce_image = announce.find('img')
        if announce_image:
            announce_image = {'image':
                                  {'source': announce_image.attrs['src'],
                                   'title': announce_image.attrs['title']}}
            json_data['content'].append(announce_image)

        publication_date = article_header.find('div', {'class': 'article__info-date'}).find('a')
        publication_date = publication_date.get_text()
        json_data['publication_date'] = publication_date

        title = article_header.find(re.compile("\w"), {'class': 'article__title'})
        title = title.get_text()
        json_data['title'] = title

        ignored_types = ['article', 'banner']
        header_tags = ['h1', 'h2', 'h3', 'h4', 'h5']
        for block in article_body.find_all('div', {'class': 'article__block'}):
            data_type = block['data-type']
            content = None
            if data_type in ignored_types:
                # skip banner ads and links on other articles
                continue

            elif data_type in header_tags:
                header_content = block.get_text()
                content = header_content

            elif data_type == 'text':
                text_content = block.get_text()#
                content = text_content

            elif data_type == 'list':
                content = []
                list_items = block.find_all('li')
                for item in list_items:
                    item_text = ""
                    for item_data in item.children:
                        if item_data.name == 'div':
                            # skip list label
                            if 'article__list-label' in item_data.attrs['class']:
                                continue
                        item_text += item_data.get_text()
                    content.append(item_text)

            elif data_type == 'media':
                # processing only images
                image = block.find('img')
                if not image:
                    continue
                data_type = 'image'
                content = {'source': image.attrs['src'], 'title': image.attrs['title']}

            elif data_type == 'quote':
                content = block.get_text()

            elif data_type == 'table':
                head = block.find('table').find('thead')
                table_body = block.find('table').find_all('tr')
                content = {'head': [], 'body': []}

                for row in head.find_all('tr'):
                    for column in row.find_all('td'):
                        content['head'].append(column.get_text())

                for row in table_body:
                    table_row = []
                    for column in row.find_all('td'):
                        table_row.append(column.get_text())
                    if table_row == content['head']:
                        continue
                    content['body'].append(table_row)

            elif data_type == 'infographics':
                image = block.find('img')
                if not image:
                    continue
                data_type = 'image'
                content = {'source': image.attrs['src'], 'title': image.attrs['title']}

            else:
                # logging something strange
                self.add_logs('Unknown data type', data_type=data_type, title=json_data['title'])
                continue

            json_data['content'].append({data_type: content})
        return json_data