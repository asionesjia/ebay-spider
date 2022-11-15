import re

import scrapy
from scrapy.linkextractors import LinkExtractor

from spider_apps.database import MongoDB
from spider_apps.items import EbayUserInfoItem


class EbayShopSpider(scrapy.Spider):
    name = 'ebay_shop'
    allowed_domains = ['ebay.com']
    custom_settings = {
        'ITEM_PIPELINES': {'spider_apps.pipelines.EbayUserInfoPipeline': 300},
    }

    def get_category_links(self):
        mongodb = MongoDB().ebay_category_db()
        return list(mongodb.find({}))

    def start_requests(self):
        category_link_items = self.get_category_links()
        for category_link_item in category_link_items:
            sops = [1, 7, 10, 12, 15, 16]
            for fcid in range(225):
                for sop in sops:
                    yield scrapy.Request(
                        url=f'{category_link_item["url"]}?listingOnly=1&rt=nc&_fcid={fcid}&_pgn=2&_sop={sop}',
                        callback=self.parse_shop_items_page,
                        meta={
                            "main_url": category_link_item["url"],
                            "fcid": fcid,
                            "pgn": 2,
                            "sop": sop
                        }
                    )

    def parse_shop_items_page(self, response):
        next_url = response.xpath('//*[@id="s0-28_1-9-0-1[0]-0-0"]/div[2]/nav/a[2]/@href').extract_first()
        if next_url:
            if next_url != '#':
                yield scrapy.Request(
                    url=f'{response.meta.get("main_url")}?listingOnly=1&rt=nc&_fcid={response.meta.get("fcid")}&_pgn={response.meta.get("pgn") + 1}&_sop={response.meta.get("sop")}', 
                    callback=self.parse_shop_items_page,
                    meta={
                        "main_url": response.meta.get("main_url"),
                        "fcid": response.meta.get("fcid"),
                        "pgn": response.meta.get("pgn") + 1,
                        "sop": response.meta.get("sop")
                    }
                )
        le = LinkExtractor(
            allow='https://www.ebay.com/itm/.*?'
        )
        shop_items_links = le.extract_links(response)
        for shop_item_link in shop_items_links:
            yield scrapy.Request(
                url=shop_item_link.url,
                callback=self.parse_shop_item_details_page
            )

    def parse_shop_item_details_page(self, response):
        pattern = 'https://www.ebay.com/usr/(.*?)\?_trksid'
        re_findall_username = re.findall(pattern, response.body.decode(response.encoding))
        if not re_findall_username:
            re_findall_username = response.xpath(
                '//*[@id="RightSummaryPanel"]/div[3]/div[1]/div/div[2]/ul/li[1]/div/a[1]/span/text()').extract()
        if re_findall_username:
            ebay_username = re_findall_username[0]
            ebay_user_link = f'https://www.ebay.com/sch/{ebay_username}/m.html'
            yield scrapy.Request(
                url=ebay_user_link,
                callback=self.parse_user_details,
                meta={
                    "username": ebay_username
                }
            )
        else:
            print(f'!!!!!!!!---没有匹配到username---referer: {response.request.url}')

    def parse_user_details(self, response):
        if not response.xpath('//*[@id="MessageContainer"]/div').extract():
            ebay_user_info_item = EbayUserInfoItem()
            ebay_user_info_item["username"] = response.meta.get('username')
            ebay_user_info_item["user_link"] = f'https://www.ebay.com/usr/{response.meta.get("username")}'
            pattern = '"http://stores.ebay.com/(.*?)"'
            re_findall = re.findall(pattern, response.body.decode(response.encoding))
            is_store = False
            store_name = ''
            if re_findall:
                is_store = True
                store_name = re_findall[0]
            ebay_user_info_item["is_store"] = is_store
            ebay_user_info_item["store_name"] = store_name
            ebay_user_info_item["stars_num"] = int(response.xpath(
                '//*[@id="soiBanner"]/div/span[2]/a/text()').extract_first())
            location = response.xpath(
                '//*[@id="LeftPanelInner"]/div[2]/div/div/div/div/div[4]/text()').extract_first().strip()
            if not location:
                location = response.xpath(
                    '//*[@id="LeftPanelInner"]/div[2]/div/div/div/div/div[3]/text()').extract_first().strip()
            ebay_user_info_item["user_location"] = location.split('in')[-1].strip()
            ebay_user_info_item["listing_num"] = int(response.xpath(
                '//*[@id="cbelm"]/div[3]/span[1]/text()').extract_first().replace(',', '').replace(' ', ''))
            listing_category = []
            listing_category2 = response.xpath(
                '//*[@id="e1-12"]/div[2]/div/div/div/div/a/text()').extract()
            listing_category1 = response.xpath(
                '//*[@id="e1-12"]/div[2]/div/div/a/text()').extract()
            listing_category4 = response.xpath(
                '//*[@id="e1-13"]/div[2]/div/div/div/div/a/text()').extract()
            listing_category3 = response.xpath(
                '//*[@id="e1-13"]/div[2]/div/div/a/text()').extract()
            if listing_category1:
                for i in listing_category1:
                    listing_category.append(i)
            if listing_category2:
                for i in listing_category2:
                    listing_category.append(i)
            if listing_category3:
                for i in listing_category3:
                    listing_category.append(i)
            if listing_category4:
                for i in listing_category4:
                    listing_category.append(i)
            ebay_user_info_item["listing_category"] = listing_category
            yield ebay_user_info_item
        else:
            print(response.xpath('//*[@id="MessageContainer"]/div').extract())
