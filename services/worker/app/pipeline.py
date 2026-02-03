import asyncio
import yaml
import json
import redis.asyncio as redis
import os
from pathlib import Path
from dotenv import load_dotenv
from app.detectors.yolo_detector import YOLODetector
from app.trackers.bytetrack_wrapper import ByteTrackWrapper
from app.classifiers.video_classifier import VideoClassifier
from app.aggregator.event_aggregator import EventAggregator
from app.nlp.commentary_generator import CommentaryGenerator
from app.tts.piper_tts import PiperTTS
from app.utils.video_reader import VideoReader
from app.config import Config

# Load environment variables
load_dotenv(Path(__file__).parent.parent.parent.parent / '.env')

class CommentaryPipeline:
    def __init__(self, config_path: str):
        self.config = Config(config_path)
        
        # Initialize components
        print("Initializing pipeline components...")
        self.detector = YOLODetector(self.config.detection)
        self.tracker = ByteTrackWrapper(self.config.tracking)
        self.classifier = VideoClassifier(self.config.classification)
        self.aggregator = EventAggregator(self.config.aggregation)
        self.commentary_gen = CommentaryGenerator(self.config.commentary)
        self.tts = PiperTTS(self.config.tts)
        print("Pipeline ready!")
    
    async def process_video(self, video_path: str, job_id: str, redis_client):
        """Process a video and generate commentary"""
        try:
            print(f"Processing video: {video_path}")
            await redis_client.set(f"job:{job_id}:status", "processing")
            
            reader = VideoReader(video_path)
            print(f"Video info: {reader.frame_count} frames, {reader.fps} fps")
            
            frame_count = 0
            for frame_id, frame in enumerate(reader):
                frame_count += 1
                
                # Process every 30th frame for efficiency
                if frame_id % 30 != 0:
                    continue
                
                # Detect objects
                detections = self.detector.detect(frame)
                print(f"[Frame {frame_id}] Detected {len(detections)} objects")
                
                # Track objects
                tracks = self.tracker.update(detections, frame)
                
                # Classify events
                events = self.classifier.classify(frame, tracks)
                
                # Debug: print events detected
                if events:
                    print(f"[Frame {frame_id}] Events: {events}")
                
                # Aggregate events
                aggregated = self.aggregator.process(events, frame_id)
                
                if aggregated:
                    # Generate commentary
                    commentary = self.commentary_gen.generate(aggregated)
                    
                    print(f"[Frame {frame_id}] Commentary: {commentary}")
                    
                    # Publish to Redis
                    commentary_data = {
                        'frame_id': frame_id,
                        'commentary': commentary,
                        'timestamp': frame_id / reader.fps,
                        'event_type': aggregated['event_type']
                    }
                    
                    await redis_client.publish(
                        f"commentary:{job_id}",
                        json.dumps(commentary_data)
                    )
                
                # Small delay
                await asyncio.sleep(0.01)
            
            print(f"Processed {frame_count} total frames")
            await redis_client.set(f"job:{job_id}:status", "completed")
            print(f"Job {job_id} completed!")
            
        except Exception as e:
            print(f"Error processing video: {e}")
            import traceback
            traceback.print_exc()
            await redis_client.set(f"job:{job_id}:status", f"error: {str(e)}")

async def worker_main():
    """Main worker loop that listens for jobs from Redis"""
    print("Starting worker service...")
    
    # Initialize Redis connection
    redis_client = await redis.from_url("redis://localhost:6379", decode_responses=True)
    print("Connected to Redis")
    
    # Initialize pipeline
    pipeline = CommentaryPipeline("../../configs/pipeline.yaml")
    
    print("Worker ready! Waiting for jobs...")
    
    while True:
        try:
            # Block and wait for job from queue
            job_data = await redis_client.brpop("video_queue", timeout=1)
            
            if job_data:
                queue_name, job_json = job_data
                job = json.loads(job_json)
                
                job_id = job["job_id"]
                video_path = job["video_path"]
                
                print(f"\nReceived job {job_id}: {job['filename']}")
                
                # Process the video
                await pipeline.process_video(video_path, job_id, redis_client)
                
        except Exception as e:
            print(f"Worker error: {e}")
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(worker_main())
