from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:63343",
    "http://localhost:5173",
    "https://example.com",
    "https://www.example.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Define your routers here
from routers.auth import router as auth_router
from routers.candidate import router as candidates_router
from routers.employers import router as employers_router
from routers.analytics import router as analytics_router
from routers.data import router as data_router

app.include_router(auth_router)
app.include_router(candidates_router)
app.include_router(employers_router)
app.include_router(analytics_router)
app.include_router(data_router)
