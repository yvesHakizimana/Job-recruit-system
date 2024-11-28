from fastapi import APIRouter
from services.api_data import ApiService

router = APIRouter(tags=["Data"], prefix="/data")


@router.get('/job_posts')
async def get_job_posts():
    return await ApiService.get_all_job_posts()


@router.get('/employer_profiles')
async def get_all_employer_profiles():
    return await ApiService.get_employer_profiles()
