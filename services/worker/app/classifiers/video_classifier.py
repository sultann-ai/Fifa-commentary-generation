import numpy as np
from typing import List, Dict
import torch
import base64
import cv2
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

class VideoClassifier:
    """Classifier for football event recognition using GPT-4 Vision"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.event_types = config.get('events', [])
        self.window_size = config.get('window_size', 16)
        self.frame_buffer = []
        
        # Initialize OpenAI client for GPT-4 Vision
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            self.client = OpenAI(api_key=api_key)
            self.use_vlm = True
            print("GPT-4 Vision enabled for event classification")
        else:
            self.client = None
            self.use_vlm = False
            print("Using heuristic-based classification (no OpenAI API key)")
    
    def _load_model(self):
        """Load video classification model"""
        pass
    
    def classify(self, frame: np.ndarray, tracks: List[Dict]) -> List[Dict]:
        """
        Classify events in the current frame using GPT-4 Vision
        
        Args:
            frame: Current video frame
            tracks: List of tracked objects
            
        Returns:
            List of detected events
        """
        self.frame_buffer.append({
            'frame': frame,
            'tracks': tracks
        })
        
        # Keep buffer size fixed
        if len(self.frame_buffer) > self.window_size:
            self.frame_buffer.pop(0)
        
        # Use GPT-4 Vision if available
        if self.use_vlm and self.client:
            return self._classify_with_vlm(frame, tracks)
        else:
            # Fallback to simple heuristics
            return self._classify_heuristic(tracks)
    
    def _classify_with_vlm(self, frame: np.ndarray, tracks: List[Dict]) -> List[Dict]:
        """Use GPT-4 Vision to classify football events"""
        try:
            # Encode frame to base64
            _, buffer = cv2.imencode('.jpg', frame)
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # Prepare prompt for GPT-4 Vision
            prompt = """You are an expert football analyst. Analyze this video frame from a football match.
            
Identify what event is happening:
- pass: Player passing the ball
- shot: Player shooting at goal
- goal: Ball entering the goal
- tackle: Player tackling for the ball
- corner: Corner kick situation
- free_kick: Free kick situation
- dribble: Player dribbling with ball
- save: Goalkeeper making a save

Respond ONLY with a JSON object in this exact format:
{"event": "event_name", "confidence": 0.0-1.0, "description": "brief description"}

If no clear event is happening, return:
{"event": "play", "confidence": 0.5, "description": "general play"}"""

            response = self.client.chat.completions.create(
                model="gpt-4o",  # Latest GPT-4 with vision
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{frame_base64}",
                                    "detail": "low"  # Use low detail for faster processing
                                }
                            }
                        ]
                    }
                ],
                max_tokens=150,
                temperature=0.3
            )
            
            # Parse response
            result_text = response.choices[0].message.content.strip()
            
            # Try to extract JSON
            import json
            # Remove markdown code blocks if present
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(result_text)
            
            return [{
                'event_type': result.get('event', 'play'),
                'confidence': float(result.get('confidence', 0.5)),
                'description': result.get('description', ''),
                'timestamp': len(self.frame_buffer)
            }]
            
        except Exception as e:
            print(f"GPT-4 Vision error: {e}")
            # Fallback to heuristics
            return self._classify_heuristic(tracks)
    
    def _classify_heuristic(self, tracks: List[Dict]) -> List[Dict]:
        """Simple heuristic-based event detection (fallback)"""
        events = []
        
        # Count players and ball
        players = [t for t in tracks if t['class_name'] == 'person']
        balls = [t for t in tracks if t['class_name'] == 'sports ball']
        
        if len(players) > 10 and len(balls) > 0:
            # Detect potential events based on ball position and player proximity
            if len(self.frame_buffer) == self.window_size:
                events.append({
                    'event_type': 'pass',
                    'confidence': 0.7,
                    'timestamp': len(self.frame_buffer)
                })
        
        return events
