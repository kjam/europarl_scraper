# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from europarl_scraper.items import EuroparlText
import re
import requests


def get_start_urls():
    """ populate start urls with full search json """
    resp = requests.post(
        'http://www.europarl.europa.eu/meps/en/json/newperformsearchjson.html')
    speaker_urls = ['http://www.europarl.europa.eu{}'.format(r.get('detailUrl'))
                    for r in resp.json().get('result')]
    all_speeches = []
    # want to merely test with a smaller set? uncomment below and comment out
    # matching line in for loop. It will give you only 90 speeches :)
    next_page, index = True, 0
    for speaker in speaker_urls:
        # next_page, index = True, 0
        url_split = speaker.split('/')[:-1]
        url_split.append('see_more.html')
        base_url = '/'.join(url_split)
        while next_page:
            resp = requests.get(base_url,
                                params={'type': 'CRE', 'index': index})
            if resp.json().get('nextIndex') == -1:
                next_page = False
            else:
                index = resp.json().get('nextIndex')
            all_speeches.extend([s.get('titleUrl')
                                 for s in resp.json().get('documentList')])
    return all_speeches


class EuroParlSpeechSpider(Spider):
    """ crawl spider for european parliament speakers """
    name = "europarl_speeches"
    allowed_domains = ["europarl.europa.eu"]
    start_urls = get_start_urls()
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
        return item

    def parse(self, response):
        """ parse a speaker page and extract items """
        self.response = response
        item = EuroparlText()
        item['text_url'] = response.url
        speaker_photo = self.grab_xpath('//td/img[@alt="MPphoto"]/@src')
        item['speaker_id'] = re.search(r'[\d]+', speaker_photo).group()
        speaker_info = self.grab_xpath(
            '//p/span[@class="doc_subtitle_level1_bis"]/text()')
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
            '//p[@class="contents"]/span[@class="italic"]/text()')
        if item['pol_group'] == 'n/a' and re.search('[A-Z]+', item['note']):
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
