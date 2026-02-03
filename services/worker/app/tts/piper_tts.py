from typing import Dict
import numpy as np
import os
from openai import OpenAI
import io
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class PiperTTS:
    """Text-to-speech using OpenAI TTS"""
    
    def __init__(self, config: Dict):
        self.config = config
        
        # Initialize OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            self.client = OpenAI(api_key=api_key)
            self.use_openai = True
            print("OpenAI TTS enabled for speech synthesis")
        else:
            self.client = None
            self.use_openai = False
            print("TTS disabled (no OpenAI API key found)")
    
    def _load_model(self):
        """Load TTS model (not needed for OpenAI)"""
        pass
    
    def synthesize(self, text: str) -> bytes:
        """
        Convert text to speech using OpenAI TTS
        
        Args:
            text: Commentary text to synthesize
            
        Returns:
            Audio data as bytes
        """
        print(f"[TTS] {text}")
        
        if self.use_openai and self.client:
            try:
                response = self.client.audio.speech.create(
                    model=self.config.get('model', 'tts-1'),
                    voice=self.config.get('voice', 'alloy'),
                    input=text,
                    speed=self.config.get('speed', 1.0)
                )
                
                # Return audio bytes
                return response.content
                
            except Exception as e:
                print(f"OpenAI TTS error: {e}")
        
        # Fallback: Generate simple tone as placeholder
        sample_rate = 22050
        duration = 2.0
        frequency = 440.0
        
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio = np.sin(2 * np.pi * frequency * t)
        
        # Convert to 16-bit PCM
        audio_int16 = (audio * 32767).astype(np.int16)
        
        return audio_int16.tobytes()
