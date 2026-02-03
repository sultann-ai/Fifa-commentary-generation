from ultralytics import YOLO
import numpy as np
from typing import List, Dict

class YOLODetector:
    """YOLO-based object detector for players and ball"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.confidence_threshold = config.get('confidence_threshold', 0.5)
        self.model = None
        self.load_model(config.get('model', 'yolov8n'))
    
    def load_model(self, model_path: str):
        """Load YOLO model"""
        self.model = YOLO(model_path)
        print(f"Loaded YOLO model: {model_path}")
    
    def detect(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect objects in frame using YOLO
        
        Args:
            frame: Input image as numpy array (HxWxC)
            
        Returns:
            List of detections
        """
        results = self.model(frame, verbose=False)[0]
        
        detections = []
        for box in results.boxes:
            confidence = float(box.conf[0])
            
            if confidence < self.confidence_threshold:
                continue
            
            class_id = int(box.cls[0])
            class_name = results.names[class_id]
            
            # Filter for relevant classes
            if class_name not in self.config.get('classes', ['person', 'sports ball']):
                continue
            
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            
            detections.append({
                'bbox': [float(x1), float(y1), float(x2), float(y2)],
                'confidence': confidence,
                'class_id': class_id,
                'class_name': class_name
            })
        
        return detections
