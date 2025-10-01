from sqlalchemy import create_engine, Column, Integer, String, Date, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

# --- Database Configuration ---
DATABASE_URL = "sqlite:///./agent.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Table Models ---

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)  # Storing plain-text password
    tasks = relationship("Task", back_populates="assignee")

class Meeting(Base):
    __tablename__ = "meetings"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    date = Column(Date)
    summary = Column(String)

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    due_date_str = Column(String)
    status = Column(String, default="To Do")
    is_locked = Column(Boolean, default=False)
    meeting_id = Column(Integer, ForeignKey("meetings.id"))
    assignee_id = Column(Integer, ForeignKey("users.id"))
    assignee = relationship("User", back_populates="tasks")
    updates = relationship("TaskUpdate", back_populates="task")

class TaskUpdate(Base):
    __tablename__ = "task_updates"
    id = Column(Integer, primary_key=True, index=True)
    comment = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    task = relationship("Task", back_populates="updates")

if __name__ == "__main__":
    print("Creating database and tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")