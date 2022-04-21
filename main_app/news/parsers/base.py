import requests
from time import sleep

class BaseParser():
    url_page_with_list_articles = None
    headers = None

    def __init__(self, headers):
        self.headers = headers

    def parse_list_pages(self):
        html_list = self._get_page(self.url_page_with_list_articles)
        # parse recent
        json_data = {}
        links_to_articles = self._parse_list_pages(html_list)
        for links in links_to_articles:
            json_page_data = self.parse_page(links)
            json_data[links] = json_page_data
        return json_data

    def parse_page(self, url):
        html_data = self._get_page(url)
        json_data = self._parse_page(html_data)
        return json_data

    def _parse_list_pages(self, html_data):
        raise NotImplementedError('Subclasses must implement this method')

    def _parse_page(self, html_data):
        raise NotImplementedError('Subclasses must implement this method')

    def _get_page(self, url, retry=5):
        try:
            response = requests.get(url, headers=self.headers)
        except Exception as ex:
            if retry:
                sleep(5)
                print(f"Retry №{retry}=>{url}")
                self._get_page(url, retry=retry - 1)
        else:
            return response.text

    def get_text_from_children(self, parent):
        text = ""
        for string in parent.strings:
            text += string
        return text