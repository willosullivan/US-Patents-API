from sqlalchemy import Column, VARCHAR, FLOAT, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()
# See here for more details about declaring `models`
# https://docs.sqlalchemy.org/en/14/orm/quickstart.html#declare-models


class Inventor(Base):
    __tablename__ = 'inventors'

    key_id = Column(VARCHAR, primary_key=True)
    first_name = Column(VARCHAR, nullable=False)
    last_name = Column(VARCHAR, nullable=False)
    location_city = Column(VARCHAR, nullable=False)
    location_state = Column(VARCHAR, nullable=False)
    location_longitude = Column(FLOAT)
    location_latitude = Column(FLOAT)


class Patent(Base):
    __tablename__ = 'patents'

    patent_id = Column(VARCHAR, primary_key=True)
    patent_title = Column(VARCHAR, nullable=False)
    created_at = Column(VARCHAR)
    updated_at = Column(VARCHAR)


class InventorPatentMapping(Base):
    __tablename__ = 'inventor_patent_mapping'

    id = Column(VARCHAR, primary_key=True)
    patent_id = Column(
        VARCHAR,
        ForeignKey(Patent.patent_id),
        nullable=False,
    )
    inventor_key_id = Column(
        VARCHAR,
        ForeignKey(Inventor.key_id),
        nullable=False,
    )
