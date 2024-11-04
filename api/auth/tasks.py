import asyncio
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List
from fastapi.responses import JSONResponse
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr
from typing_extensions import Annotated
from fastapi import APIRouter, Depends, FastAPI, Form, status, HTTPException

from api.config.config import settings

import smtplib

from api.auth import auth

from api.models.models import TaskOrm

from sqlalchemy.orm import Session

from api.models.schema import AddToDo, EmailSchema

from apscheduler.schedulers.background import BackgroundScheduler


from api.db.database import engine, SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(auth.get_current_user)]


task_router = APIRouter(
    prefix="/tasks",
    tags=["task"]
)

email_router = APIRouter(
    prefix="/email",
    tags = ["email"]
)


@task_router.post("/")
async def add_task(create_todo:Annotated[AddToDo, Form()], db:db_dependency, 
                   user:user_dependency):

    orm_todo = TaskOrm(name = create_todo.name, description = create_todo.description, 
                       user_id = user.get("id"),
                       priority = create_todo.priority, deadline = create_todo.deadline)
        



    db.add(orm_todo)
    db.commit()
    return {"name": orm_todo.name, "description": orm_todo.description, 
            "priority": orm_todo.priority}


def user_query(user_id: int, db):
    user = db.query(TaskOrm).filter(TaskOrm.user_id == user_id).first()
    return user

@task_router.get("/")
async def get_tasks(db:db_dependency, user:user_dependency):
    user_tasks = user_query(user.get("id"), db)
    return user_tasks


@task_router.delete("/")
async def delete_tasks(db:db_dependency, user:user_dependency):
    user_tasks = user_query(user.get("id"), db)
    db.delete(user_tasks)
    db.commit()

@task_router.delete("/{task_id}")
async def delete_tasks(db:db_dependency, user:user_dependency):
    user_tasks = user_query(user.get("id"), db)
    db.delete(user_tasks)
    db.commit()




def tasks_query(id:int, db:Session):
    return db.query(TaskOrm).filter(TaskOrm.user_id == id).all()



conf = ConnectionConfig(
    MAIL_USERNAME = settings.MAIL_USERNAME,
    MAIL_PASSWORD = settings.MAIL_PASSWORD,
    MAIL_FROM = settings.MAIL_FROM,
    MAIL_PORT = settings.MAIL_PORT,
    MAIL_SERVER = settings.MAIL_SERVER,
    MAIL_STARTTLS = False,
    MAIL_SSL_TLS = True,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)





body = f"Your Task is due soon"


async def send_email(recipents:List[str]):
    message = MessageSchema(
        subject="Task Reminder",
        recipients=recipents,
        body = body,
        subtype=MessageType.html)
    
    fm = FastMail(conf)
    await fm.send_message(message)


@email_router.get("/")
async def read_email(user: user_dependency, db:db_dependency):
    email: str = user.get("email")
    await send_email([email])
    return {"email": "Email was successfully send"}

@email_router.get("/complex")
async def read_email(user: user_dependency, db:db_dependency):
    now = datetime.utcnow()
    user_id = user.get("id")
    tasks = tasks_query(user_id, db)
    for task in tasks:
        if task.deadline - now <= timedelta(hours=1):
            email: str = user.get("email")
            await send_email([email])
            task.is_reminder_sent = True
            db.add(task)
            db.commit()
            return JSONResponse(status_code=200, content={"message": "email has been sent"})








