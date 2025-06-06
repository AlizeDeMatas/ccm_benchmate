import pandas as pd

from sqlalchemy import MetaData, select
from sqlalchemy.orm import Session


class KnowledgeBase:
    def __init__(self, engine):
        self.engine = engine
        self.meta = MetaData(bind=self.engine)
        self.meta.reflect(bind=self.engine)
        self.session = Session(self.engine)
        self.db_tables = self.meta.tables




#TODO try some large-ish models for chatting with the data