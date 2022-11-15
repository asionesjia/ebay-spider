import random

import scrapy

from spider_apps.items import EbayCategoryItem


class EbayCategorySpider(scrapy.Spider):
    name = 'ebay_category'
    allowed_domains = ['ebay.com']
    custom_settings = {
        'ITEM_PIPELINES': {'spider_apps.pipelines.EbayCategoryLinkPipeline': 300},
    }

    next_round_links = []

    def start_requests(self):
        print('Starting!')
        yield scrapy.Request(
            url='https://www.ebay.com/n/all-categories/',
            callback=self.start_request_process
        )

    def start_request_process(self, response):
        links: list = response.xpath(
            '//*[@id="wrapper"]/div[1]/div/div/div[2]/div[2]/div/div/div/div/ul/li/a/@href').extract()
        random.shuffle(links)
        for j, i in enumerate(links):
            yield scrapy.Request(
                url=f'{i}?_pgn=2',
                callback=self.handle_category_link,
                meta={
                    "last_item": j == len(links) - 1
                }
            )

    def handle_category_link(self, response):
        print(response.meta.get("last_item"))
        if response.meta.get("last_item"):
            this_round_links = self.next_round_links[:]
            self.next_round_links.clear()
            for j, i in enumerate(this_round_links):
                yield scrapy.Request(
                    url=f'{i}?_pgn=2',
                    callback=self.handle_category_link,
                    meta={
                        "last_item": j == len(this_round_links) - 1
                    }
                )
        for i in range(3):
            flip_page_element = response.css(f'#s0-28_1-9-0-1\[{i}\]-0-0 > div.b-pagination')
            if not flip_page_element:
                continue
            kws_list: list = response.xpath('/html/body/div[2]/div[2]/div/nav/ul/li/a/span/text()').extract()
            kws = []
            for kw in kws_list:
                kw = str.strip(kw)
                if kw:
                    kws.append(kw)
            ebay_category_item = EbayCategoryItem()
            ebay_category_item["url"] = response.url.split('?_pgn=2')[0]
            ebay_category_item["kws"] = kws
            yield ebay_category_item
            break
        category_links_1 = response.xpath('//*[@id="leftnav"]/div/div/div/section/ul/li/ul/li/a/@href').extract()
        category_links_2 = response.xpath('//*[@id="leftnav"]/div/div/div/section/ul/li/a/@href').extract()
        if category_links_1:
            for i in category_links_1:
                self.next_round_links.append(i)
        if category_links_2:
            for i in category_links_2:
                self.next_round_links.append(i)
