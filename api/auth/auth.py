from datetime import datetime, timedelta
from typing_extensions import Annotated
from fastapi import APIRouter, Form, HTTPException, status, Depends

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from api.config.config import settings

from jose import JWTError, jwt

from sqlalchemy.orm import Session

from api.db.database import SessionLocal

from api.models.schema import CreateUser, Token

from api.models.models import UsersOrm

from passlib.context import CryptContext





oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/login/")
password_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@router.post("/register/", status_code=status.HTTP_201_CREATED)
async def register_user(create_user:Annotated[CreateUser, Form()], db:db_dependency):
    orm_user = UsersOrm(username = create_user.username, 
        password = password_context.hash(create_user.password))
    
    db.add(orm_user)
    db.commit()



@router.post("/login/", response_model=Token)
async def login_user(user_form: Annotated[OAuth2PasswordRequestForm, Depends()], db:db_dependency):
    user = authenticate_user(user_form.username, user_form.password, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate the user.")
    token = create_access_token(user.username, user.id, timedelta(minutes=20))
    return {"access_token":token, "token_type": "bearer"}




def authenticate_user(username:str, password:str, db):
    user = db.query(UsersOrm).filter(UsersOrm.username == username).first()
    if not user:
        return False
    if not password_context.verify(password, user.password):
        return False
    return user


def create_access_token(username: str, user_id: int, expires:timedelta):
    encode = {"sub": username, "id" : user_id}
    expiry_date = datetime.utcnow() + expires
    encode.update({"exp": expiry_date})
    return jwt.encode(encode, settings.SECRET_KEY, settings.ALGORITHM)


async def get_current_user(token:Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        user_id: str = payload.get("id")
        if email is None and user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate the user.")
        return {"email": email, "id": user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate the user.")
    

