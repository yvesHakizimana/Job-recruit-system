from optparse import Option
from typing import Optional

from fastapi import APIRouter, Depends, UploadFile, Query

from core.security import get_current_user
from models.candidate import CandidateBasicInfo, CandidateProfile, JobCriteria, Skills, RegionEnum, ExperienceLevelEnum, \
    DesiredSalaryEnum
from services.candidate import CandidateService

router = APIRouter(tags=["Candidates"], prefix="/candidate", dependencies=[Depends(get_current_user)])


# Create and update the user profile
@router.get("/profile")
async def get_candidate_profile(current_user=Depends(get_current_user)):
    return await CandidateService.get_user_profile(current_user)


@router.patch("/profile/update")
async def edit_profile_information(candidate_info: CandidateBasicInfo, current_user=Depends(get_current_user)):
    return await CandidateService.update_candidate_profile(current_user, candidate_info)


@router.patch("/job_criteria/update")
async def edit_job_criteria_info(job_criteria_info: JobCriteria, current_user=Depends(get_current_user)):
    return await CandidateService.update_job_criteria_info(current_user, job_criteria_info)


@router.patch("/skills/update")
async def edit_skills_info(skills_info: Skills, current_user=Depends(get_current_user)):
    return await CandidateService.update_skills_info(current_user, skills_info)


@router.patch("/profile_files/edit")
async def edit_user_profile_files(profile_pic: UploadFile = None, cv_file: UploadFile = None,
                                  current_user=Depends(get_current_user)):
    return await CandidateService.upload_user_basic_files(profile_pic, cv_file, current_user)


@router.get("/jobs")
async def get_jobs(
        page: int = Query(1, ge=1, description="Page Number, starting from 1"),
        limit: int = Query(10, ge=1, description="The Number of jobs per page, (max 100)"),
        region: Optional[RegionEnum] = Query(None, description="Filter jobs per region"),
        city: Optional[str] = Query(None, description="Filter jobs per city (case-insensitive)"),
        experience_level: Optional[ExperienceLevelEnum] = Query(None, description="Filter jobs per experience level"),
        job_ad_title: Optional[str] = Query(None, description="Filter jobs per ad title"),
        offered_salary: Optional[DesiredSalaryEnum] = Query(None, description="Filter jobs per offered salary"),
):
    """
       Fetch job posts with optional filters and pagination.

       Args:
           page (int): The current page number.\n
           limit (int): The number of jobs to display per page.
           region (RegionEnum): Filter jobs by region.
           city (str): Filter jobs by city (case-insensitive).
           experience_level (ExperienceLevelEnum): Filter jobs by experience level.
           job_ad_title (str): Filter jobs by job title (case-insensitive).
           offered_salary (DesiredSalaryEnum): Filter jobs by salary range.

       Returns:
           dict: Paginated job posts with metadata.\n
       """
    return await CandidateService.get_jobs_posted(
        page=page,
        limit=limit,
        region=region,
        city=city,
        experience_level=experience_level,
        job_ad_title=job_ad_title,
        offered_salary=offered_salary,
    )


@router.get("/jobs/{job_id}")
async def get_job(job_id: str, ):
    return await CandidateService.get_job_post(job_id=job_id)


@router.post('/jobs/apply/{job_id}')
async def apply_job(job_id: str, current_user=Depends(get_current_user)):
    return await CandidateService.apply_for_job_post(job_id=job_id, current_user=current_user)


@router.get('/applications')
async def get_applications(
        page: int = Query(1, ge=1, description="The current page number, starting from 1"),
        limit: int = Query(10, ge=1, le=100, description="The number of applications per page, (max 100)"),
        job_ad_title: Optional[str] = Query(None, description="Filter jobs by job title (case-insensitive)."),
        current_user=Depends(get_current_user)):
    return await CandidateService.get_applications(page, limit, job_ad_title, current_user)


@router.patch('/applications/{application_id}')
async def withdraw_appplication(application_id: str, current_user=Depends(get_current_user)):
    return await CandidateService.withdraw_application(application_id=application_id, current_user=current_user)
