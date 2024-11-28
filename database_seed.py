import json
import random
import string
import uuid
from datetime import datetime, timezone

import names
import pymongo
from faker import Faker
from tqdm import tqdm  # For progress tracking
import logging  # For logging

from core.security import hash_password

# Initialize Faker
fake = Faker()

# Configure logging
logging.basicConfig(
    filename='data_generation.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27018/")
db = client["job_recruitment_system"]

# Collections
users_col = db["users"]
candidate_profiles_col = db["candidate_profiles"]
employer_profiles_col = db["employer_profiles"]
job_posts_col = db["job_posts"]
applications_col = db["applications"]

# Enumerations and Constants
genders = ["Male", "Female"]
roles = ["candidate", "employer"]
seeked_jobs_options = [
    "Accounting, controlling, finance", "Health and social professions", "HR, training",
    "IT, new technologies", "Legal", "Management", "Marketing, communication",
    "Production, maintenance, quality", "Public buildings and works professions",
    "Purchases", "R&D, project management", "Sales", "Secretarial work, assistantship",
    "Services", "Telemarketing, teleassistance", "Tourism, hotel business and catering",
    "Transport, logistics"
]

business_sectors_options = [
    "Advice, audit, accounting", "Aeronautics, naval", "Agriculture, fishing, aquaculture",
    "Airport and shipping services", "Associative activities", "Banking, insurance, finance",
    "Call centers, hotlines", "Chemistry, petrochemistry, raw materials, mining",
    "Cleaning, security, surveillance", "Consumer goods", "Distribution, selling, wholesale",
    "Edition, printing", "Education, training",
    "Electric, electronic, optical and precision equipments",
    "Electricity, water, gas, nuclear, energy", "Engineering, development studies",
    "Environment, recycling", "Event, receptionist", "Food-processing industry",
    "Furnishing, decoration", "Government services", "Greenways, forests, hunting",
    "Handling", "Health, pharmacy, hospitals, medical equipment",
    "Hotel business, catering", "Import-export business",
    "Industry, production, manufacturing and other", "IT, software engineering, Internet",
    "Luxury, cosmetics", "Maintenance, servicing, after-sales services",
    "Marketing, communication, media", "Mechanical equipment, machines",
    "Metallurgy, steel industry", "Motor, transportation equipment, reparation",
    "Paper, wood, rubber, plastic, glass, tobacco", "Pharmaceutical industry",
    "Public buildings and works sector, construction", "Quality, methods",
    "Real-estate, architecture, town planning", "Rental", "Research and development",
    "Secretarial work", "Services other", "Social, public and human services",
    "Sports, cultural and social action", "Telecom", "Temporary work, recruitment",
    "Textile, leather, shoes, clothing industry", "Tourism, leisure activities",
    "Transport, logistics, postal services"
]

geographical_mobility_options = ["Eastern", "Kigali", "Northern", "Southern", "Western", "International"]
desired_contract_types = [
    "Permanent Contract", "Fixed-term contract", "Temporary work", "Internship", "Freelance",
    "Cooperative Education Program", "Part-time work"
]

availability_options = ["Immediately", "In one month", "In two months", "In three months", "In six months",
                        "Not available"]

desired_salary_options = [
    "Under 300,000 FRW", "Between 300,000 FRW and 400,000 FRW",
    "Between 400,000 FRW and 600,000 FRW", "Between 600,000 FRW and 850,000 FRW",
    "Between 850,000 FRW and 1,100,000 FRW", "Between 1,100,000 FRW and 1,300,000 FRW",
    "Between 1,300,000 FRW and 1,600,000 FRW", "Between 1,600,000 FRW and 2,100,000 FRW",
    "Between 2,100,000 FRW and 3,200,000 FRW", "Between 3,200,000 FRW and 4,200,000 FRW",
    "Greater than 4,200,000 FRW"
]

fluency_levels = ["Native", "Fluent", "Good Level", "Intermediate", "Beginner"]
languages = ["English", "French", "Kinyarwanda", "Swahili", "German", "Spanish"]

job_types = desired_contract_types  # Reusing the same contract types for job posts
application_statuses = ["Pending", "Accepted", "Rejected", "Withdrawn"]
experience_levels = ["No experience", "Less than 2 years", "2 to 5 years", "5 to 10 years", "More than 10 years"]
education_levels = ["High school", "Technical school", "College", "HND", "Bachelor", "Master", "Doctorate"]
remote_work_options = ["No", "Yes", "Hybrid"]
team_management_options = ["No", "Yes"]
number_of_positions_options = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 25, 50, 75, 100]
cities = ["Kigali", "Huye", "Musanze", "Rubavu", "Rusizi"]
regions = ["Eastern", "Kigali", "Northern", "Southern", "Western", "International"]
key_skills_examples = ["Sales", "Accounting", "SAP", "Civil Engineering", "Python", "Data Analysis",
                       "Project Management"]

# Parameters for data generation
NUM_CANDIDATES = 100000
NUM_EMPLOYERS = 1000
NUM_JOB_POSTS = 5000
NUM_APPLICATIONS_PER_JOB = 100  # To reach over 500,000 applications
BATCH_SIZE = 1000  # For bulk insert operations


# Helper Functions
def generate_password(length=12):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_timestamp():
    return datetime.now(timezone.utc)


def generate_experience():
    experiences = []
    for _ in range(random.randint(1, 5)):
        start_date = fake.date_between(start_date='-10y', end_date='-1y')
        end_date = fake.date_between(start_date=start_date, end_date='today')
        experiences.append({
            "title": fake.job(),
            "company": fake.company(),
            "start_date": start_date.strftime("%B %Y"),
            "end_date": end_date.strftime("%B %Y") if random.choice([True, False]) else None,
            "description": fake.text(max_nb_chars=200)
        })
    return experiences


def generate_education():
    educations = []
    for _ in range(random.randint(1, 3)):
        start_date = fake.date_between(start_date='-15y', end_date='-5y')
        end_date = fake.date_between(start_date=start_date, end_date='today')
        educations.append({
            "institution": fake.company(),
            "degree": random.choice(education_levels),
            "start_date": start_date.strftime("%B %Y"),
            "end_date": end_date.strftime("%B %Y"),
            "type_of_training": fake.text(max_nb_chars=100)
        })
    return educations


def generate_skills():
    skills = random.sample(key_skills_examples, random.randint(1, 5))
    spoken_languages = []
    for _ in range(random.randint(1, 3)):
        spoken_languages.append({
            "language": random.choice(languages),
            "fluency": random.choice(fluency_levels)
        })
    return skills, spoken_languages


def generate_company_industry():
    return random.sample(business_sectors_options, random.randint(1, 5))


def generate_seeked_jobs():
    return random.sample(seeked_jobs_options, random.randint(1, 4))


def generate_business_sectors():
    return random.sample(business_sectors_options, random.randint(1, 5))


def generate_geographical_mobility():
    return random.sample(geographical_mobility_options, random.randint(1, len(geographical_mobility_options)))


def generate_desired_contract_type():
    return random.sample(desired_contract_types, random.randint(1, len(desired_contract_types)))


def generate_required_skills():
    return random.sample(key_skills_examples, random.randint(1, 5))


def generate_languages_required():
    languages_required = []
    for _ in range(random.randint(1, 3)):
        languages_required.append({
            "language": random.choice(languages),
            "fluency": random.choice(fluency_levels)
        })
    return languages_required


def generate_job_post(employer_id):
    job_ad_title = fake.job()
    number_of_positions = random.choice(number_of_positions_options)
    job_description = fake.text(max_nb_chars=500)
    required_profile_description = fake.text(max_nb_chars=300)
    sector = random.choice(business_sectors_options)
    job_category = random.choice(seeked_jobs_options)
    experience_level = random.choice(experience_levels)
    languages_required = generate_languages_required()
    education_level_required = random.choice(education_levels)
    job_type = random.choice(job_types)
    region = random.choice(regions)
    city = random.choice(cities)
    remote_work = random.choice(remote_work_options)
    team_management = random.choice(team_management_options)
    key_skills = generate_required_skills()
    offered_salary = random.choice(desired_salary_options)
    created_at = generate_timestamp()
    return {
        "employer_id": employer_id,
        "job_ad_title": job_ad_title,
        "number_of_positions": number_of_positions,
        "job_description": job_description,
        "required_profile_description": required_profile_description,
        "sector": sector,
        "job_category": job_category,
        "experience_level": experience_level,
        "languages_required": languages_required,
        "education_level_required": education_level_required,
        "job_type": job_type,
        "region": region,
        "city": city,
        "remote_work": remote_work,
        "team_management": team_management,
        "key_skills": key_skills,
        "offered_salary": offered_salary,
        "created_at": created_at
    }


# Generate Users
users = []
candidate_user_ids = []
employer_user_ids = []
user_passwords = []
employer_passwords = []

print("Generating candidate users...")
candidate_users = []
for _ in tqdm(range(NUM_CANDIDATES)):
    first_name = names.get_first_name()
    last_name = names.get_last_name()
    user = {
        "first_name": first_name,
        "last_name": last_name,
        "gender": random.choice(genders),
        "email": f"{first_name.lower()}.{last_name.lower()}.{uuid.uuid4()}@example.com",
        "password": generate_password(),
        "role": "candidate",
        "created_at": generate_timestamp()
    }
    user_passwords.append({"email": user["email"], "password": user['password']})
    user['password'] = hash_password(user['password'])
    candidate_users.append(user)

    # Bulk insert in batches
    if len(candidate_users) >= BATCH_SIZE:
        try:
            result = users_col.insert_many(candidate_users)
            candidate_user_ids.extend(result.inserted_ids)
            candidate_users = []
        except Exception as e:
            logging.error(f"Error inserting candidate users: {e}")

# Insert any remaining candidate users
if candidate_users:
    try:
        result = users_col.insert_many(candidate_users)
        candidate_user_ids.extend(result.inserted_ids)
    except Exception as e:
        logging.error(f"Error inserting candidate users: {e}")

print("Generating employer users...")
employer_users = []
for _ in tqdm(range(NUM_EMPLOYERS)):
    first_name = names.get_first_name()
    last_name = names.get_last_name()
    user = {
        "first_name": first_name,
        "last_name": last_name,
        "gender": random.choice(genders),
        "email": f"{first_name.lower()}.{last_name.lower()}.{uuid.uuid4()}@example.com",
        "password": generate_password(),
        "role": "employer",
        "created_at": generate_timestamp()
    }
    employer_passwords.append({"email": user["email"], "password": user['password']})
    user['password'] = hash_password(user['password'])
    employer_users.append(user)

    # Bulk insert in batches
    if len(employer_users) >= BATCH_SIZE:
        try:
            result = users_col.insert_many(employer_users)
            employer_user_ids.extend(result.inserted_ids)
            employer_users = []
        except Exception as e:
            logging.error(f"Error inserting employer users: {e}")

# Insert any remaining employer users
if employer_users:
    try:
        result = users_col.insert_many(employer_users)
        employer_user_ids.extend(result.inserted_ids)
    except Exception as e:
        logging.error(f"Error inserting employer users: {e}")

# Generate Candidate Profiles
print("Generating candidate profiles...")
candidate_profiles = []
for candidate_id in tqdm(candidate_user_ids):
    linkedin_url = f"https://www.linkedin.com/in/{uuid.uuid4()}/"
    experiences = generate_experience()
    educations = generate_education()
    picture_url = fake.image_url()
    cv_file = f"https://example.com/cv/{uuid.uuid4()}.pdf"
    skills, spoken_languages = generate_skills()
    profile = {
        "candidate_id": candidate_id,
        "profile_cv": {
            "linkedin_url": linkedin_url,
            "experience": experiences,
            "education": educations,
            "picture_url": picture_url,
            "cv_file": cv_file
        },
        "job_criteria": {
            "seeked_jobs": generate_seeked_jobs(),
            "business_sectors": generate_business_sectors(),
            "geographical_mobility": generate_geographical_mobility(),
            "desired_contract_type": generate_desired_contract_type(),
            "availability": random.choice(availability_options),
            "desired_salary": random.choice(desired_salary_options)
        },
        "skills": {
            "skill_description": skills,
            "spoken_languages": spoken_languages
        },
        "created_at": generate_timestamp()
    }
    candidate_profiles.append(profile)

    # Bulk insert in batches
    if len(candidate_profiles) >= BATCH_SIZE:
        try:
            candidate_profiles_col.insert_many(candidate_profiles)
            candidate_profiles = []
        except Exception as e:
            logging.error(f"Error inserting candidate profiles: {e}")

# Insert any remaining candidate profiles
if candidate_profiles:
    try:
        candidate_profiles_col.insert_many(candidate_profiles)
    except Exception as e:
        logging.error(f"Error inserting candidate profiles: {e}")
# Generate Employer Profiles
print("Generating employer profiles...")
employer_profiles = []
for employer_id in tqdm(employer_user_ids):
    company_name = fake.company()
    address = fake.address()
    zip_code = fake.postcode()
    city = random.choice(cities)
    country = "Rwanda"
    company_industry = generate_company_industry()
    company_description = fake.text(max_nb_chars=200)
    position_in_organization = fake.job()
    number_of_employees = random.randint(10, 1000)
    profile = {
        "employer_id": employer_id,
        "company_name": company_name,
        "address": address,
        "zip_code": zip_code,
        "city": city,
        "country": country,
        "company_industry": company_industry,
        "company_description": company_description,
        "position_in_organization": position_in_organization,
        "number_of_employees": number_of_employees,
        "created_at": generate_timestamp()
    }
    employer_profiles.append(profile)

    # Bulk insert in batches
    if len(employer_profiles) >= BATCH_SIZE:
        try:
            employer_profiles_col.insert_many(employer_profiles)
            employer_profiles = []
        except Exception as e:
            logging.error(f"Error inserting employer profiles: {e}")

# Insert any remaining employer profiles
if employer_profiles:
    try:
        employer_profiles_col.insert_many(employer_profiles)
    except Exception as e:
        logging.error(f"Error inserting employer profiles: {e}")

# Generate Job Posts
job_post_ids = []
print("Generating job posts...")
job_posts = []
for _ in tqdm(range(NUM_JOB_POSTS)):
    employer_id = random.choice(employer_user_ids)
    job_post = generate_job_post(employer_id)
    job_posts.append(job_post)

    # Bulk insert in batches
    if len(job_posts) >= BATCH_SIZE:
        try:
            result = job_posts_col.insert_many(job_posts)
            job_post_ids.extend(result.inserted_ids)
            job_posts = []
        except Exception as e:
            logging.error(f"Error inserting job posts: {e}")

# Insert any remaining job posts
if job_posts:
    try:
        result = job_posts_col.insert_many(job_posts)
        job_post_ids.extend(result.inserted_ids)
    except Exception as e:
        logging.error(f"Error inserting job posts: {e}")

# Generate Applications
print("Generating applications...")
applications = []
total_applications = NUM_JOB_POSTS * NUM_APPLICATIONS_PER_JOB
with tqdm(total=total_applications) as pbar:
    for job_post_id in job_post_ids:
        # Randomly select applicants for each job post
        applicants = random.sample(candidate_user_ids, NUM_APPLICATIONS_PER_JOB)
        for candidate_id in applicants:
            application = {
                "candidate_id": candidate_id,
                "job_post_id": job_post_id,
                "application_date": generate_timestamp(),
                "status": random.choice(application_statuses)
            }
            applications.append(application)
            pbar.update(1)

            # Bulk insert in batches
            if len(applications) >= BATCH_SIZE:
                try:
                    applications_col.insert_many(applications)
                    applications = []
                except Exception as e:
                    logging.error(f"Error inserting applications: {e}")

# Insert any remaining applications
if applications:
    try:
        applications_col.insert_many(applications)
    except Exception as e:
        logging.error(f"Error inserting applications: {e}")

data = {
    "user_passwords": user_passwords,
    "employer_passwords": employer_passwords
}

# Save to JSON file
with open("usernames-passwords.json", 'w') as outfile:
    json.dump(data, outfile, indent=4)

print("Data generation completed successfully.")
