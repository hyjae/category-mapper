import os
import time
from utils import *
from config import ConfigManager
from elasticsearch import Elasticsearch
from sqlalchemy.exc import *
from mysql.object import *
from mysql.connector import MySQLConnector
from sqlalchemy.orm import scoped_session, sessionmaker
from queue import Empty
from multiprocessing import Process, cpu_count, Manager

logpath = os.path.join(os.path.dirname(__name__), 'log')
logfile = os.path.join(logpath, '{}.log'.format(time.strftime('%Y%m%d%H')))
logging.basicConfig(filename=logfile,
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.ERROR)
logger = logging.getLogger('sqlalchemy.engine')
logger.setLevel(logging.ERROR)


def batch_insert(session, org_category, mm_result):

    es_config = ConfigManager().get_setting(key='elasticsearch')

    addresses = es_config['address']
    if not isinstance(addresses, list):
        addresses = [addresses]
    es = Elasticsearch(addresses, port=es_config['port'])

    batch_insert = es.msearch(body=mm_result)['responses']

    if batch_insert:
        try:
            for org_cat, batch_result in zip(org_category, batch_insert):
                if len(batch_result['hits']['hits']) == 0:
                    message = 'No Category Mapping: %s' % ' '.join(str(item) for item in org_cat)
                    logging.getLogger(__name__).error(message)
                else:
                    item_cat = ItemCat(org_cat)
                    intg_id = batch_result['hits']['hits'][0]['_source']['intg_id']
                    cat_map = CatMap(INTG_ID=intg_id, UPDATE_TIME=datetime.datetime.now(timezone('Asia/Seoul')))
                    item_cat.cat_map.append(cat_map)
                    session.add(item_cat)
            session.commit()
        except IntegrityError as e:
            logger.error('Insertion Error %s' % e)
            session.rollback()
    session.close()


def producer_queue(queue):
    """
    Once this function finishes, it puts 'STOP' in queue, so that consumer knows this is done.

    :param queue: queue to put into your tasks
    """
    db_connector = MySQLConnector.from_config().db_engine
    session_factory = sessionmaker()
    session_factory.configure(bind=db_connector)
    Session = scoped_session(session_factory)  # thread-safe
    session = Session()

    index = 'intg_category'
    fields = ['intg_cat1', 'intg_cat2', 'intg_cat3', 'intg_cat4']

    # SELECT DISTINCT CAT1, CAT2, CAT3, CAT4 WHERE CAT_ID IS NULL;
    for result in DBUtils.page_query(session.query(EPInfo.CAT1, EPInfo.CAT2, EPInfo.CAT3, EPInfo.CAT4)
                                            .filter(EPInfo.CAT_ID.is_(None))
                                            .distinct(EPInfo.CAT1, EPInfo.CAT2, EPInfo.CAT3, EPInfo.CAT4)):
        mm_query = ESUtils.gen_mm_query(index, fields, ' '.join(str(i) for i in result if i is not None))
        queue.put({
            'org_category': [*result],
            'mm_query': mm_query
        })
        print('queue size %d' % queue.qsize())
    queue.put('STOP')


def consumer_queue(proc_id, queue):
    """
    This function opens up a database connection in a queue manner and insert processed data into
    :param proc_id: a process_id that each process is going to be assigned
    :param queue: a queue where each process is held.
    """
    db_connector = MySQLConnector.from_config().db_engine
    session_factory = sessionmaker()
    session_factory.configure(bind=db_connector)
    Session = scoped_session(session_factory)  # thread-safe

    while True:
        try:
            time.sleep(0.01)
            consumer_data = queue.get(proc_id, 1)  # timeout
            if consumer_data == 'STOP':
                logger.info('STOP received')
                # put stop back in queue for other consumers
                queue.put('STOP')
                break
            org_category = [consumer_data['org_category']]
            mm_query = consumer_data['mm_query']
            if queue.qsize() > 500:
                for i in range(50):
                    consumer_data = queue.get(proc_id, 1)
                    org_category.append(consumer_data['org_category'])
                    mm_query += consumer_data['mm_query']
            session = Session()
            batch_insert(session, org_category, mm_query)
        except Empty:
            pass


class ProcessManager:
    producers = []
    consumers = []

    def __init__(self):
        manager = Manager()
        self.queue = manager.Queue()

    def start(self):
        """
        This initializes all processes to run the function given in a multiprocessing manner.
        It initializes the number of processes of your cpu number.
        """
        self.producers = Process(target=producer_queue, args=(self.queue,))
        self.producers.start()
        self.consumers = [Process(target=consumer_queue, args=(i, self.queue,)) for i in range(cpu_count())]
        for consumer in self.consumers:
            consumer.start()

    def join(self):
        self.producers.join()
        for consumer in self.consumers:
            consumer.join()


def update_ep_info():
    """Join item_cat and ep_info to update cat_id updated in item_cat

    :return: None
    """
    db_connector = MySQLConnector.from_config().db_engine
    connection = db_connector.connect()
    connection.execute('SET SQL_SAFE_UPDATES = 0')
    connection.execute('UPDATE EP_INFO, ITEM_CAT '
                       'SET EP_INFO.CAT_ID = ITEM_CAT.CAT_ID '
                       'WHERE ITEM_CAT.CAT1 <=> EP_INFO.CAT1 '
                       'AND ITEM_CAT.CAT2 <=> EP_INFO.CAT2 '
                       'AND ITEM_CAT.CAT3 <=> EP_INFO.CAT3 '
                       'AND ITEM_CAT.CAT4 <=> EP_INFO.CAT4')
    connection.execute('SET SQL_SAFE_UPDATES = 1')
    connection.close()


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    try:
        print('start')
        t0 = time.time()
        manager = ProcessManager()
        manager.start()
        manager.join()
        print('update_info')
        update_ep_info()
        t1 = time.time()
        print(t1 - t0)
    except (KeyboardInterrupt, SystemExit):
        logger.info('Interrupt Signal Received')
        exit(1)
    except Exception as e:
        logger.error('Unknown Exception! %s' % e)
