from typing import Annotated

from fastapi import APIRouter, HTTPException, FastAPI
from fastapi.params import Depends
from starlette import status


from todo_app.models.users import User
from todo_app.database import db_dependency
from todo_app.utils.auth import get_current_user
from todo_app.schemas.users import PasswordChangeModel, PhoneNumber
from todo_app.utils.passwords import get_password_hash, verify_password

router = APIRouter(
    prefix="/user",
    tags=["user"],
)

user_dependency = Annotated[User, Depends(get_current_user)]


@router.get('/', status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="User unauthorized")
    return db.query(User).filter(User.id == user.get('id')).first()


@router.patch('/change-phone-number', status_code=status.HTTP_204_NO_CONTENT)
async def update_user_phone_number(user: user_dependency, db: db_dependency, new_phone_number: PhoneNumber):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="User unauthorized")
    user_model = db.query(User).filter(User.id == user.get('id')).first()
    user_model.phone_number = new_phone_number.phone_number
    db.add(user_model)
    db.commit()


@router.patch('/change-password', status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency, password: PasswordChangeModel):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="User unauthorized")

    user_model = db.query(User).filter(User.id == user.get('id')).first()
    if not verify_password(password.old_password, user_model.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect password")
    if password.new_password != password.confirm_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="New password does not match confirmation password")

    user_model.hashed_password = get_password_hash(password.new_password)
    db.add(user_model)
    db.commit()
