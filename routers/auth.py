from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from models.employer import CreateEmployer
from models.user import UserCreate, RoleEnum
from services.auth import AuthService

router = APIRouter(tags=["Auth"], prefix="/auth")


@router.post('/register/candidate')
async def register_candidate(user: UserCreate):
    return await AuthService.register_user(user, user_type=RoleEnum.CANDIDATE)


@router.post('/register/employer')
async def register_employer(user: UserCreate, employer_profile: CreateEmployer):
    return await AuthService.register_employer(user, employer_profile)


@router.post("/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    return await AuthService.get_jwt_token(form_data)
