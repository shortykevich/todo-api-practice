from pydantic import BaseModel, Field


class UserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str = Field(min_length=8, max_length=50)
    role: str
    phone_number: str = Field(min_length=5, max_length=15)


class Token(BaseModel):
    access_token: str
    token_type: str


class PhoneNumber(BaseModel):
    new_phone_number: str = Field(min_length=7, max_length=15)


class PasswordChangeModel(BaseModel):
    old_password: str = Field(min_length=8, max_length=50)
    new_password: str = Field(min_length=8, max_length=50)
    confirm_password: str = Field(min_length=8, max_length=50)
