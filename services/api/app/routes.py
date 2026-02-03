from fastapi import APIRouter, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.responses import JSONResponse
import json
import asyncio
import redis.asyncio as redis
import uuid
from pathlib import Path

router = APIRouter()

# Store active WebSocket connections
active_connections: list[WebSocket] = []
redis_client = None

# Create uploads directory with absolute path
UPLOADS_DIR = Path(__file__).parent.parent.parent.parent / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

async def get_redis():
    global redis_client
    if redis_client is None:
        redis_client = await redis.from_url("redis://localhost:6379", decode_responses=True)
    return redis_client

@router.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    """Upload a video file for processing"""
    try:
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Save the uploaded file
        file_path = UPLOADS_DIR / f"{job_id}_{file.filename}"
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Send job to Redis queue with absolute path
        r = await get_redis()
        await r.lpush("video_queue", json.dumps({
            "job_id": job_id,
            "video_path": str(file_path.absolute()),
            "filename": file.filename
        }))
        
        # Store job status
        await r.set(f"job:{job_id}:status", "queued")
        
        return JSONResponse(
            content={
                "message": "Video uploaded successfully",
                "job_id": job_id,
                "filename": file.filename,
                "size": len(contents)
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@router.websocket("/ws/commentary")
async def websocket_commentary(websocket: WebSocket):
    """WebSocket endpoint for real-time commentary streaming"""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        # Wait for job_id from client
        data = await websocket.receive_text()
        job_data = json.loads(data)
        job_id = job_data.get("job_id")
        
        if not job_id:
            await websocket.send_json({"error": "No job_id provided"})
            return
        
        # Subscribe to Redis pub/sub for this job
        r = await get_redis()
        pubsub = r.pubsub()
        await pubsub.subscribe(f"commentary:{job_id}")
        
        await websocket.send_json({
            "status": "connected",
            "message": "Listening for commentary..."
        })
        
        # Listen for commentary updates
        async for message in pubsub.listen():
            if message["type"] == "message":
                commentary_data = json.loads(message["data"])
                await websocket.send_json(commentary_data)
            
    except WebSocketDisconnect:
        active_connections.remove(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        if websocket in active_connections:
            active_connections.remove(websocket)

@router.get("/status/{job_id}")
async def get_job_status(job_id: str):
    """Get the status of a processing job"""
    # TODO: Query Redis for job status
    return {"job_id": job_id, "status": "processing"}
