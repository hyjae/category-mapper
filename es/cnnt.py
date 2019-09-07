from config import ConfigManager
from elasticsearch import Elasticsearch
from elasticsearch import helpers

class ESConnector:

    @classmethod
    def from_config(cls):
        config = ConfigManager()
        db_settings = config.get_setting('es')
        cls.es = Elasticsearch([
            '192.168.210.149'
        ], port=9200)
        return cls

import json
cnnt = ESConnector.from_config()
with open('C:\\Developer\\yjhnnn\\cat-mapper\\files\\category.json', 'r', encoding='utf-8') as t:
    data = json.load(t)
helpers.bulk(cnnt.es, data)

