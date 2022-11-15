from pymongo import MongoClient

CONNECTION_STRING = "mongodb+srv://ebayscrap:wQZYHguqgKlm0uwc@cluster0.ba9xwbw.mongodb.net/"
mongodb = MongoClient(CONNECTION_STRING)['e-commerce_platforms_crawler']
ebay_category_db = mongodb["ebay_category"]
ebay_user_info_db = mongodb["ebay_user_info"]


class MongoDB:

    def ebay_category_db(self):
        return ebay_category_db

    def ebay_user_info_db(self):
        return ebay_user_info_db
