from enum import Enum
from typing import List, Optional

from pydantic import BaseModel

from models.candidate import ExperienceLevelEnum, EducationLevelEnum, SpokenLanguage, ContractTypeEnum, RegionEnum, \
    DesiredSalaryEnum
from models.employer import IndustryEnum


# Enum for Remote Work
class RemoteWorkEnum(str, Enum):
    NO = "No"
    YES = "Yes"
    HYBRID = "Hybrid"


# Enum for Team Management
class TeamManagementEnum(str, Enum):
    YES = "Yes"
    NO = "No"


class JobPost(BaseModel):
    job_ad_title: str
    number_of_positions: int
    job_description: str
    required_profile_description: str
    sector: IndustryEnum  # You could also make this an Enum if there's a predefined set of sectors.
    job_category: str
    experience_level: ExperienceLevelEnum
    languages_required: List[SpokenLanguage]  # List of languages required for the job
    education_level_required: EducationLevelEnum
    job_type: ContractTypeEnum
    region: RegionEnum
    city: Optional[str] = None  # Optional if it's city-based, else you could remove this.
    remote_work: RemoteWorkEnum
    team_management: TeamManagementEnum
    key_skills: List[str]  # List of key skills for the job
    offered_salary: DesiredSalaryEnum
