from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

db_url = 'sqlite:///budget_application.db'

engine = create_engine(db_url)

Base = declarative_base()