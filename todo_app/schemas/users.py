from pydantic import BaseModel, Field, EmailStr, field_validator, constr
from pydantic_extra_types.phone_numbers import PhoneNumber


class UserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    email: EmailStr
    first_name: str
    last_name: str
    password: str = Field(
        min_length=8,
        description='Password must be at least 8 characters long and contain '
                    'uppercase letters, lowercase letters, digits and special characters: @$!%*?&#',
        examples=['Passw0rd!']
    )
    role: str
    phone_number: PhoneNumber

    @field_validator('password')
    def validate_password(cls, password):
        if not any(char.islower() for char in password):
            raise ValueError('Password must contain at least one lowercase letter')

        if not any(char.isupper() for char in password):
            raise ValueError('Password must contain at least one uppercase letter')

        if not any(char.isdigit() for char in password):
            raise ValueError('Password must contain at least one digit')

        special_characters = "@$!%*?&#"
        if not any(char in special_characters for char in password):
            raise ValueError(f'Password must contain at least one special character: {special_characters}')

        return password

    @classmethod
    def validate_alphabetic(cls, name: str) -> str:
        if not all(char.isalpha() for char in name):
            raise ValueError(f'{name.__name__} must contain only alphabetic characters')
        return name

    @field_validator('first_name')
    def validate_first_name(cls, first_name: str) -> str:
        return cls.validate_alphabetic(first_name)

    @field_validator('last_name')
    def validate_last_name(cls, last_name: str) -> str:
        return cls.validate_alphabetic(last_name)



class Token(BaseModel):
    access_token: str
    token_type: str


class PhoneNum(BaseModel):
    phone_number: str = Field(min_length=7, max_length=15)


class PasswordChangeModel(BaseModel):
    password: str = Field(min_length=8, max_length=50)
    new_password: str = Field(min_length=8, max_length=50)
    confirm_password: str = Field(min_length=8, max_length=50)
