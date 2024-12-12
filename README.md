# Job Recruitment System

## Table of Contents
1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Project Structure](#project-structure)
4. [Installation and Setup](#installation-and-setup)
5. [Environment Variables](#environment-variables)
6. [Usage Instructions](#usage-instructions)
7. [API Endpoints](#api-endpoints)
8. [Project Modules](#project-modules)
9. [Security](#security)
10. [Troubleshooting](#troubleshooting)

---

## Project Overview
The **Job Recruitment System** is a FastAPI-based application that facilitates the hiring process for employers and job searching for candidates. It integrates with a MongoDB database to store user profiles, job postings, and application data. The system supports role-based access for candidates and employers, providing tailored views and actions for each role.

---

## Features
- **User Authentication**: Secure login and registration using JWT tokens.
- **Role-based Access**: Separate views and permissions for candidates and employers.
- **Candidate Profiles**: Create and update profiles with skills, job criteria, and uploaded documents.
- **Employer Profiles**: Employers can create, update, and view job postings.
- **Job Applications**: Candidates can apply for jobs and view their application status.
- **Analytics and Insights**: Provides detailed insights on candidates, employers, and job applications.

---

## Project Structure
```
project-root/
  ├── core/
  │     ├── config.py     # Application configurations
  │     ├── database.py   # Database connection to MongoDB
  │     └── security.py   # Security logic (JWT, password hashing, etc.)
  │
  ├── models/            # Pydantic models for request/response validation
  │     ├── application.py
  │     ├── candidate.py
  │     ├── employer.py
  │     ├── job_post.py
  │     └── user.py
  │
  ├── services/          # Business logic for core functionalities
  │
  ├── uploads/           # File handling logic for candidate uploads (e.g., CVs)
  │
  ├── utils/             # Utility functions used across the application
  │
  ├── .env               # Environment variables for local development
  └── database_seed.py   # Script to seed the database with initial data
```

---

## Installation and Setup

1. **Clone the Repository**:
    ```bash
    git clone <repository-url>
    cd job-recruitment-system
    ```

2. **Create Virtual Environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate   # On Windows: .\venv\Scripts\activate
    ```

3. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Set Environment Variables**:
    Create a `.env` file in the project root and set the following variables:
    ```env
    db_url=<your-mongodb-url>
    secret_key=<your-secret-key>
    algorithm=HS256
    access_token_expire_minutes=30
    ```

5. **Run the Application**:
    ```bash
    uvicorn main:app --reload
    ```

6. **Access the Application**:
    Visit `http://127.0.0.1:8000/docs` for interactive API documentation.

---

## Environment Variables
| Variable                | Description                      |
|------------------------|----------------------------------|
| `db_url`                | MongoDB connection string         |
| `secret_key`            | Secret key for JWT encryption     |
| `algorithm`             | Algorithm for JWT encryption     |
| `access_token_expire_minutes` | Expiration time for access tokens |

---

## Usage Instructions
- **Register as Candidate**: Call `/auth/register/candidate` with the candidate's information.
- **Register as Employer**: Call `/auth/register/employer` with the employer's information.
- **Login**: Use `/auth/login` with valid credentials to get an access token.
- **Access Protected Routes**: Include the JWT token in the `Authorization: Bearer <token>` header.

---

## API Endpoints
### Authentication Endpoints
- `POST /auth/register/candidate`: Register a candidate.
- `POST /auth/register/employer`: Register an employer.
- `POST /auth/login`: Login to obtain a JWT token.

### Candidate Endpoints
- `GET /candidate/profile`: Get candidate profile.
- `PATCH /candidate/profile/update`: Update candidate profile.
- `PATCH /candidate/job_criteria/update`: Update job search criteria.
- `PATCH /candidate/skills/update`: Update skills information.
- `PATCH /candidate/profile_files/edit`: Upload profile picture and CV.
- `GET /candidate/jobs`: Browse job posts with filters.

### Employer Endpoints
- `POST /employer/create_job_post`: Create a job post.
- `GET /employer/get_job_posts`: View job posts created by the employer.
- `GET /employer/me/profile`: Get employer profile.
- `PUT /employer/me/profile/update`: Update employer profile.

---

## Project Modules
### **Core Module**
- **config.py**: Manages app configurations using Pydantic.
- **database.py**: Establishes a connection to MongoDB using `motor.motor_asyncio`.
- **security.py**: Handles JWT creation, validation, and role-based access.

### **Models Module**
Contains data models for validation using Pydantic.
- **User Models**: Handles user registration, login, and profile.
- **Employer Models**: Manages employer profiles and job postings.
- **Candidate Models**: Manages candidate profiles, skills, and job applications.

### **Services Module**
Handles business logic and communicates with the database.

### **Utils Module**
Contains reusable utility functions for the application.

---

## Security
- **JWT Authentication**: Ensures secure access with JWT tokens.
- **Password Hashing**: User passwords are hashed using bcrypt before storing them.
- **Role-based Access**: Candidate and employer roles have distinct permissions.
- **Token Expiration**: Access tokens expire after a set time to enhance security.

---

## Troubleshooting
| Issue                      | Possible Solution                |
|----------------------------|-----------------------------------|
| **Cannot connect to MongoDB** | Check if MongoDB URL is correct in `.env`. Ensure the database is running. |
| **Access Denied**             | Ensure JWT token is provided in the `Authorization` header. |
| **Token Expired**             | Re-login to obtain a fresh token. |

If you encounter any issues not listed here, please check the error logs or open an issue in the project's GitHub repository.

---
