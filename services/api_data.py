from core.database import job_posts, employer_profile, candidate_profile, applications, user_collection
from services.paginate import PaginationService


class ApiService:
    @staticmethod
    async def get_all_job_posts(limit: int = 100, page: int = 1):
        return await PaginationService.get_paginated_data(job_posts, limit=limit, page=page)

    @staticmethod
    async def get_employer_profiles(limit: int = 100, page: int = 1):
        return await PaginationService.get_paginated_data(employer_profile, limit=limit, page=page)

    @staticmethod
    async def get_candidate_profiles(limit: int = 100, page: int = 1):
        return await PaginationService.get_paginated_data(candidate_profile, limit=limit, page=page)

    @staticmethod
    async def get_applications(limit: int = 100, page: int = 1):
        return await PaginationService.get_paginated_data(applications, limit=limit, page=page)

    @staticmethod
    async def get_all_users(limit: int = 100, page: int = 1):
        return await PaginationService.get_paginated_data(user_collection, limit=limit, page=page)
