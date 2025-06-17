from sqlalchemy import (
    Column, ForeignKey, Integer, String, ARRAY, Float
)
from sqlalchemy.dialects.postgresql import JSONB

from sqlalchemy.orm import declarative_base

from ccm_benchmate.knowledge_base.tables import Base


class Structure(Base):
    __tablename__="structure"
    id = Column(Integer, primary_key=True, autoincrement=True)


