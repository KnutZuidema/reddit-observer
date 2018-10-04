from collections import defaultdict
from typing import Union, Any, Type, Dict, List, Tuple

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

    def get_submissions(self, keyword: str) -> List[Tuple[str, str, int]]:
        query = self.session.query(Mention.permalink)
        query = query.filter(Mention.keyword.collate('nocase') == keyword)
        submissions = defaultdict(int)
        for permalink in query:
            link = permalink.rsplit('/', maxsplit=2)[0]
            title = permalink.split('/')[4].replace('_', ' ')
            submissions[(link, title)] += 1
        return [(link, title, mentions) for (link, title), mentions in submissions.items()]

    def get_commenters(self, keyword: str) -> List[Tuple[str, int]]:
        query = self.session.query(Mention.commenter, func.count(Mention.commenter))
        query = query.filter(Mention.keyword.collate('nocase') == keyword)
        query = query.group_by(Mention.commenter)
        return list(query)


Base = declarative_base()


class Mention(Base):
    __tablename__ = 'keywords'

    id = Column(Integer, primary_key=True)
    keyword = Column(String)
    timestamp = Column(Integer)
    permalink = Column(String)
    subreddit = Column(String)
    commenter = Column(String)
