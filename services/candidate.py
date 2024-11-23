from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId
from fastapi import Depends, HTTPException
from pydantic import BaseModel

from core.database import candidate_profile, job_posts, applications
from core.security import get_current_user
from models.application import StatusEnum
from models.candidate import Education, Experience, RegionEnum, ExperienceLevelEnum, DesiredSalaryEnum, Skills, \
    SpokenLanguage
from utils.save_file import save_file
from utils.transform import objectid_to_str


class CandidateBasicInformation(BaseModel):
    education: list[Education]
    experience: list[Experience]
    linkedin: Optional[str]

    def to_dict(self):
        return {
            "education": [
                {
                    "level": e.level.value,  # Convert Enum to string value
                    "from_date": e.from_date,
                    "to_date": e.to_date,
                    "is_present": e.is_present,
                    "type_of_training": e.type_of_training,
                    "institution_name": e.institution_name,
                    "description": e.description
                }
                for e in self.education
            ],
            "experience": [
                {
                    "from_date": e.from_date,
                    "to_date": e.to_date,
                    "is_present": e.is_present,
                    "position": e.position,
                    "company_name": e.company_name,
                    "description": e.description
                }
                for e in self.experience
            ],
            "linkedin": self.linkedin
        }


class CandidateService:
    @staticmethod
    async def get_user_profile(current_user=Depends(get_current_user)):
        try:
            if not current_user or '_id' not in current_user:
                raise HTTPException(status_code=401, detail="Unauthorized: Invalid credentials")

            candidate_information = await candidate_profile.find_one({"candidate_id": (current_user['_id'])})

            if not candidate_information:
                raise HTTPException(status_code=404, detail="Candidate not found")

            return {
                "message": "Candidate Profile retrieved successfully",
                "candidate_profile": {
                    # todo :: returning the profile_photo and also cv_file to the end user.
                    "profile_cv": candidate_information.get("profile_cv", {}),
                    "criteria": candidate_information.get("criteria", {}),
                    "skills": candidate_information.get("skills", {}),
                    "created_at": candidate_information.get("created_at").isoformat() if candidate_information.get(
                        "created_at") else None,
                }
            }
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500,
                                detail='Please wait as we solve the error as it is happening on our end.')

    @staticmethod
    async def upload_user_basic_files(profile_pic, cv_file, current_user):
        candidate_id = current_user["_id"]

        # Validate the input to our function
        if not profile_pic or not cv_file:
            raise HTTPException(status_code=404, detail="Both profile picture and cv_file is needed.")

        profile_pic_url = save_file(profile_pic, str(candidate_id), "profile_pic")
        cv_file_url = save_file(cv_file, str(candidate_id), "cv_file")

        candidate_info = await candidate_profile.find_one({"candidate_id": candidate_id})
        if not candidate_info:
            raise HTTPException(status_code=404, detail="Candidate was not found.")

        candidate_info.get("profile_cv", {
            "picture": None,
            "cv_file": None,
            "experience": [Experience],
            "education": [Education],
            "linkedin": None
        })

        updated_candidate_info = {
            "picture": profile_pic_url or candidate_info.get("profile_cv"),
            "cv_file": cv_file_url or candidate_info.get("cv_file"),
            "experience": candidate_info.get("experience"),
            "education": candidate_info.get("education"),
            "linkedin": candidate_info.get("linkedin")
        }

        # update the data
        result = await candidate_profile.update_one(
            {"candidate_id": candidate_id},
            {"$set": {"profile_cv": updated_candidate_info}}
        )

        # Check the result of the  operation
        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="Candidate profile pic/cv files were not updated")

        return {
            "message": "The files were uploaded successfully",
            "profile_picture_url": profile_pic_url,
            "cv_file_url": cv_file_url,
        }

    @staticmethod
    async def update_candidate_profile(current_user, candidate_basic_info):
        try:
            # Fetch candidate_id from current_user
            candidate_id = current_user['_id']

            # Attempt to find the existing profile in the database
            existing_profile = await candidate_profile.find_one({"candidate_id": candidate_id})

            # If no profile is found, raise HTTPException
            if not existing_profile:
                raise HTTPException(status_code=404, detail="Candidate not found")

            # Extract current profile_cv or provide default values
            profile_cv = existing_profile.get("profile_cv", {
                "picture": None,
                "cv_file": None,
                "experience": [],
                "education": [],
                "linkedin": None
            })

            # Prepare the updated data
            candidate_update_info = candidate_basic_info.model_dump()

            # Debug log
            updated_data = {
                "linkedin": candidate_update_info["linkedin"] or profile_cv["linkedin"],
                "experience": candidate_update_info["experience"] or profile_cv["experience"],
                "education": candidate_update_info["education"] or profile_cv["education"],
                "picture": profile_cv["picture"],
                "cv_file": profile_cv["cv_file"]
            }

            # Perform the update in the database
            result = await candidate_profile.update_one(
                {"candidate_id": candidate_id},
                {"$set": {"profile_cv": updated_data}},
            )

            # Check if the update was successful
            if result.modified_count == 0:
                raise HTTPException(status_code=500, detail="Failed to update candidate background.")

            # Return the success response
            return {
                "message": "Profile CV updated successfully",
                "profile_information": {
                    "education_background": updated_data.get("education"),
                    "experience_background": updated_data.get("experience"),
                    "linkedin_url": updated_data.get("linkedin"),
                }
            }
        except Exception as e:
            # Catch any other unexpected exceptions
            raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

    @staticmethod
    async def update_job_criteria_info(current_user, job_criteria_info):
        # Fetch the existing candidate from the DB using candidate_id
        existing_candidate = await candidate_profile.find_one({"candidate_id": current_user['_id']})

        if not existing_candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")

        # Fetch the job_criteria section from the DB
        job_criteria_from_db = existing_candidate.get("job_criteria", {
            "seeked_jobs": [],
            "business_sectors": [],
            "geographical_mobility": [RegionEnum.KIGALI.value],
            "desired_contract_type": None,
            "desired_salary": None
        })

        job_criteria_info = job_criteria_info.model_dump()

        # Prepare the updated data
        updated_job_criteria = {
            "seeked_jobs": job_criteria_info.get("seeked_jobs", job_criteria_from_db["seeked_jobs"]),
            "business_sectors": job_criteria_info.get("business_sectors", job_criteria_from_db["business_sectors"]),
            "geographical_mobility": job_criteria_info.get("geographical_mobility",
                                                           job_criteria_from_db["geographical_mobility"]),
            "desired_contract_type": job_criteria_info.get("desired_contract_type",
                                                           job_criteria_from_db["desired_contract_type"]),
            "desired_salary": job_criteria_info.get("desired_salary", job_criteria_from_db["desired_salary"]),
        }

        # Perform the update in the database
        result = await candidate_profile.update_one(
            {"candidate_id": current_user['_id']},  # Query filter
            {"$set": {"criteria": updated_job_criteria}}  # Update operation
        )

        # Check if any document was modified
        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Failed to update candidate background.")

        return {
            "message": "Candidate job criteria updated successfully"
        }

    @staticmethod
    async def update_skills_info(current_user, skills_info: Skills):
        # Fetch the existing candidate from the DB using candidate_id
        existing_candidate = await candidate_profile.find_one({"candidate_id": current_user['_id']})

        if not existing_candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")

        skills_from_db = existing_candidate.get("skills", {
            "skill_description": "",
            "spoken_languages": [],
            "expertise": ""
        })

        # Serialize spoken languages and fluency levels to dictionaries or simple types
        def serialize_spoken_languages(spoken_languages):
            serialized_languages = []
            for language in spoken_languages:
                if isinstance(language, SpokenLanguage):  # If it's an instance of SpokenLanguage
                    # Convert FluentLevelEnum to string or a simple representation
                    serialized_language = {
                        "language": language.language,
                        "fluency": language.fluency.value  # or language.fluency.name if you prefer the string name
                    }
                    serialized_languages.append(serialized_language)
                else:
                    # Handle cases where the language is already in the expected format
                    serialized_languages.append(language)
            return serialized_languages

        # Prepare the updated data
        updated_skills = {
            "skill_description": skills_info.skill_description or skills_from_db["skill_description"],
            "spoken_languages": serialize_spoken_languages(skills_info.spoken_languages) or skills_from_db[
                "spoken_languages"],
            "expertise": skills_info.expertise or skills_from_db["expertise"],
        }

        # Perform the update in the database
        result = await candidate_profile.update_one(
            {"candidate_id": current_user['_id']},  # Query filter
            {"$set": {"skills": updated_skills}}  # Update operation
        )

        # Check the update result
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Candidate not found for update")
        elif result.modified_count == 0:
            return {"message": "No changes were made as the data is identical"}

        return {
            "message": "Candidate skills section updated successfully"
        }

    @staticmethod
    async def get_jobs_posted(page: int,
                              limit: int,
                              region: Optional[RegionEnum],
                              city: Optional[str],
                              experience_level: Optional[ExperienceLevelEnum],
                              job_ad_title: Optional[str],
                              offered_salary: Optional[DesiredSalaryEnum],
                              ):

        search_query = {}

        if region:
            search_query["region"] = region.value
        if city:
            search_query["city"] = city
        if experience_level:
            search_query["experience_level"] = experience_level.value
        if job_ad_title:
            search_query["job_ad_title"] = job_ad_title
        if offered_salary:
            search_query["offered_salary"] = offered_salary.value

        skip = (page - 1) * limit

        jobs_cursor = job_posts.find(search_query).skip(skip).limit(limit)
        jobs_posted = objectid_to_str(await jobs_cursor.to_list(length=limit))

        total_jobs = await job_posts.count_documents(search_query)

        return {
            "page": page,
            "limit": limit,
            "total_jobs": total_jobs,
            "jobs": jobs_posted,
        }

        jobs_posted = objectid_to_str(await job_posts.find().to_list(1000))
        return jobs_posted

    @staticmethod
    async def get_job_post(job_id):
        try:
            job_post = await job_posts.find_one({"_id": ObjectId(job_id)})
            return objectid_to_str(job_post)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @staticmethod
    async def apply_for_job_post(job_id, current_user):
        # Check for the existence of the job_post
        # Check if the user has already applied for the job
        # Insert the application in the collection

        # todo:: Adding validation and handling error responses.

        candidate_id = current_user['_id']

        job_post = await job_posts.find_one({"_id": ObjectId(job_id)})
        if not job_post:
            raise HTTPException(status_code=404, detail="JobPost not found")

        existing_application = await applications.find_one({
            "job_id": ObjectId(job_id),
            "candidate_id": ObjectId(candidate_id)
        })

        if existing_application:
            raise HTTPException(status_code=400, detail="You have already applied for this job")

        application_data = {
            "job_id": ObjectId(job_id),
            "candidate_id": candidate_id,
            "status": StatusEnum.PENDING.value,
            "created_at": datetime.now(timezone.utc),
        }

        result = await applications.insert_one(application_data)

        return {
            "application_id": str(result.inserted_id),
            "message": "Job Post submitted successfully",
            "status": application_data["status"],
            "created_at": application_data["created_at"],
        }

    @staticmethod
    async def get_applications(page: int, limit: int, job_ad_title: Optional[str], current_user):

        candidate_id = current_user["_id"]

        # Pagination parameters
        skip = (page - 1) * limit

        # Match candidate ID and filter by job_ad_title if provided
        match_stage = {"$match": {"candidate_id": candidate_id}}
        if job_ad_title:
            match_stage["$match"]["job_details.job_ad_title"] = {"$regex": job_ad_title,
                                                                 "$options": "i"}  # Case-insensitive

        pipeline = [
            match_stage,

            # Lookup job details from job_posts
            {
                "$lookup": {
                    "from": "job_posts",
                    "localField": "job_id",
                    "foreignField": "_id",
                    "as": "job_details",
                }
            },
            {"$unwind": "$job_details"},

            # Lookup employer profile details
            {
                "$lookup": {
                    "from": "employer_profiles",
                    "localField": "job_details.employer_id",
                    "foreignField": "employer_id",
                    "as": "employer_details"
                }
            },
            {"$unwind": "$employer_details"},

            # Project required fields
            {
                "$project": {
                    "_id": 1,
                    "job_id": "$job_details._id",
                    "status": 1,
                    "created_at": 1,
                    "job_ad_title": "$job_details.job_ad_title",
                    "company_name": "$employer_details.company_name",
                    "company_address": "$employer_details.address",
                    "company_city": "$employer_details.city",
                    "company_country": "$employer_details.country",
                    "industry": "$employer_details.company_industry"
                }
            },

            # Pagination
            {"$skip": skip},
            {"$limit": limit}
        ]

        # Fetch total count for pagination metadata
        total_count_pipeline = [
            match_stage,
            {"$count": "total_count"}
        ]
        total_count_result = await applications.aggregate(total_count_pipeline).to_list(1)
        total_count = total_count_result[0]["total_count"] if total_count_result else 0

        # Fetch paginated data
        applications_for_user = objectid_to_str(await applications.aggregate(pipeline).to_list(limit))

        return {
            "page": page,
            "limit": limit,
            "total_count": total_count,
            "applications": applications_for_user,
        }

    @staticmethod
    async def withdraw_application(application_id: str, current_user):
        candidate_id = current_user["_id"]

        # Get the application by  application_id and also candidate_id
        user_application = await applications.find_one({"candidate_id": candidate_id, "_id": ObjectId(application_id)})
        if not user_application:
            raise HTTPException(status_code=404, detail="Your application was not found.")

        # Validate the current status
        current_status = user_application.get("status")

        if current_status == 'Approved':
            raise HTTPException(status_code=400, detail="Your application was already approved my dear.")

        if current_status == 'Withdrawn':
            raise HTTPException(status_code=400,
                                detail="Your withdrawn your application already and the action is irreversible.")

        await applications.update_one(
            {"candidate_id": candidate_id},
            {"$set": {"status": StatusEnum.WITHDRAWN.value}},
        )

        return {"message": "Your application has been withdrawn successfully."}
