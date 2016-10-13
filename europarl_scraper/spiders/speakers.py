# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from europarl_scraper.items import EuroparlMember, EuroparlText
from lxml import html
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
            callback='parse_speaker',),
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

    def parse_speaker(self, response):
        """ parse a speaker page and extract items """
        self.response = response
        item = EuroparlMember()
        item['speaker_url'] = response.url
        name = self.grab_xpath('//li[@class="mep_name"]/a/text()')
        first_name, last_name = [], []
        for token in name:
            if token.isupper():
                last_name.append(token)
            else:
                first_name.append(token)

        item['first_name'] = ' '.join(first_name).rstrip(' ')
        item['last_name'] = ' '.join(last_name).rstrip(' ')
        item['speaker_id'] = re.search(r'\d+', response.url).group()
        item['nationality'] = self.grab_xpath(
            '//li[contains(@class, "nationality")]/text()')
        dob = self.grab_xpath(
            '//span[@class="more_info"]/text()')[-1]
        item['dob'] = dob.lstrip('Date of birth: ').split(',')[0]
        item['curr_pol_group'] = self.grab_xpath(
            '//li[contains(@class, "group")]/text()')
        item['curr_pol_group_abbr'] = self.grab_xpath(
            '//li[contains(@class, "group")]/@class').lstrip('group ')
        item['email'] = self.grab_xpath(
            '//a[@class="link_email"]/@href', return_str=True).lstrip('mailto:')
        item['website'] = self.grab_xpath(
            '//a[@class="link_website"]/@href', return_str=True)
        item['facebook'] = self.grab_xpath(
            '//ul[@class="link_collection_noborder"]/li/a[@class="link_fb"]/@href',
            return_str=True)
        item['twitter'] = self.grab_xpath(
            '//ul[@class="link_collection_noborder"]/li/a[@class="link_twitt"]/@href',
            return_str=True)

        activity_page = requests.get(response.url.replace('home', 'activities'))
        activity_tree = html.fromstring(activity_page.content)
        ns = activity_tree.xpath('//div[h3[@id="section1"]]/p/text()')
        item['num_speeches'] = (lambda x: int(x[0]) if len(x) else 0)(ns)

        nr = activity_tree.xpath('//div[h3[@id="section2"]]/p/text()')
        nr.extend(activity_tree.xpath('//div[h3[@id="section3"]]/p/text()'))

        item['num_reports'] = sum([int(n) for n in nr if n])

        no = activity_tree.xpath('//div[h3[@id="section4"]]/p/text()')
        no.extend(activity_tree.xpath('//div[h3[@id="section5"]]/p/text()'))

        item['num_opinions'] = sum([int(n) for n in nr if n])

        nm = activity_tree.xpath('//div[h3[@id="section6"]]/p/text()')
        item['num_motions'] = (lambda x: int(x[0]) if len(x) else 0)(nm)

        sect_eight = activity_tree.xpath('//div[h3[@id="section8"]]/p/text()')

        if sect_eight:
            item['num_questions'] = (lambda x: int(x[0]) if len(x) else 0)(
                sect_eight)
            nd = activity_tree.xpath('//div[h3[@id="section7"]]/p/text()')
            item['num_declarations'] = (lambda x:
                                        int(x[0]) if len(x) else 0)(nd)
        else:
            ns = activity_tree.xpath('//div[h3[@id="section7"]]/p/text()')
            item['num_questions'] = (lambda x: int(x[0]) if len(x) else 0)(ns)
            item['num_declarations'] = 0

        history_page = requests.get(response.url.replace('home', 'history'))
        history_tree = html.fromstring(history_page.content)

        apg = history_tree.xpath(
            '//div[h4[contains(text(), "Political Groups")]]/ul/li/text()')
        item['all_pol_groups'] = [ap.strip() for ap in apg]
        npg = history_tree.xpath(
            '//div[h4[contains(text(), "National Parties")]]/ul/li/text()')
        item['natl_pol_groups'] = [np.strip() for np in npg]
        cpg = history_tree.xpath(
            '//div[h4[contains(text(), "Chair")]]/ul/li/text()')
        item['chair_positions'] = [cp.strip() for cp in cpg]

        split_url = response.url.split('/')[:-1]
        split_url.append('seeall.html?type=CRE')
        item['speeches_url'] = '/'.join(split_url)
        return item
