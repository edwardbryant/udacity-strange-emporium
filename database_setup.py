
import sys

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship 
from sqlalchemy import create_engine

Base = declarative_base()

"""
class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key = True)
    name = Column(String(250), nullable = False)
    email = Column(String(250), nullable = False)
    image = Column(String(250), nullable = False)
"""

class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key = True)
    name = Column(String(80), nullable = False)
    img = Column(String(250))
    featured = Column(Integer)
    price = Column(String(32))
    description = Column(String(250))
"""
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
"""

class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key = True)
    name = Column(String(80), nullable = False)


class ItemCategory(Base):
    __tablename__ = 'item_category'
    id = Column(Integer, primary_key = True)
    item_id = Column(Integer, ForeignKey('item.id'))
    category_id = Column(Integer, ForeignKey('category.id'))  
    item = relationship(Item)
    category = relationship(Category)


engine = create_engine('sqlite:///strange_emporium.db')

Base.metadata.create_all(engine)