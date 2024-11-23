from datetime import datetime, timezone
from typing import Optional, List

from bson import ObjectId
from fastapi import Depends, HTTPException
from pydantic import BaseModel
from python_multipart.multipart import Field

from core.database import job_posts, applications, employer_profile, candidate_profile
from core.security import check_employer_role
from models.application import StatusEnum
from models.employer import IndustryEnum, NumberOfEmployeesEnum
from models.job_post import JobPost
from utils.transform import objectid_to_str


class UpdateEmployerProfile(BaseModel):
    company_name: Optional[str] = Field(None)
    address: Optional[str] = Field(None)
    zip_code: Optional[str] = Field(None)
    country: Optional[str] = Field(None)
    city: Optional[str] = Field(None)
    number_of_employees: Optional[NumberOfEmployeesEnum] = Field(None)
    company_industry: Optional[List[IndustryEnum]] = Field(None)
    company_description: Optional[str] = Field(None)
    position_in_organization: Optional[str] = Field(None)


class EmployerService:

    @staticmethod
    async def get_profile(current_user):
        employer_id = current_user['_id']

        employer_information = objectid_to_str(await employer_profile.find_one({'employer_id': employer_id}))

        return employer_information

    @staticmethod
    async def update_profile(updated_profile: UpdateEmployerProfile, current_user):
        employer_id = current_user['_id']

        updated_data = updated_profile.model_dump(exclude_unset=True)
        result = await employer_profile.update_one(
            {'employer_id': employer_id},
            {'$set': updated_data},
        )

        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail='Employer profile not found.')

        updated_info = objectid_to_str(await employer_profile.find_one({'employer_id': employer_id}))
        if updated_info:
            updated_info.pop("_id", None)
        return updated_info

    @staticmethod
    async def create_job_post(job_post: JobPost, current_user=Depends(check_employer_role)):
        employer_id = current_user['_id']

        job_post_data = job_post.model_dump()

        job_post_data['employer_id'] = employer_id
        job_post_data['created_at'] = datetime.now(timezone.utc)

        result = await job_posts.insert_one(job_post_data)

        job_post_response = {
            "job_ad_title": job_post_data["job_ad_title"],
            "number_of_positions": job_post_data["number_of_positions"],
            "offered_salary": job_post_data["offered_salary"],
            "job_description": job_post_data["job_description"],
            "sector": job_post_data["sector"],
            "job_category": job_post_data["job_category"],
            "created_at": job_post_data.get("created_at", None)  # Optional field
        }

        return job_post_response

    @staticmethod
    async def get_job_posts(page: int, limit: int, job_title: str, current_user):
        employer_id = current_user['_id']

        skip = (page - 1) * limit
        # Build the query you are using to find the filter the data from db.
        query = {'employer_id': employer_id}
        if job_title:
            # To  mean I am adding the property of regex which will case-insensitive.
            query['job_title'] = {"$regex": job_title, "$options": "i"}

        # Fetch the paginated data
        job_posts_info = await job_posts.find(query).skip(skip).limit(limit).to_list(limit)

        # Count the total number of documents matching the query
        total_count = await job_posts.count_documents(query)

        job_posts_raw = objectid_to_str(job_posts_info)

        return {
            "data": job_posts_raw,
            "pagination": {
                "page": page,
                "page_size": limit,
                "total_count": total_count,
                "total_pages": (total_count + limit - 1) // limit,
            }
        }

    @staticmethod
    async def get_applications(job_id: str, status: StatusEnum, current_user):
        employer_id = current_user['_id']

        pipeline = [
            {"$match": {"job_id": ObjectId(job_id)}},

            {"$match": {"status": status}},

            {
                "$lookup": {
                    "from": "job_posts",
                    "localField": "job_id",
                    "foreignField": "_id",
                    "as": "job_details",
                }
            },
            {"$unwind": "$job_details"},
            {"$match": {"job_details.employer_id": employer_id}},

            {
                "$lookup": {
                    "from": "users",
                    "localField": "candidate_id",
                    "foreignField": "_id",
                    "as": "candidate_details",
                }
            },
            {"$unwind": "$candidate_details"},

            {
                "$lookup": {
                    "from": "candidate_profiles",
                    "localField": "candidate_id",
                    "foreignField": "candidate_id",
                    "as": "candidate_profile",
                }
            },
            {"$unwind": "$candidate_profile"},

            {
                "$project": {
                    "_id": 1,
                    "job_id": 1,
                    "status": 1,
                    "created_at": 1,
                    "candidate_id": "$candidate_details._id",
                    "first_name": "$candidate_details.first_name",
                    "last_name": "$candidate_details.last_name",
                    "email": "$candidate_details.email",
                    "candidate_profile": {
                        "profile_cv": "$candidate_profile.profile_cv",
                        "skills": "$candidate_profile.skills",
                        "criteria": "$candidate_profile.criteria",
                        "created_at": "$candidate_profile.created_at"
                    }
                }
            }
        ]

        summary_for_employer = objectid_to_str(await applications.aggregate(pipeline).to_list(100))
        return summary_for_employer

    @staticmethod
    async def get_user_application(job_id: str, application_id: str, current_user):
        employer_id = current_user['_id']

        # Make sure the job being retrieved is for the current_user
        job_post = await job_posts.find_one({"_id": ObjectId(job_id)})

        if job_post.get('employer_id') != employer_id:
            raise HTTPException(status_code=400, detail="You are not allowed to view the other jobs details")

        # Fetch the user application
        user_application = await applications.find_one({"_id": ObjectId(application_id), "job_id": ObjectId(job_id)})

        if not user_application:
            raise HTTPException(status_code=404, detail="Application not found my dear.")

        # Fetch the candidate Details
        candidate_id = user_application["candidate_id"]
        if not candidate_id:
            raise HTTPException(status_code=404, detail="Candidate Details not found my dear.")

        candidate_information = await candidate_profile.find_one({"candidate_id": candidate_id})
        if not candidate_information:
            raise HTTPException(status_code=404, detail="Candidate Details not found my dear.")

        response = {
            "candidate_details": {
                "candidate_id": str(candidate_id),
                "user_basic_profile": candidate_information.get("profile_cv", {}),
            }
        }

        return response

    @staticmethod
    async def approve_user_application(job_id: str, application_id: str, current_user):
        employer_id = current_user['_id']

        # make sure the job was posted by current employer
        job_post = await job_posts.find_one({"_id": ObjectId(job_id)})
        if not job_post or job_post.get('employer_id') != employer_id:
            raise HTTPException(status_code=403,
                                detail="You are not allowed to modify applications of the jobs you don't own.")

        # Fetch the application status
        application = await applications.find_one({"_id": ObjectId(application_id)})

        if not application:
            raise HTTPException(status_code=404, detail="Application not found my dear.")

        # First see if the application was pending and update it and if approved leave it or withdrawn
        current_status = application.get("status")

        if current_status == 'Approved':
            raise HTTPException(status_code=400, detail="This application is already approved.")

        if current_status == 'Withdrawn':
            raise HTTPException(status_code=400,
                                detail="This application has been withdrawn by the candidate and can't be approved.")

        # Update the application as required
        await applications.update_one(
            {"_id": ObjectId(application_id)},
            {"$set": {"status": "Approved", "updated_at": datetime.now(timezone.utc)}},
        )

        return {"message": "Application approved successfully"}
