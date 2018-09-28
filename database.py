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


def get_max(session: Session,
            column: Union[QueryableAttribute, Type['Keyword']]) -> Any:
    return session.query(func.max(column)).first()[0]


def counts(session: Session, column: Union[QueryableAttribute, Type['Keyword']]) -> Dict[str, int]:
    query = session.query(column, func.count(column)).group_by(column)
    return dict(query)


def count(session: Session,
          column: Union[QueryableAttribute, Type['Keyword']],
          comparison: Any = None) -> int:
    query = session.query(column)
    if comparison:
        query = query.filter(column.collate('nocase') == comparison)
    return query.count()


def counts_between(
        session: Session,
        column: Union[QueryableAttribute, Type['Keyword']],
        lower: int, upper: int) -> Dict[str, int]:
    query = session.query(column, func.count(column))
    query = query.filter(Keyword.timestamp.between(lower, upper))
    query = query.group_by(Keyword.keyword)
    return dict(query)


def count_between(session: Session,
                  column: Union[QueryableAttribute, Type['Keyword']],
                  lower: int, upper: int, comparison: Any = None) -> int:
    query = session.query(column)
    if comparison:
        query = query.filter(column.collate('nocase') == comparison)
    return query.filter(Keyword.timestamp.between(lower, upper)).count()


Base = declarative_base()


class Keyword(Base):
    __tablename__ = 'keywords'

    id = Column(Integer, primary_key=True)
    keyword = Column(String)
    timestamp = Column(Integer)
    permalink = Column(String)
    subreddit = Column(String)
    commenter = Column(String)
