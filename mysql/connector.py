import logging
from config import ConfigManager
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class MySQLConnector:

    @classmethod
    def from_config(cls):
        config = ConfigManager()
        db_settings = config.get_setting('mysql')
        db_connector = DBConnector('mysql', db_settings)
        cls.db_engine = db_connector.db_engine
        return cls


class DBConnector:
    # http://docs.sqlalchemy.org/en/latest/core/engines.html
    DB_ENGINE = {'mysql': 'mysql://{username}:{password}@{address}/{dbname}?charset={charset}'}

    def __init__(self, db_type, db_settings):
        self.logger = logging.getLogger(__name__)

        db_type = db_type.lower()
        if db_type in self.DB_ENGINE.keys():
            engine_url = self.DB_ENGINE[db_type].format(**db_settings)
            self.db_engine = create_engine(engine_url, pool_size=10, max_overflow=5, pool_recycle=3600)
            Base.metadata.bind = self.db_engine
        else:
            self.logger.error('Not Supported Database: %s' % db_type)
            exit(1)
