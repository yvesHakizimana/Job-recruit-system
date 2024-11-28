import motor.motor_asyncio

from core.config import settings

client = motor.motor_asyncio.AsyncIOMotorClient(settings.db_url)
db = client.get_database('job_recruitment_system')
user_collection = db.get_collection('users')
candidate_profile = db.get_collection('candidate_profiles')
employer_profile = db.get_collection('employer_profiles')
job_posts = db.get_collection("job_posts")
applications = db.get_collection("applications")


