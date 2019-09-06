import time
import logging
from queue import Empty
from sqlalchemy.exc import *
from database.utils import *
from database.object import *
from database.cnnt import MySQLConnector
from multiprocessing import Process, cpu_count, Manager
from sqlalchemy.orm import scoped_session, sessionmaker

logging.basicConfig(filename='error.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.ERROR)
logger = logging.getLogger('sqlalchemy.engine')
logger.setLevel(logging.ERROR)


def batch_insert(session, result, clazz):
    """
    :param session: sqlalchemy session object
    :param result: a list of output to insert to database
    :param clazz: output class to insert into db
    """
    batch_insert = []
    for batch_object in result:
        # only if you need to check key constraints
        # record = session.query(clazz).get({batch_object.ma_id})
        # if record:
        #     logger.error('duplicate entry in db %s' % batch_object.ma_id)
        #     continue
        batch_insert.append(batch_object)
    if batch_insert:
        try:
            session.add_all(batch_insert)
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

    for ep_info in DBUtils.page_query(session.query(CategoryEPInfo, EPInfo).filter_by(
            process_yn=0).filter_by(CategoryEPInfo.item_code == EPInfo.item_code)):
        ep_info


    for line in FileSplitter():
        parser = JsonLineParser(line)
        results = parser.get_values()
        for elements in results:
            for element in elements:
                customer_purchase_history = CustomerPurchaseHistory()
                customer_purchase_history.set_values(element)
                queue.put(customer_purchase_history)
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
            consumer_data_batch = [consumer_data]
            if queue.qsize() > 500:
                for i in range(50):
                    consumer_data = queue.get(proc_id, 1)
                    consumer_data_batch.append(consumer_data)
            session = Session()
            batch_insert(session, consumer_data_batch, CustomerPurchaseHistory)
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


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    try:
        print('start')
        t0 = time.time()
        manager = ProcessManager()
        manager.start()
        manager.join()
        t1 = time.time()
        print(t1 - t0)
    except (KeyboardInterrupt, SystemExit):
        logger.info('Interrupt Signal Received')
        exit(1)
    except Exception as e:
        logger.error('Unknown Exception! %s' % e)