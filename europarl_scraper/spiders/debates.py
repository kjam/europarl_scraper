# -*- coding: utf-8 -*-
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from europarl_scraper.items import EuroparlDebate
import re
import requests


def get_start_urls():
    """ populate start urls with full search json """
    resp = requests.post(
        'http://www.europarl.europa.eu/meps/en/json/newperformsearchjson.html')
    return ['http://www.europarl.europa.eu{}'.format(r.get('detailUrl'))
            for r in resp.json().get('result')]


def get_initial_list():
    """ populate initial list used for xtra data with full search json """
    resp = requests.post(
        'http://www.europarl.europa.eu/meps/en/json/newperformsearchjson.html')
    return resp.json().get('result')


class EuroParlSpeakerSpider(CrawlSpider):
    """ crawl spider for european parliament speakers """
    name = "europarl_speaker"
    allowed_domains = ["europarl.europa.eu"]
    start_urls = get_start_urls()
    response = None
    initial_list = get_initial_list()

    rules = (
        Rule(
            LinkExtractor(
                allow=r'/meps/en/[\d]+/[A-Z_]+_home.html'
            ),
            follow=True,
        ),
        Rule(
            LinkExtractor(
                allow=[r'/meps/en/[\d]+/seeall.html?type=[A-Z]+',
                       r'/sides/getDoc.do?pubRef=-//EP//[\w\d_\-\\\/]+', ],
            ),
            follow=True,
        ),
    )
    more_rules = """Rule(
            LinkExtractor(
                allow=''
            ),
            follow=True,
            callback='parse_speeches',),
        Rule(
            LinkExtractor(
                allow=''
            ),
            follow=True,
            callback='parse_debate',),
        """

    def remove_returns(self, my_string):
        """ remove returns from strings """
        return my_string.replace('\n', '').replace(
            '\t', '').replace('\r', '').strip()

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

    def parse_debate(self, response):
        """ parse a speaker page and extract items """
        self.response = response
        item = EuroparlDebate()
        item['text_url'] = response.url
        return item
