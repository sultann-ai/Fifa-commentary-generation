import numpy as np
from typing import List, Dict

class ByteTrackWrapper:
    """Wrapper for ByteTrack multi-object tracker"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.tracks = {}
        self.next_id = 0
        self.track_buffer = config.get('track_buffer', 30)
        self.match_thresh = config.get('match_thresh', 0.8)
    
    def update(self, detections: List[Dict], frame: np.ndarray) -> List[Dict]:
        """
        Update tracks with new detections
        
        Args:
            detections: List of detections from detector
            frame: Current frame
            
        Returns:
            List of tracked objects with track IDs
        """
        tracks = []
        
        for detection in detections:
            bbox = detection['bbox']
            
            # Simple IOU-based matching (simplified ByteTrack)
            matched_id = self._match_detection(bbox)
            
            if matched_id is None:
                matched_id = self.next_id
                self.next_id += 1
            
            track = {
                'track_id': matched_id,
                'bbox': bbox,
                'confidence': detection['confidence'],
                'class_name': detection['class_name']
            }
            
            self.tracks[matched_id] = {
                'bbox': bbox,
                'age': 0
            }
            
            tracks.append(track)
        
        # Age out old tracks
        self._age_tracks()
        
        return tracks
    
    def _match_detection(self, bbox: List[float]) -> int:
        """Match detection to existing track using IOU"""
        best_iou = 0
        best_id = None
        
        for track_id, track_data in self.tracks.items():
            iou = self._compute_iou(bbox, track_data['bbox'])
            if iou > best_iou and iou > self.match_thresh:
                best_iou = iou
                best_id = track_id
        
        return best_id
    
    def _compute_iou(self, bbox1: List[float], bbox2: List[float]) -> float:
        """Compute intersection over union"""
        x1 = max(bbox1[0], bbox2[0])
        y1 = max(bbox1[1], bbox2[1])
        x2 = min(bbox1[2], bbox2[2])
        y2 = min(bbox1[3], bbox2[3])
        
        if x2 < x1 or y2 < y1:
            return 0.0
        
        intersection = (x2 - x1) * (y2 - y1)
        area1 = (bbox1[2] - bbox1[0]) * (bbox1[3] - bbox1[1])
        area2 = (bbox2[2] - bbox2[0]) * (bbox2[3] - bbox2[1])
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0.0
    
    def _age_tracks(self):
        """Remove old tracks"""
        to_remove = []
        for track_id in self.tracks:
            self.tracks[track_id]['age'] += 1
            if self.tracks[track_id]['age'] > self.track_buffer:
                to_remove.append(track_id)
        
        for track_id in to_remove:
            del self.tracks[track_id]
