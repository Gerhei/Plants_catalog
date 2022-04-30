import requests
from time import sleep
from datetime import datetime

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
    site = None
    url_list_articles = None
    headers = None
    logging_file = None
    _json_list_pages = None

    def __init__(self, headers, logging_file=None):
        self.headers = headers
        self.logging_file = logging_file

    async def _parse_list_pages(self, list_urls):
        """
         For a given list of urls, return parsed data for each of the pages
        """
        async with aiohttp.ClientSession(headers=self.headers) as session:
            json_page_data_list = await asyncio.gather(*[self._parse_page(links, session)
                                                         for links in list_urls])

        json_data = {}
        for (links, json_page_data) in zip(list_urls, json_page_data_list):
            json_data[links] = json_page_data
        self._json_list_pages = json_data

    async def _parse_page(self, url, session):
        html_data = await self._get_page(url, session)
        json_data = self.process_parse_page(html_data, source_url=url)
        return json_data

    def parse(self, list_urls):
        """
         For a given urls returns parsed data in format: {url: page_content}
        """
        asyncio.run(self._parse_list_pages(list_urls))
        return self._json_list_pages

    def get_list_urls(self, parse_for_days=-1):
        """
         Finds all links to articles on site and returns them.
         parse_for_days means parses data for a certain number of days
         parse_for_days<0 means parse all data form site
         parse_for_days=0 means to parse the data for the current day
        """
        raise NotImplementedError('Subclasses must implement this method')

    def process_parse_list_articles(self, html_data):
        """
         For a given html page, finds all links to articles in it and returns a list of urls
        """
        raise NotImplementedError('Subclasses must implement this method')

    def process_parse_page(self, html_data, source_url=None):
        """
         For a given html page return parsed data in json.
         Source urls optional and needs only for logging.
        """
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
                # FIXME it is work?
                await self._get_page(url, session, retry=retry - 1)
        else:
            return response_text

    # Sync version _get_page for outer use
    def get_page(self, url, retry=5):
        """
         Make a request by applying all the request parameters specified in the class (headers for example)
        """
        try:
            response = requests.get(url, headers=self.headers)
        except Exception as ex:
            if retry:
                sleep(5)
                print(f"Retry №{retry}=>{url}")
                # FIXME it is work?
                self.get_page(url, retry=retry - 1)
        else:
            return response.text

    def add_logs(self, message, **extrainfo):
        if not self.logging_file:
            return
        with open(self.logging_file, 'a') as logs:
            logs.write(f'[{datetime.now()}] {message} {extrainfo}\n')