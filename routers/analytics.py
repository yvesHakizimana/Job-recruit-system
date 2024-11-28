from fastapi import APIRouter

from services.analytics import AnalyticsService

router = APIRouter(tags=["Analytics"], prefix="/analytics")


@router.get('/')
async def get_candidate_region_analytics():
    return await AnalyticsService.get_candidate_regional_distribution()


@router.get('/data_summary')
async def get_overall_summary():
    return await AnalyticsService.get_overall_statistics()


@router.get('/candidate_insights')
async def get_candidate_insights():
    return await AnalyticsService.get_candidate_overall_statistics()


@router.get('/employer_insights')
async def get_employer_insights():
    return await AnalyticsService.get_employers_overall_statistics()


@router.get('/job_post_insights')
async def get_job_post_insights():
    return await AnalyticsService.get_job_posts_overall_statistics()


@router.get('/job_application_insights')
async def get_application_insights():
    return await AnalyticsService.get_applications_overall_statistics()
