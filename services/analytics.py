from core.database import candidate_profile, employer_profile, applications, job_posts
from utils.transform import objectid_to_str


# helper functions
async def get_employers_by_size():
    size_buckets = [
        {"min": 1, "max": 10},
        {"min": 11, "max": 50},
        {"min": 51, "max": 200},
        {"min": 201, "max": 500},
        {"min": 501, "max": 1000},
        {"min": 1001, "max": float('inf')}
    ]

    pipeline = [
        {
            "$project": {
                "company_name": 1,
                "number_of_employees": 1,
                "employee_size_category": {
                    "$switch": {
                        "branches": [
                            {"case": {"$lte": ["$number_of_employees", 10]}, "then": "1-10"},
                            {"case": {"$and": [{"$gte": ["$number_of_employees", 11]},
                                               {"$lte": ["$number_of_employees", 50]}]}, "then": "11-50"},
                            {"case": {"$and": [{"$gte": ["$number_of_employees", 51]},
                                               {"$lte": ["$number_of_employees", 200]}]}, "then": "51-200"},
                            {"case": {"$and": [{"$gte": ["$number_of_employees", 201]},
                                               {"$lte": ["$number_of_employees", 500]}]}, "then": "201-500"},
                            {"case": {"$and": [{"$gte": ["$number_of_employees", 501]},
                                               {"$lte": ["$number_of_employees", 1000]}]}, "then": "501-1000"},
                            {"case": {"$gte": ["$number_of_employees", 1001]}, "then": "1001+"}
                        ],
                        "default": "Unknown"
                    }
                }
            }
        },
        {"$group": {"_id": "$employee_size_category", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]

    employers_by_size = await employer_profile.aggregate(pipeline).to_list(None)
    return employers_by_size


class AnalyticsService:
    @staticmethod
    async def get_candidate_regional_distribution():
        regions_pipeline = [
            {"$unwind": "$criteria.geographical_mobility"},
            {"$group": {"_id": "$criteria.geographical_mobility", "count": {"$sum": 1}}},
        ]

        regions_data = await candidate_profile.aggregate(regions_pipeline).to_list(100)

        return {
            "regional_distribution": regions_data,
        }

    @staticmethod
    async def get_overall_statistics():
        # Total candidates registered
        total_candidates = await candidate_profile.count_documents({})

        # Total Employers registered
        total_employers = await employer_profile.count_documents({})

        # Total Applications submitted
        applications_submitted = await applications.count_documents({})

        # Total Job posts submitted
        job_posts_submitted = await job_posts.count_documents({})

        # Application Status breakdown
        status_breakdown = await applications.aggregate([
            {"$group": {"_id": "$status", "count": {"$sum": 1}}},
        ]).to_list()

        # Top Industries by Job Posts
        top_industries = await job_posts.aggregate([
            {"$group": {"_id": "$job_category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5},
        ]).to_list()

        print(top_industries)

        top_industries = [{doc["_id"]: doc["count"]} for doc in top_industries]

        return {
            "total_candidates": total_candidates,
            "total_employers": total_employers,
            "total_job_posts": job_posts_submitted,
            "applications_submitted": applications_submitted,
            "application_status_breakdown": status_breakdown,
            "top_industries": top_industries,
        }

    @staticmethod
    async def get_candidate_overall_statistics():
        # Total candidates
        total_candidates = await candidate_profile.count_documents({})

        # By experience level
        group_by_experience_level = await candidate_profile.aggregate([
            {"$unwind": "$skills.skill_description"},
            {"$group": {"_id": "$skills.skill_description", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]).to_list()

        # By education level
        group_by_education_level = await candidate_profile.aggregate([
            {"$unwind": "$profile_cv.education"},
            {"$group": {"_id": "$profile_cv.education.degree", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]).to_list()

        # By Geographical mobility/region
        group_by_region = await candidate_profile.aggregate([
            {"$unwind": "$job_criteria.geographical_mobility"},
            {"$group": {"_id": "$job_criteria.geographical_mobility", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]).to_list()

        # By Top Languages known
        top_languages_known = await candidate_profile.aggregate([
            {"$unwind": "$skills.spoken_languages"},
            {"$group": {"_id": "$skills.spoken_languages.language", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]).to_list()

        # Popular job types
        popular_job_types = await candidate_profile.aggregate([
            {"$unwind": "$job_criteria.seeked_jobs"},
            {"$group": {"_id": "$job_criteria.seeked_jobs", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]).to_list()

        return {
            "total_candidates": total_candidates,
            "group_by_experience_level": group_by_experience_level,
            "group_by_education_level": group_by_education_level,
            "group_by_region": group_by_region,
            "top_languages_known": top_languages_known,
            "popular_job_types": popular_job_types,
        }

    @staticmethod
    async def get_employers_overall_statistics():
        # Total number of employers
        total_employers = await employer_profile.count_documents({})

        employers_by_industry = await employer_profile.aggregate([
            {"$unwind": "$company_industry"},
            {"$group": {"_id": "$company_industry", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]).to_list()

        employers_by_size = await get_employers_by_size()

        # geographical_regions of employers
        popular_regions_by_employers = await employer_profile.aggregate([
            {"$group": {"_id": "$city", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]).to_list(None)

        return {
            "total_employers": total_employers,
            "employers_by_industry": employers_by_industry,
            "employers_by_size": employers_by_size,
            "popular_regions_by_employers": popular_regions_by_employers,
        }

    @staticmethod
    async def get_job_posts_overall_statistics():
        total_job_posts = await job_posts.count_documents({})

        # jobs by Education Level required.
        jobs_by_education_level = await job_posts.aggregate([
            {"$group": {"_id": "$education_level_required", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]).to_list(None)

        # jobs by business sector
        jobs_by_business_sector = await job_posts.aggregate([
            {"$group": {"_id": "$sector", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]).to_list(None)

        # Jobs by job_category
        job_by_job_category = await job_posts.aggregate([
            {"$group": {"_id": "$job_type", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]).to_list(None)

        # Jobs by Region
        jobs_by_region = await job_posts.aggregate([
            {"$group": {"_id": "$region", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]).to_list(None)

        # Jobs by experience_level_required
        jobs_by_experience_level_required = await job_posts.aggregate([
            {"$group": {"_id": "$experience_level", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]).to_list(None)

        return {
            "total_job_posts": total_job_posts,
            "jobs_by_education_level_required": jobs_by_education_level,
            "jobs_by_business_sector": jobs_by_business_sector,
            "job_by_job_category": job_by_job_category,
            "jobs_by_region": jobs_by_region,
            "jobs_by_experience_level_required": jobs_by_experience_level_required,
        }

    @staticmethod
    async def get_applications_overall_statistics():
        total_applications = await applications.count_documents({})

        # Group the applications by the status
        applications_by_status_level = await applications.aggregate([
            {"$group": {"_id": "$status", "count": {"$sum": 1}}},
        ]).to_list(None)

        average_applications_per_job_posts = await applications.aggregate([
            {"$lookup": {
                "from": "job_posts",
                "localField": "job_post_id",
                "foreignField": "_id",
                "as": "applications",
            }},
            {
                "$project": {
                    "job_ad_title": 1,
                    "applications_count": {"$size": "$applications"},
                }
            },
            {
                "$group": {
                    "_id": None,
                    "average_applications": {"$avg": "$applications_count"},
                }
            }
        ]).to_list(None)

        top_job_posts_by_applications = await applications.aggregate([
            {"$lookup": {
                "from": "job_posts",
                "localField": "job_post_id",
                "foreignField": "_id",
                "as": "applications",
            }},
            {
                "$project": {
                    "job_ad_title": 1,
                    "applications_count": {"$size": "$applications"},
                }
            },
            {"$sort": {"applications_count": -1}},
            {"$limit": 5}
        ]).to_list(None)

        conversion_rates = objectid_to_str(await applications.aggregate([
            {
                "$group": {
                    "_id": "$status",
                    "count": {"$sum": 1}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "accepted_count": {"$sum": {"$cond": [{"$eq": ["$_id", "Accepted"]}, 1, 0]}},
                    "rejected_count": {"$sum": {"$cond": [{"$eq": ["$_id", "Rejected"]}, 1, 0]}}
                }
            },
            {
                "$project": {
                    "conversion_rate": {
                        "$divide": ["$accepted_count", {"$add": ["$accepted_count", "$rejected_count"]}]
                    }
                }
            }
        ]).to_list(length=None))

        return {
            "total_applications": total_applications,
            "applications_by_status": applications_by_status_level,
        }


