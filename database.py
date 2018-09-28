from sqlalchemy import engine_from_config, Column, Integer, String
from sqlalchemy.engine.base import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

engine: Engine = None
session_creator: sessionmaker = None


def get_session(config: dict) -> Session:
    global engine, session_creator
    if not engine:
        engine = engine_from_config(config)
    if not session_creator:
        session_creator = sessionmaker(bind=engine)
    return session_creator()


Base = declarative_base()


class Keyword(Base):
    __tablename__ = 'keywords'

    id = Column(Integer, primary_key=True)
    keyword = Column(String)
    timestamp = Column(Integer)
    permalink = Column(String)
    subreddit = Column(String)
    commenter = Column(String)
