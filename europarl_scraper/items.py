""" European parliament scrapy item models """
# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class EuroparlMember(scrapy.Item):
    """ Data points for each member of EP """
    first_name = scrapy.Field()
    last_name = scrapy.Field()
    speaker_id = scrapy.Field()
    speaker_url = scrapy.Field()
    dob = scrapy.Field()
    nationality = scrapy.Field()
    curr_pol_group = scrapy.Field()
    curr_pol_group_abbr = scrapy.Field()
    all_pol_groups = scrapy.Field()
    natl_pol_groups = scrapy.Field()
    chair_positions = scrapy.Field()
    email = scrapy.Field()
    website = scrapy.Field()
    twitter = scrapy.Field()
    facebook = scrapy.Field()
    num_reports = scrapy.Field()
    num_opinions = scrapy.Field()
    num_motions = scrapy.Field()
    num_declarations = scrapy.Field()
    num_questions = scrapy.Field()
    speeches_url = scrapy.Field()


class EuroparlText(scrapy.Item):
    """ Data points for each speech from EP website """
    speaker_id = scrapy.Field()
    text_url = scrapy.Field()
    pol_group = scrapy.Field()
    topic = scrapy.Field()
    topic_links = scrapy.Field()
    note = scrapy.Field()
    text = scrapy.Field()
    language = scrapy.Field()
    speech_type = scrapy.Field()
    speech_date = scrapy.Field()
    speech_location = scrapy.Field()


class EuroparlDebate(scrapy.Item):
    """ Data points for each debate from EP website """
    text_url = scrapy.Field()
    speaker_id = scrapy.Field()
    order = scrapy.Field()
    pol_group = scrapy.Field()
    topic = scrapy.Field()
    topic_links = scrapy.Field()
    note = scrapy.Field()
    text = scrapy.Field()
    speech_type = scrapy.Field()
    speech_date = scrapy.Field()
    speech_location = scrapy.Field()
