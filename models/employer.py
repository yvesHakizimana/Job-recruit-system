# Enum for number of employees
from enum import Enum
from typing import List
from pydantic import BaseModel


# Enum for the number of employees.
class NumberOfEmployeesEnum(str, Enum):
    ONE_TO_TEN = "1-10"
    ELEVEN_TO_FIFTY = "11-50"
    FIFTY_ONE_TO_HUNDRED = "51-100"
    ONE_HUNDRED_ONE_TO_FIVE_HUNDRED = "101-500"
    FIVE_HUNDRED_ONE_TO_ONE_THOUSAND = "501-1000"
    ONE_THOUSAND_PLUS = "1000+"


# Enum for industry representation
class IndustryEnum(str, Enum):
    ADVICE_AUDIT_ACCOUNTING = "Advice, audit, accounting"
    AERONAUTICS_NAVAL = "Aeronautics, naval"
    AGRICULTURE_FISHING_AQUACULTURE = "Agriculture, fishing, aquaculture"
    AIRPORT_SHIPPING_SERVICES = "Airport and shipping services"
    ASSOCIATIVE_ACTIVITIES = "Associative activities"
    BANKING_INSURANCE_FINANCE = "Banking, insurance, finance"
    CALL_CENTERS_HOTLINES = "Call centers, hotlines"
    CHEMISTRY_PETROCHEMISTRY_RAW_MATERIALS_MINING = "Chemistry, petrochemistry, raw materials, mining"
    CLEANING_SECURITY_SURVEILLANCE = "Cleaning, security, surveillance"
    CONSUMER_GOODS = "Consumer goods"
    DISTRIBUTION_SELLING_WHOLESALE = "Distribution, selling, wholesale"
    EDITION_PRINTING = "Edition, printing"
    EDUCATION_TRAINING = "Education, training"
    ELECTRIC_ELECTRONIC_OPTICAL_PRECISION_EQUIPMENTS = "Electric, electronic, optical and precision equipments"
    ELECTRICITY_WATER_GAS_NUCLEAR_ENERGY = "Electricity, water, gas, nuclear, energy"
    ENGINEERING_DEVELOPMENT_STUDIES = "Engineering, development studies"
    ENVIRONMENT_RECYCLING = "Environment, recycling"
    EVENT_RECEPTIONIST = "Event, receptionist"
    FOOD_PROCESSING_INDUSTRY = "Food-processing industry"
    FURNISHING_DECORATION = "Furnishing, decoration"
    GOVERNMENT_SERVICES = "Government services"
    GREENWAYS_FORESTS_HUNTING = "Greenways, forests, hunting"
    HANDLING = "Handling"
    HEALTH_PHARMACY_HOSPITALS_MEDICAL_EQUIPMENT = "Health, pharmacy, hospitals, medical equipment"
    HOTEL_BUSINESS_CATERING = "Hotel business, catering"
    IMPORT_EXPORT_BUSINESS = "Import-export business"
    INDUSTRY_PRODUCTION_MANUFACTURING_OTHER = "Industry, production, manufacturing and other"
    IT_SOFTWARE_ENGINEERING_INTERNET = "IT, software engineering, Internet"
    LUXURY_COSMETICS = "Luxury, cosmetics"
    MAINTENANCE_SERVICING_AFTER_SALES_SERVICES = "Maintenance, servicing, after-sales services"
    MARKETING_COMMUNICATION_MEDIA = "Marketing, communication, media"
    MECHANICAL_EQUIPMENT_MACHINES = "Mechanical equipment, machines"
    METALLURGY_STEEL_INDUSTRY = "Metallurgy, steel industry"
    MOTOR_TRANSPORTATION_EQUIPMENT_REPARATION = "Motor, transportation equipment, reparation"
    PAPER_WOOD_RUBBER_PLASTIC_GLASS_TOBACCO = "Paper, wood, rubber, plastic, glass, tobacco"
    PHARMACEUTICAL_INDUSTRY = "Pharmaceutical industry"
    PUBLIC_BUILDINGS_WORKS_SECTOR_CONSTRUCTION = "Public buildings and works sector, construction"
    QUALITY_METHODS = "Quality, methods"
    REAL_ESTATE_ARCHITECTURE_TOWN_PLANNING = "Real-estate, architecture, town planning"
    RENTAL = "Rental"
    RESEARCH_DEVELOPMENT = "Research and development"
    SECRETARIAL_WORK = "Secretarial work"
    SERVICES_OTHER = "Services other"
    SOCIAL_PUBLIC_HUMAN_SERVICES = "Social, public and human services"
    SPORTS_CULTURAL_SOCIAL_ACTION = "Sports, cultural and social action"
    TELECOM = "Telecom"
    TEMPORARY_WORK_RECRUITMENT = "Temporary work, recruitment"
    TEXTILE_LEATHER_SHOES_CLOTHING_INDUSTRY = "Textile, leather, shoes, clothing industry"
    TOURISM_LEISURE_ACTIVITIES = "Tourism, leisure activities"
    TRANSPORT_LOGISTICS_POSTAL_SERVICES = "Transport, logistics, postal services"


class CreateEmployer(BaseModel):
    company_name: str
    address: str
    zip_code: str
    city: str
    country: str
    company_industry: List[IndustryEnum]
    number_of_employees: NumberOfEmployeesEnum
    company_description: str
    position_in_organization: str
