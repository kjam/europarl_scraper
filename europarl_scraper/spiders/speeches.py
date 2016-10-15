# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from europarl_scraper.items import EuroparlText
import re
import requests
import pandas as pd
import os

DATA_DIR = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..', 'data'))

class EuroParlSpeechSpider(Spider):
    """ crawl spider for european parliament speakers """
    name = "europarl_speeches"
    allowed_domains = ["europarl.europa.eu"]
    start_urls = pd.read_csv(
        os.path.join(DATA_DIR, 'speech_urls.csv')).url.values
    response = None

    def remove_returns(self, my_string):
        """ remove returns from strings """
        return my_string.replace('\n', '').replace(
            '\t', '').replace('\r', '').replace('\xa0', '').strip()

    def grab_xpath(self, xpath_str, pick_one=False, digit=False,
                   return_str=False):
        """ Some intelligence around how to grab from an xpath. """
        item = self.response.xpath(xpath_str).extract()
        if isinstance(item, list):
            item = [self.remove_returns(i) for i in item
                    if self.remove_returns(i)]
            if len(item) == 1 or pick_one:
                item = item[0]
        if isinstance(item, str):
            item = self.remove_returns(item)
            if item.isdigit() and digit:
                item = float(item)
        if return_str and item == []:
            return ''
        elif return_str and isinstance(item, list):
            return ';'.join(item)
        return item

    def parse(self, response):
        """ parse a speaker page and extract items """
        self.response = response
        item = EuroparlText()
        item['text_url'] = response.url
        speaker_photo = self.grab_xpath('//td/img[@alt="MPphoto"]/@src')
        try:
            item['speaker_id'] = re.search(r'[\d]+', speaker_photo).group()
        except AttributeError:
            item['speaker_id'] = 'n/a'
        speaker_info = self.grab_xpath(
            '//p/span[@class="doc_subtitle_level1_bis"]/text()', return_str=True)
        try:
            item['pol_group'] = re.search(
                r'\(\w+\)', speaker_info).group().lstrip('(').rstrip(')')
        except AttributeError:
            item['pol_group'] = 'n/a'
        item['topic'] = ''.join(
            self.grab_xpath('//td[@class="doc_title"]/text()|' +
                            '//td[@class="doc_title"]/a/text()')[2:])
        item['topic_links'] = self.grab_xpath(
            '//td[@class="doc_title"]/a/@href')
        item['note'] = self.grab_xpath(
            '//p[@class="contents"]/span[@class="italic"]/text()', return_str=True)
        if item['pol_group'] == 'n/a' and re.search(r'[A-Z]+', item['note']):
            # sometimes the party is instead in the note
            item['pol_group'] = re.search('[A-Z]+', item['note']).group()
        item['text'] = self.grab_xpath('//p[@class="contents"]/text()')
        item['language'] = self.grab_xpath(
            '//ul[@class="language_select"]/li[contains(@class, "selected")]/@title')
        item['speech_type'] = self.grab_xpath('//td[@class="title_TA"]/text()')
        date_and_location = self.grab_xpath(
            '//td[@class="doc_title"]/text()')[0]
        item['speech_date'] = date_and_location.split('-')[0]
        item['speech_location'] = date_and_location.split('-')[1]
        return item
