from typing import List, Dict, Optional
import time

class EventAggregator:
    """Aggregate and filter events to prevent duplicate commentary"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.cooldown_period = config.get('cooldown_period', 3.0)
        self.min_confidence = config.get('min_confidence', 0.6)
        self.last_event_time = {}
    
    def process(self, events: List[Dict], frame_id: int) -> Optional[Dict]:
        """
        Process and aggregate events
        
        Args:
            events: List of detected events
            frame_id: Current frame ID
            
        Returns:
            Aggregated event if significant, None otherwise
        """
        if not events:
            return None
        
        current_time = time.time()
        
        for event in events:
            event_type = event['event_type']
            confidence = event['confidence']
            
            # Check confidence threshold
            if confidence < self.min_confidence:
                continue
            
            # Check cooldown
            last_time = self.last_event_time.get(event_type, 0)
            if current_time - last_time < self.cooldown_period:
                continue
            
            # Event is significant
            self.last_event_time[event_type] = current_time
            
            return {
                'event_type': event_type,
                'confidence': confidence,
                'frame_id': frame_id,
                'timestamp': current_time
            }
        
        return None
