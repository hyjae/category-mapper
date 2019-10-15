import os
import json
import logging
from config import ConfigManager
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from elasticsearch.client import IndicesClient

logging.basicConfig(filename='setup.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)


def es_connect():
    """Open up a ElasticSearch connector

    :return: ElasticSearch connector instance
    """
    es_config = ConfigManager().get_setting(key='elasticsearch')
    addresses = es_config['address']
    if not isinstance(addresses, list):
        addresses = [addresses]
    return Elasticsearch(addresses, port=es_config['port'])


def create_index(file_path, index_name):
    """Indexing a json file given

    :param file_path: json file to be indexed
    :param index_name:
    :return:
    """
    if not file_path.endswith('json'):
        logger.error('The file must be a json format: %s' % file_path)
        exit(1)

    index_es = IndicesClient(es_connect())

    if index_es.exists(index=index_name):
        index_es.delete(index_name)
        logger.debug('The existing %s has been removed!' % index_name)

    with open(file_path, encoding='utf-8') as f:
        mapping_settings = json.loads(f.read())
        index_es.create(index=index_name, body=mapping_settings)
        logger.debug('%s has been successfully registered!' % index_name)


def index_json(file_path, index_name, doc_type):
    """Indexing json file given

    :param file_path: json file path
    :param index_name: index name
    :param doc_type: ElasticSearch doc_type
    :return: None
    """
    if not file_path.endswith('json'):
        logger.error('The file must be a json format: %s' % file_path)
        exit(1)

    es = es_connect()

    with open(file_path, encoding='utf-8') as f:
        index_data = json.loads(f.read())
        helpers.bulk(es, index_data, index=index_name, doc_type=doc_type)
        logger.debug('%s has been successfully registered!' % index_name)


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    try:
        print('start')
        dir_path = os.path.join(os.path.dirname(__file__), 'files')
        create_index(os.path.join(dir_path, 'index_settings.json'), 'intg_category')
        index_json(os.path.join(dir_path, 'intg_category.json'), 'intg_category', 'categories')
        print('end')
    except (KeyboardInterrupt, SystemExit):
        logger.info('Interrupt Signal Received')
        exit(1)
    except Exception as e:
        logger.error('Unknown Exception! %s' % e)
