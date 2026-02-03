from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes import router
import redis.asyncio as redis

app = FastAPI(title="FIFA Commentator API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)

# Redis connection pool
redis_client = None

@app.on_event("startup")
async def startup_event():
    global redis_client
    redis_client = await redis.from_url("redis://localhost:6379", decode_responses=True)

@app.on_event("shutdown")
async def shutdown_event():
    if redis_client:
        await redis_client.close()

@app.get("/")
async def root():
    return {"message": "FIFA Commentator API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
