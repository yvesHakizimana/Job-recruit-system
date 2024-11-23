from datetime import timedelta, datetime, timezone

from bson import ObjectId
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from core.config import settings
from core.database import user_collection, employer_profile, candidate_profile
from core.security import hash_password, verify_password, create_jwt_token
from models.employer import CreateEmployer
from models.user import UserCreate, RoleEnum


class AuthService:
    @staticmethod
    async def register_user(user: UserCreate, user_type: RoleEnum):
        # Check if the email already exists
        user_from_db = await user_collection.find_one({"email": user.email})
        if user_from_db:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Hash the user's password
        user.password = hash_password(user.password)

        # Build user data
        user_data = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "password": user.password,
            "role": user_type.value,
        }

        # Insert the user into the database
        new_user = await user_collection.insert_one(user_data)

        # Fetch the created user
        created_user = await user_collection.find_one({"_id": new_user.inserted_id})

        if user_type == RoleEnum.CANDIDATE:
            default_profile_data = {
                "candidate_id": (created_user["_id"]),
                "profile_cv": {
                    "picture": None,
                    "cv_file": None,
                    "experience": [],
                    "education": [],
                    "linkedin": None,
                },
                "job_criteria": None,
                "skills": {
                    "skill_description": None,
                    "spoken_languages": [],
                    "expertise": None
                },
                "created_at": datetime.now(timezone.utc)
            }
            await candidate_profile.insert_one(default_profile_data)

        return {
            "id": str(created_user["_id"]),
            "first_name": created_user["first_name"],
            "last_name": created_user["last_name"],
            "email": created_user["email"],
            "role": created_user["role"],
            "message": "User Profile created successfully"
        }

    @staticmethod
    async def register_employer(user: UserCreate, employer: CreateEmployer):
        # Register the employer as a user with the "employer" role
        user_data = await AuthService.register_user(user, RoleEnum.EMPLOYER)

        # Build employer profile data
        employer_data = {
            "employer_id": ObjectId(user_data["id"]),  # Reference to the user's ObjectId
            "company_name": employer.company_name,
            "address": employer.address,
            "zip_code": employer.zip_code,
            "city": employer.city,
            "country": employer.country,
            "company_industry": employer.company_industry,
            "company_description": employer.company_description,
            "position_in_organization": employer.position_in_organization,
        }

        # Insert the employer profile into the database
        new_employer = await employer_profile.insert_one(employer_data)

        created_employer = await employer_profile.find_one({"_id": new_employer.inserted_id})

        return {
            "message": "Employer registered successfully",
            "user": user_data,
            "employer_profile": {
                "id": str(created_employer["_id"]),
                "user_id": str(created_employer["employer_id"]),
                "company_name": created_employer["company_name"],
                "address": created_employer["address"],
                "zip_code": created_employer["zip_code"],
                "city": created_employer["city"],
                "country": created_employer["country"],
                "company_industry": created_employer["company_industry"],
                "company_description": created_employer["company_description"],
                "position_in_organization": created_employer["position_in_organization"],
            },
        }

    @staticmethod
    async def get_jwt_token(form_data: OAuth2PasswordRequestForm):
        try:
            user = await user_collection.find_one({"email": form_data.username})
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database connection error",
            )

        if not user or not verify_password(form_data.password, user['password']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = await create_jwt_token(
            data={"id": str(user["_id"]), "email": user['email'], "role": user['role']}, expire_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
