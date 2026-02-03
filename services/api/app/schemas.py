from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class VideoUploadResponse(BaseModel):
    job_id: str
    status: str
    message: str

class CommentaryEvent(BaseModel):
    timestamp: float
    event_type: str
    description: str
    confidence: float

class DetectionResult(BaseModel):
    frame_id: int
    timestamp: float
    detections: List[dict]
    events: List[CommentaryEvent]

class JobStatus(BaseModel):
    job_id: str
    status: str
    progress: float
    created_at: datetime
    updated_at: datetime
    error: Optional[str] = None
