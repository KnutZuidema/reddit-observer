from sqlalchemy import engine_from_config, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


def get_session(config):
    engine = engine_from_config(config)
    return sessionmaker(bind=engine)


Base = declarative_base()


class Keyword(Base):
    __tablename__ = 'keywords'

    id = Column(Integer, primary_key=True)
    keyword = Column(String)
    timestamp = Column(Integer)
    permalink = Column(String)
    subreddit = Column(String)
    commenter = Column(String)
