import yaml
from pathlib import Path
from typing import Any, Dict

class Config:
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.data = yaml.safe_load(f)
        
        self.detection = self.data['pipeline']['detection']
        self.tracking = self.data['pipeline']['tracking']
        self.classification = self.data['pipeline']['classification']
        self.aggregation = self.data['pipeline']['aggregation']
        self.commentary = self.data['pipeline']['commentary']
        self.tts = self.data['pipeline']['tts']
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-separated key"""
        keys = key.split('.')
        value = self.data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        return value
