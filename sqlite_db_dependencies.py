from pydantic import BaseModel, Field
from typing import Optional
from sqlite_db_setup import Base
from uuid import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Float, Uuid, Boolean, ForeignKey

#create pydantic models
class CategoryBase(BaseModel):
    category: str
    income_cat: bool

class RecordBase(BaseModel):
    record_id: Optional[UUID] = None
    date: Optional[str] = None
    category: str
    description: Optional[str] = None
    amount: float

class GoalBase(BaseModel):
    title: str
    amount: float
    priority: int = Field(ge=1, le=5, default=1)

#create models of SQL tables
class Categories(Base):
    __tablename__ = 'categories'

    category = Column(String(100), primary_key=True, index=True)
    income_cat = Column(Boolean)

class Records(Base):
    __tablename__ = 'records'

    record_id = Column(Uuid, primary_key=True, index=True)
    date = Column(String(30))
    category = Column(String(100), ForeignKey('categories.category', onupdate='CASCADE', ondelete='CASCADE'))
    description = Column(String(150))
    amount = Column(Float)

    record_category = relationship('Categories', foreign_keys='category')
class Goals(Base):
    __tablename__ = 'savings_goals'

    title = Column(String(100), primary_key=True, index=True)
    amount = Column(Float)
    priority = Column(Integer)