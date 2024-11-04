from datetime import timedelta
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import Boolean, Column, Enum, ForeignKey, Integer, String, DateTime

from sqlalchemy.orm import relationship

from api.models.schema import TaskPriority

Base = declarative_base()


class UsersOrm(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key = True)
    username = Column(String, unique = True)
    password = Column(String)

    task = relationship("TaskOrm", back_populates = "user")


class TaskOrm(Base):
    __tablename__ = "task"

    id = Column(Integer, primary_key = True)
    name = Column (String) 
    description = Column (String, nullable = True)
    priority = Column(Enum(TaskPriority))
    deadline = Column(DateTime, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    is_reminder_sent = Column(Boolean)




    user = relationship("UsersOrm", back_populates = "task" )

    

