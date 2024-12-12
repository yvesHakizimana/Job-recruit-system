from fastapi import APIRouter
from fastapi.params import Query

from services.api_data import ApiService

router = APIRouter(tags=["Data"], prefix="/data")


@router.get('/job_posts')
async def get_job_posts(
        limit: int = Query(100, ge=1, description="Number of jobs to return"),
        page: int = Query(1, ge=1, description="Current page number"),
):
    return await ApiService.get_all_job_posts(limit, page)


@router.get('/employer_profiles')
async def get_all_employer_profiles(
        limit: int = Query(100, ge=1, description="Number of employers to return"),
        page: int = Query(1, ge=1, description="Current page number"),
):
    return await ApiService.get_employer_profiles(limit, page)


@router.get('/candidate_profiles')
async def get_all_employer_profiles(
        limit: int = Query(100, ge=1, description="Number of candidates to return"),
        page: int = Query(1, ge=1, description="Current page number"),
):
    return await ApiService.get_candidate_profiles(limit, page)


@router.get('/applications')
async def get_all_applications(
        limit: int = Query(100, ge=1, description="Number of applications to return"),
        page: int = Query(1, ge=1, description="Current page number"),
):
    return await ApiService.get_applications(limit, page)


@router.get('/users')
async def get_all_users(
        limit: int = Query(100, ge=1, description="Number of users to return"),
        page: int = Query(1, ge=1, description="Current page number"),
):
    return await ApiService.get_all_users(limit, page)
