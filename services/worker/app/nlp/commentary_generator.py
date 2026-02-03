from typing import Dict
import random
import os
from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class CommentaryGenerator:
    """Generate natural language commentary from events using OpenAI"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.templates = self._load_templates()
        
        # Initialize OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            self.client = OpenAI(api_key=api_key)
            self.use_openai = True
            print("OpenAI GPT enabled for commentary generation")
        else:
            self.client = None
            self.use_openai = False
            print("Using template-based commentary (no OpenAI API key found)")
    
    def _load_templates(self) -> Dict:
        """Load commentary templates for different events"""
        return {
            'pass': [
                "Great pass from midfield!",
                "Nice ball movement!",
                "The players are connecting well.",
                "Excellent passing play here."
            ],
            'shot': [
                "Shot on goal!",
                "He takes the shot!",
                "A powerful strike towards goal!",
                "What a shot attempt!"
            ],
            'goal': [
                "GOAL! What a finish!",
                "It's in! Incredible goal!",
                "GOAL! The crowd goes wild!",
                "Yes! They've scored!"
            ],
            'tackle': [
                "Strong tackle!",
                "Great defensive play!",
                "He wins the ball back!",
                "Excellent defending!"
            ],
            'corner': [
                "Corner kick awarded.",
                "It's a corner for the attacking team.",
                "Corner kick coming up."
            ],
            'free_kick': [
                "Free kick opportunity.",
                "The referee awards a free kick.",
                "Free kick in a dangerous position."
            ]
        }
    
    def generate(self, event: Dict) -> str:
        """
        Generate commentary for an event
        
        Args:
            event: Event dictionary with type and metadata
            
        Returns:
            Commentary text
        """
        event_type = event.get('event_type', 'pass')
        event_description = event.get('description', '')
        
        # Use OpenAI if available
        if self.use_openai and self.client:
            return self._generate_with_openai(event)
        
        # Fallback to templates
        templates = self.templates.get(event_type, self.templates['pass'])
        return random.choice(templates)
    
    def _generate_with_openai(self, event: Dict) -> str:
        """Generate commentary using OpenAI GPT"""
        try:
            event_type = event.get('event_type', 'pass')
            confidence = event.get('confidence', 0.5)
            frame_id = event.get('frame_id', 0)
            description = event.get('description', '')
            
            # If we have a description from GPT-4 Vision, use it for context
            if description:
                prompt = f"""You are a football commentator. Generate ONE SHORT sentence (max 8 words) for this event:
                
Event: {event_type}
What's happening: {description}

Just one brief, exciting sentence!"""
            else:
                prompt = f"""You are a football commentator. Generate ONE SHORT sentence (max 8 words) for this event:
                
Event: {event_type}

Just one brief, exciting sentence!"""
            
            response = self.client.chat.completions.create(
                model=self.config.get('model', 'gpt-3.5-turbo'),
                messages=[
                    {"role": "system", "content": "You are a football commentator. Always respond with ONE SHORT sentence only (max 8 words). Be exciting but brief."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=30,
                temperature=self.config.get('temperature', 0.7)
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"OpenAI error: {e}")
            # Fallback to templates
            templates = self.templates.get(event.get('event_type', 'pass'), self.templates['pass'])
            return random.choice(templates)
