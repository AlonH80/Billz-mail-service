from variables import *
import pymongo


class MongoConnector:
    mongo_client = None

    def __init__(self, col):
        if MongoConnector.mongo_client is None:
            self.init_mongo()
        self.col = col

    @staticmethod
    def init_mongo():
        if MongoConnector.mongo_client is None:
            MongoConnector.mongo_client = pymongo.MongoClient(MONGO_ADDRESS)[APP_DATABASE]

    def find(self, find_map):
        res = MongoConnector.mongo_client[self.col].find(find_map)
        return list(res)

    def insert(self, list_map):
        res = MongoConnector.mongo_client[self.col].insert_many(list_map)
        return res

    def update(self, query: dict, new_values: dict):
        new_values_adapt = {"$set": new_values}
        res = MongoConnector.mongo_client[self.col].update_one(query, new_values_adapt)
        return res


mongo_obj = MongoConnector("pdfTest")
pdf_test_map = mongo_obj.find({})
print(pdf_test_map)
# insert("pdfTest", [{"type": "arnona", "amount": 50}])
# insert("pdfTest", [{"type": "water", "amount": 50}, {"type": "electricity", "amount": 100}])
#update("pdfTest", {"type": "electricity"}, {"amount": 120})
