from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

# Define the database file. It will be created in the same folder.
DATABASE_URL = "sqlite:///./meetings.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Meeting(Base):
    __tablename__ = "meetings"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    summary = Column(String, nullable=True)

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, index=True)
    assignee = Column(String)
    due_date_str = Column(String)
    status = Column(String, default="To Do")
    meeting_id = Column(Integer, ForeignKey("meetings.id"))

# This function creates the tables in the database
def create_db_and_tables():
    Base.metadata.create_all(bind=engine)