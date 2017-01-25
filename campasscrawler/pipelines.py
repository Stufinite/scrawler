# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy_djangoitem import DjangoItem
from campasscrawler.items import CampasscrawlerItem
from timetable.models import Course

class CampasscrawlerPipeline(object):

    def process_item(self, item, spider):
        CampasscrawlerItem.django_model.objects.bulk_create(item['array'])
