from typing import Union, Any, Type, Dict

from sqlalchemy import engine_from_config, Column, Integer, String, func
from sqlalchemy.engine.base import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.orm.attributes import QueryableAttribute

engine: Engine = None
session_creator: sessionmaker = None


def get_session(config: dict) -> Session:
    global engine, session_creator
    if not engine:
        engine = engine_from_config(config)
    if not session_creator:
        session_creator = sessionmaker(bind=engine)
    return session_creator()


def get_max(session: Session, column: Union[QueryableAttribute, Type['Mention']]) -> Any:
    return session.query(func.max(column)).first()[0]


def counts(session: Session, column: Union[QueryableAttribute, Type['Mention']]) -> Dict[str, int]:
    query = session.query(column, func.count(column)).group_by(column)
    return dict(query)


def count(session: Session, column: Union[QueryableAttribute, Type['Mention']],
          comparison: Any) -> int:
    query = session.query(column)
    query = query.filter(column.collate('nocase') == comparison)
    return query.count()


def counts_between(session: Session, column: Union[QueryableAttribute, Type['Mention']],
                   lower: int, upper: int) -> Dict[str, int]:
    query = session.query(column, func.count(column))
    query = query.filter(Mention.timestamp.between(lower, upper))
    query = query.group_by(Mention.keyword)
    return dict(query)


def count_between(session: Session, column: Union[QueryableAttribute, Type['Mention']],
                  lower: int, upper: int, comparison: Any) -> int:
    query = session.query(column)
    query = query.filter(column.collate('nocase') == comparison)
    return query.filter(Mention.timestamp.between(lower, upper)).count()


Base = declarative_base()


class Mention(Base):
    __tablename__ = 'keywords'

    id = Column(Integer, primary_key=True)
    keyword = Column(String)
    timestamp = Column(Integer)
    permalink = Column(String)
    subreddit = Column(String)
    commenter = Column(String)
