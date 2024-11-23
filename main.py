from fastapi import FastAPI
from routers.auth import router as auth_router
from routers.candidate import router as candidates_router
from routers.employers import router as employers_router

app = FastAPI()
app.include_router(auth_router)
app.include_router(candidates_router)
app.include_router(employers_router)
