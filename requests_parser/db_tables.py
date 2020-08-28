from .config import DATABASE_SETTINGS

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

USER = DATABASE_SETTINGS['user']
PASSWORD = DATABASE_SETTINGS['password']
DATABASE = DATABASE_SETTINGS['database']

engine = create_engine(
    f'postgresql+psycopg2://{USER}:{PASSWORD}@localhost:5432/{DATABASE}'
)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class BankruptMessage(Base):
    """"""
    __tablename__ = 'messages'

    id = Column(Integer, unique=True, nullable=False, primary_key=True)
    guid = Column(String(99), nullable=False)
    text = Column(String(499), nullable=False)
    date = Column(DateTime)
    url = Column(String(99), nullable=False)

    def __repr__(self):
        return f'<message: {self.url} | [{self.date}]>'

    def __init__(self, guid, text, date, url):
        self.guid = guid
        self.text = text
        self.date = date
        self.url = url
