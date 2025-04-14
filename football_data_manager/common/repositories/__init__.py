from abc import ABCMeta

from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta


class AlchemyABCMeta(DeclarativeMeta, ABCMeta):
    pass


Base = declarative_base(metaclass=AlchemyABCMeta)
