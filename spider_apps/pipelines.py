import gspread
from spider_apps.database import MongoDB


class EbayCategoryLinkPipeline:
    def __init__(self):
        self.db = MongoDB().ebay_category_db()

    def process_item(self, item, spider):
        self.db.insert_one(
            {
                "url": item.get('url'),
                "kws": item.get('kws')
            }
        )
        return item


class EbayUserInfoPipeline:
    def __init__(self):
        self.db = MongoDB().ebay_user_info_db()
        sa = gspread.service_account(filename="./.config/gspread/service_account.json")
        sh = sa.open("registration")
        self.wks = sh.worksheet("ebayscrap")

    def open_spider(self, spider):
        if not self.wks.get_all_values():
            self.wks.append_row(["username",
                                 "user_link",
                                 "is_store",
                                 "store_name",
                                 "stars_num",
                                 "user_location",
                                 "listing_num",
                                 "listing_category"])

    def process_item(self, item, spider):
        data = {
            "username": item.get('username'),
            "user_link": item.get('user_link'),
            "is_store": item.get('is_store'),
            "store_name": item.get('store_name'),
            "stars_num": item.get('stars_num'),
            "user_location": item.get('user_location'),
            "listing_num": item.get('listing_num'),
            "listing_category": item.get('listing_category'),
        }
        if item.get('stars_num') < 300:
            if item.get('listing_num') > 10 or item.get('is_store'):
                row = []
                for i in data:
                    if i == "listing_category":
                        listing_category_str = ''
                        for c in data[i]:
                            if not listing_category_str:
                                listing_category_str = c
                            else:
                                listing_category_str = f'{listing_category_str}, {c}'
                        row.append(listing_category_str)
                        continue
                    row.append(data[i])
                self.wks.append_row(row)
        self.db.insert_one(data)

        return item
