#configuration
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable = False)
    picture = Column(String(250))

class Task(Base):
    __tablename__ = 'task'

    name = Column(String(240), nullable = False)
    priority = Column(Integer, nullable = False)
    id = Column(Integer, primary_key = True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

engine = create_engine(
'sqlite:///todo.db')

Base.metadata.create_all(engine)
 