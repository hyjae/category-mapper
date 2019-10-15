import logging
import datetime
from pytz import timezone
from sqlalchemy.orm import validates, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, TIMESTAMP, DATETIME, DECIMAL, ForeignKey


Base = declarative_base()

logger = logging.getLogger(__name__)


class IntgCat(Base):
    __tablename__ = 'INTG_CAT'

    INTG_ID = Column(String(15), primary_key=True)
    INTG_CAT1 = Column(String(60))
    INTG_CAT2 = Column(String(60))
    INTG_CAT3 = Column(String(60))
    INTG_CAT4 = Column(String(60))


class ItemCat(Base):
    __tablename__ = 'ITEM_CAT'

    CAT_ID = Column(Integer, primary_key=True)
    CAT1 = Column(String(60))
    CAT2 = Column(String(60))
    CAT3 = Column(String(60))
    CAT4 = Column(String(60))

    cat_map = relationship('CatMap', back_populates='item_cat')

    def __init__(self, cats):
        for i, cat in enumerate(cats):
            var = 'CAT{}'.format(i + 1)
            setattr(self, var, cat)


class CatMap(Base):
    __tablename__ = 'CAT_MAP'

    CAT_ID = Column(Integer, ForeignKey('ITEM_CAT.CAT_ID'), primary_key=True)
    INTG_ID = Column(String(15), ForeignKey('INTG_CAT.INTG_ID'))
    UPDATE_TIME = Column(TIMESTAMP, nullable=False, default=datetime.datetime.now(timezone('Asia/Seoul')))

    item_cat = relationship('ItemCat', back_populates='cat_map')


class EPInfo(Base):
    __tablename__ = 'EP_INFO'

    SHOPPING_ID = Column(Integer, primary_key=True)
    ITEM_CODE = Column(String(11), primary_key=True)
    ITEM_NAME = Column(String(150), nullable=False)
    CAT_ID = Column(Integer, ForeignKey('CAT_MAP.CAT_ID'))
    CAT1 = Column(String(60))
    CAT2 = Column(String(60))
    CAT3 = Column(String(60))
    CAT4 = Column(String(60))

    @validates('ITEM_NAME', 'CAT1', 'CAT2', 'CAT3', 'CAT4')
    def validate_length(self, key, value):
        max_len = getattr(self.__class__, key).prop.columns[0].type.length
        if value and len(value) > max_len:
            return value[:max_len]
        return value
