import logging
from sqlalchemy.orm import validates
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, TIMESTAMP, DATETIME, DECIMAL, ForeignKey

Base = declarative_base()

logger = logging.getLogger(__name__)


class Category(Base):
    __tablename__ = 'category'

    intg_id = Column(String(15), primary_key=True)
    intg_cat1 = Column(String(20), nullable=False)
    intg_cat2 = Column(String(20), nullable=True)
    intg_cat3 = Column(String(20), nullable=True)
    intg_cat4 = Column(String(20), nullable=True)


class CategoryEPInfo(Base):
    __tablename__ = 'category_ep_info'

    intg_id = Column(String(15), ForeignKey('category.intg_id'), primary_key=True)
    item_code = Column(String(11), ForeignKey('ep_info.ep_info'), primary_key=True)
    shopping_id = Column(Integer, ForeignKey('ep_info.shopping_id'), primary_key=True)
    process_yn = Column(TINYINT, nullable=True, default=0)
    process_time = Column(TIMESTAMP, nullable=True, default=None)


class EPInfo(Base):
    __tablename__ = 'ep_info'

    item_code = Column(String(15), primary_key=True)
    item_name = Column(String(100), nullable=False)
    shopping_id = Column(Integer, nullable=False)
    cat1 = Column(String(50), nullable=False)
    cat2 = Column(String(50), nullable=True)
    cat3 = Column(String(50), nullable=True)
    cat4 = Column(String(50), nullable=True)

    @validates('item_name', 'cat1', 'cat2', 'cat3', 'cat4')
    def validate_length(self, key, value):
        max_len = getattr(self.__class__, key).prop.columns[0].type.length
        if value and len(value) > max_len:
            return value[:max_len]
        return value
