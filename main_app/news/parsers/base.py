import requests
from time import time
from datetime import datetime

import bs4
import asyncio
import aiohttp


# https://github.com/aio-libs/aiohttp/issues/6635
from functools import wraps
from asyncio.proactor_events import _ProactorBasePipeTransport


def silence_event_loop_closed(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except RuntimeError as e:
            if str(e) != 'Event loop is closed':
                raise
    return wrapper

_ProactorBasePipeTransport.__del__ = silence_event_loop_closed(_ProactorBasePipeTransport.__del__)


class BaseParser():
    url_page_with_list_articles = None
    headers = None
    logging_file = None
    _list_pages = None

    def __init__(self, headers, logging_file):
        self.headers = headers
        self.logging_file = logging_file

    async def _parse_list_pages(self, list_urls):
        async with aiohttp.ClientSession(headers=self.headers) as session:
            json_page_data_list = await asyncio.gather(*[self._parse_page(links, session)
                                                         for links in list_urls])

        json_data = {}
        for (links, json_page_data) in zip(list_urls, json_page_data_list):
            json_data[links] = json_page_data
        self._list_pages = json_data

    async def _parse_page(self, url, session):
        html_data = await self._get_page(url, session)
        json_data = self._process_parse_page(html_data)
        return json_data

    def get_json_list_pages(self, list_urls):
        if not self._list_pages:
            asyncio.run(self._parse_list_pages(list_urls))
        return self._list_pages

    def get_list_urls_pages(self):
        html_data = requests.get(self.url_page_with_list_articles, headers=self.headers).text
        links_to_articles = self._process_parse_list_pages(html_data)
        return links_to_articles

    def _process_parse_list_pages(self, html_data):
        raise NotImplementedError('Subclasses must implement this method')

    def _process_parse_page(self, html_data):
        raise NotImplementedError('Subclasses must implement this method')

    async def _get_page(self, url, session, retry=5):
        try:
            # don't work with ssl=True
            async with session.get(url=url, headers=self.headers, ssl=False) as response:
                response_text = await response.text()
        except Exception as ex:
            if retry:
                await asyncio.sleep(5)
                print(f"Retry №{retry}=>{url}")
                await self._get_page(url, session, retry=retry - 1)
        else:
            return response_text

    def add_logs(self, message, **extrainfo):
        with open(self.logging_file, 'a') as logs:
            logs.write(f'[{datetime.now()}] {message} {extrainfo}\n')