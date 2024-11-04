
from typing_extensions import Annotated
from fastapi import Depends, FastAPI, Form, status, HTTPException
import uvicorn



from api.models import models
from api.auth import auth, tasks


from sqlalchemy.orm import Session



from api.db.database import engine, SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(auth.get_current_user)]



app = FastAPI()
app.include_router(auth.router)
app.include_router(tasks.task_router)
app.include_router(tasks.email_router)

models.Base.metadata.create_all(bind = engine)


@app.get("/", status_code=status.HTTP_200_OK)
async def user(user:user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    return {"User":user}

if __name__ == "__main__":
    uvicorn.run(app, port=8000)



















    