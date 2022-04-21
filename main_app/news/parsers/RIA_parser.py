from bs4 import BeautifulSoup

from news.parsers.base import BaseParser

class RIA_Parser(BaseParser):
    url_page_with_list_articles = 'https://ria.ru/tag_rastenija/'

    def _parse_list_pages(self, html_data):
        soup = BeautifulSoup(html_data, 'lxml')
        links_to_articles = []

        return links_to_articles

    def _parse_page(self, html_data):
        soup = BeautifulSoup(html_data, 'lxml')
        json_data = {}
        article_header = soup.find('div', {'class': 'article__header'})
        article_body = soup.find('div', {'class': 'article__body'})

        i = 0
        ignored_types = ['article', 'banner']
        header_tags = ['h1', 'h2', 'h3', 'h4', 'h5']
        for block in article_body.find_all('div', {'class': 'article__block'}):
            data_type = block['data-type']
            content = []
            if data_type in ignored_types:
                # skip banner ads and links on other articles
                continue

            elif data_type in header_tags:
                header_content = self.get_text_from_children(block)
                content.append(header_content)

            elif data_type == 'text':
                text_content = ""
                for child in block.children:
                    if child.name == 'strong':
                            content.append(child.string)


                    for string in child.strings:
                        text_content += string
                    content.append(text_content)

            elif data_type == 'list':
                list_items = block.find_all('li')
                for item in list_items:
                    item_text = ""
                    for item_data in item.children:
                        if item_data.name == 'div':
                            # skip list label
                            if 'article__list-label' in item_data.attrs['class']:
                                continue
                        for string in item_data.strings:
                            item_text += string
                    
                    content.append(item_text)

            elif data_type == 'media':
                # add specific logic
                pass

            else:
                # something strange
                pass

            json_data[i] = {data_type: content}
            i +=1
        return json_data