from enum import Enum

from bson import ObjectId
from pydantic import BaseModel, EmailStr


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        if not ObjectId.is_valid(value):
            raise ValueError('Invalid object id')
        return ObjectId(value)


class GenderEnum(str, Enum):
    MALE = "Male"
    FEMALE = "Female"


class RoleEnum(str, Enum):
    EMPLOYER = "employer"
    CANDIDATE = "candidate"


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    gender: GenderEnum
    password: str

