from datetime import timedelta

from fastapi import APIRouter, HTTPException
from starlette import status

from todo_app.models.users import User
from todo_app.schemas.users import UserRequest, Token
from todo_app.utils.passwords import bcrypt_context
from todo_app.utils.auth import outh_form_dependency, authenticate_user, create_access_token
from todo_app.database import db_dependency


router = APIRouter(
    prefix='/auth',
    tags=['auth'],
)


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, user_request: UserRequest):
    user_model = User(
        email=user_request.email,
        username=user_request.username,
        first_name=user_request.first_name,
        last_name=user_request.last_name,
        role=user_request.role,
        hashed_password=bcrypt_context.hash(user_request.password),
        phone_number=user_request.phone_number,
        is_active=True,
    )
    db.add(user_model)
    db.commit()


@router.post('/token', status_code=status.HTTP_200_OK, response_model=Token)
async def login_for_access_token(form_data: outh_form_dependency,
                                 db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid credentials')

    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))
    return {'access_token': token, 'token_type': 'bearer'}
