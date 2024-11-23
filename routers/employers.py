from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.params import Query

from core.security import check_employer_role
from models.application import StatusEnum
from models.job_post import JobPost
from services.employer import EmployerService, UpdateEmployerProfile

router = APIRouter(tags=["Employers"], prefix="/employer")


@router.post('/create_job_post')
async def create_job_post(job_post: JobPost, current_user=Depends(check_employer_role)):
    return await EmployerService.create_job_post(job_post=job_post, current_user=current_user)


@router.get('/get_job_posts')
async def get_job_post(
        page: int = Query(1, ge=1, description="Page Number"),
        limit: int = Query(10, ge=1, le=100),
        job_title: str | None = None,
        current_user=Depends(check_employer_role)):
    return await EmployerService.get_job_posts(page, limit, job_title, current_user=current_user)


@router.get('/me/profile')
async def get_employer_profile_info(current_user=Depends(check_employer_role)):
    return await EmployerService.get_profile(current_user=current_user)


@router.put('/me/profile/update')
async def update_employer_profile_info(updated_profile: UpdateEmployerProfile,
                                       current_user=Depends(check_employer_role)):
    return await EmployerService.update_profile(updated_profile=updated_profile, current_user=current_user)


@router.get('/applications/{job_id}')
async def get_all_application_specific_for_job_post(
        job_id: str,
        status: Optional[StatusEnum] = Query(None, description="Filter by the application status"),
        current_user=Depends(check_employer_role)):
    return await EmployerService.get_applications(job_id=job_id, status=status, current_user=current_user)


@router.get('/applications/{job_id}/{application_id}')
async def get_user_application_details(job_id: str, application_id: str, current_user=Depends(check_employer_role)):
    return await EmployerService.get_user_application(job_id=job_id, application_id=application_id,
                                                      current_user=current_user)


@router.patch('/applications/{job_id}/{application_id}')
async def approve_user_application(job_id: str, application_id: str, current_user=Depends(check_employer_role)):
    return await EmployerService.approve_user_application(job_id=job_id, application_id=application_id,
                                                          current_user=current_user)
