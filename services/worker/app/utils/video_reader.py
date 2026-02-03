import cv2
import numpy as np
from typing import Iterator

class VideoReader:
    """Video frame reader utility"""
    
    def __init__(self, video_path: str):
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)
        
        if not self.cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")
        
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    def __iter__(self) -> Iterator[np.ndarray]:
        """Iterate over video frames"""
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            yield frame
    
    def __len__(self) -> int:
        return self.frame_count
    
    def __del__(self):
        if hasattr(self, 'cap'):
            self.cap.release()
    
    def read_frame(self, frame_id: int) -> np.ndarray:
        """Read specific frame by ID"""
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_id)
        ret, frame = self.cap.read()
        return frame if ret else None
