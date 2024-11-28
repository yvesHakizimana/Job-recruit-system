# Enums for predefined choices
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel


# Education Level Enum
class EducationLevelEnum(str, Enum):
    HIGH_SCHOOL = 'High School'
    TECHNICAL_SCHOOL = 'Technical School'
    COLLEGE = 'College'
    HND = 'HND'
    BACHELOR = 'Bachelor'
    MASTER = 'Master'
    DOCTORATE = 'Doctorate'


# Experience Level Enum
class ExperienceLevelEnum(str, Enum):
    NO_EXPERIENCE = 'No Experience'
    LESS_THAN_TWO_YEARS = 'Less than two years'
    TWO_TO_FIVE_YEARS = "2 to 5 years"
    FIVE_TO_TEN_YEARS = "5 to 10 years"
    MORE_THAN_TEN_YEARS = "More than 10 years"


# Availability Enum
class AvailabilityLevelEnum(str, Enum):
    IMMEDIATELY = "Immediately"
    IN_1_MONTH = "In 1 month"
    IN_2_MONTHS = "In 2 months"
    IN_3_MONTHS = "In 3 months"
    IN_6_MONTHS = "In 6 months"
    NOT_AVAILABLE = "Not available"


# Contract Type Enum
class ContractTypeEnum(str, Enum):
    PERMANENT = "Permanent contract"
    FIXED_TERM = "Fixed-term contract"
    TEMPORARY = "Temporary work"
    INTERNSHIP = "Internship"
    FREELANCE = "Freelance"
    COOPERATIVE = "Cooperative education program"
    PART_TIME = "Part-time work"


# Enum for regions
class RegionEnum(str, Enum):
    EASTERN = "Eastern"
    WESTERN = "Western"
    NORTHERN = "Northern"
    SOUTHERN = "Southern"
    INTERNATIONAL = "International"
    KIGALI = 'Kigali'


# Enum for Desired Salary Ranges
class DesiredSalaryEnum(str, Enum):
    UNDER_300K = "Under 300,000 FRW"
    BETWEEN_300K_400K = "Between 300,000 FRW and 400,000 FRW"
    BETWEEN_400K_600K = "Between 400,000 FRW and 600,000 FRW"
    BETWEEN_850K_1_1M = "Between 850,000 FRW and 1,100,000 FRW"
    BETWEEN_1_1M_1_3M = "Between 1,100,000 FRW and 1,300,000 FRW"
    BETWEEN_1_3M_1_6M = "Between 1,300,000 FRW and 1,600,000 FRW"
    BETWEEN_1_6M_2_1M = "Between 1,600,000 FRW and 2,100,000 FRW"
    BETWEEN_2_1M_3_2M = "Between 2,100,000 FRW and 3,200,000 FRW"
    BETWEEN_3_2M_4_2M = "Between 3,200,000 FRW and 4,200,000 FRW"


# Enum for Fluency Levels
class FluencyLevelEnum(str, Enum):
    NATIVE = "Native"
    FLUENT = "Fluent"
    GOOD_LEVEL = "Good Level"
    INTERMEDIATE = "Intermediate"
    BEGINNER = "Beginner"


# Sub Models
class SpokenLanguage(BaseModel):
    language: str
    fluency: FluencyLevelEnum

    def to_dict(self):
        return {"language": self.language, "fluency": self.fluency.value}


class Education(BaseModel):
    level: EducationLevelEnum
    from_date: Optional[str] # like i will want month and year
    to_date: Optional[str] # like i will want month and year
    is_present: Optional[bool] = False
    type_of_training: Optional[str]
    institution_name: Optional[str]
    description: Optional[str]

    # @validator("from_date", "to_date", pre=True)
    # def validate_date_format(cls, value):
    #     if value:
    #         try:
    #             datetime.strptime(value, "%Y-%m-%d")
    #         except ValueError:
    #             raise ValueError("Date must be in the format YYYY-MM-DD")

    # class Config:
    #     json_encoders= {
    #         date: lambda v: v.isoformat() if v else None,
    #     }


class Experience(BaseModel):
    from_date: Optional[str]
    to_date: Optional[str]
    is_present: Optional[bool]
    position: Optional[str]
    company_name: Optional[str]
    description: Optional[str]

    # @validator("from_date", "to_date")
    # def validate_date_format(cls, value):
    #     if value:
    #         try:
    #             datetime.strptime(value, "%Y-%m-%d")
    #         except ValueError:
    #             raise ValueError("Date must be in the format YYYY-MM-DD")

    # class Config:
    #     json_encoders = {
    #         date: lambda v: v.isoformat() if v else None,
    #     }


class JobCriteria(BaseModel):
    seeked_jobs: List[str]
    business_sectors: List[str]
    availability: List[AvailabilityLevelEnum]
    geographical_mobility: List[RegionEnum]
    desired_contract_type: Optional[ContractTypeEnum]
    desired_salary: Optional[DesiredSalaryEnum]


class Skills(BaseModel):
    skill_description: Optional[str] = None
    spoken_languages: List[SpokenLanguage] = []
    expertise: Optional[str] = None


class CandidateBasicInfo(BaseModel):
    experience: List[Experience] = []
    education: List[Education] = []
    linkedin: Optional[str] = None


class ProfileCV(BaseModel):
    picture: Optional[str]
    cv_file: Optional[str]
    experience: List[Experience]
    education: List[Education]
    linkedin: Optional[str]


class CandidateProfile(BaseModel):
    profile_cv: ProfileCV
    criteria: List[JobCriteria]
    skills: Skills
    created_at: Optional[datetime] = datetime.now(timezone.utc)
