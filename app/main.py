from fastapi import FastAPI
from app.routes import router
from app.database import engine
from app.db_models import Base

# Create all database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Banking API",
    description="A simple banking application built with FastAPI",
    version="1.0.0"
)

app.include_router(router)


@app.get("/")
def home():
    return {"message": "Welcome to the Banking API! Visit /docs to see all endpoints."}