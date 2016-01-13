# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from radiople.config import config

engine = create_engine(
    config.common.db.uri, pool_size=5, echo=config.common.db.echo)

Session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()
