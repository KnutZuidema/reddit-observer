from typing import Union, Any, Type, Dict

from sqlalchemy import engine_from_config, Column, Integer, String, func
from sqlalchemy.engine.base import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.orm.attributes import QueryableAttribute


class SQLSession:

    def __init__(self, config: dict):
        self.engine: Engine = engine_from_config(config)
        self.session: Session = sessionmaker(bind=self.engine)()

    def close(self):
        self.session.close()

    def get_max(self, column: Union[QueryableAttribute, Type['Mention']]) -> Any:
        return self.session.query(func.max(column)).first()[0]

    def counts(self, column: Union[QueryableAttribute, Type['Mention']]) -> Dict[str, int]:
        query = self.session.query(column, func.count(column)).group_by(column)
        return dict(query)

    def count(self, column: Union[QueryableAttribute, Type['Mention']],
              comparison: Any) -> int:
        query = self.session.query(column)
        query = query.filter(column.collate('nocase') == comparison)
        return query.count()

    def counts_between(self, column: Union[QueryableAttribute, Type['Mention']],
                       lower: int, upper: int) -> Dict[str, int]:
        query = self.session.query(column, func.count(column))
        query = query.filter(Mention.timestamp.between(lower, upper))
        query = query.group_by(Mention.keyword)
        return dict(query)

    def count_between(self, column: Union[QueryableAttribute, Type['Mention']],
                      lower: int, upper: int, comparison: Any) -> int:
        query = self.session.query(column)
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
