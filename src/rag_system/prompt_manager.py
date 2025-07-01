import os
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class PromptManager:
    """Manages prompt templates for different query types"""
    
    def __init__(self, templates_dir: str = "templates"):
        self.templates_dir = templates_dir
        self.templates = {}
        self._load_templates()
    
    def _load_templates(self):
        """Load all prompt templates from the templates directory"""
        template_files = {
            "general": "system_prompt.txt",
            "trail": "trail_query_prompt.txt",
            "weather": "weather_query_prompt.txt",
            "safety": "safety_prompt.txt",
            "gear": "gear_prompt.txt",
            "permits": "permits_prompt.txt"
        }
        
        for query_type, filename in template_files.items():
            try:
                filepath = os.path.join(self.templates_dir, filename)
                if os.path.exists(filepath):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        self.templates[query_type] = f.read()
                    logger.info(f"Loaded template for {query_type}")
                else:
                    # Use default template if specific one doesn't exist
                    self.templates[query_type] = self._get_default_template()
                    logger.warning(f"Template file {filename} not found, using default")
            except Exception as e:
                logger.error(f"Error loading template {filename}: {e}")
                self.templates[query_type] = self._get_default_template()
    
    def _get_default_template(self) -> str:
        """Get default template if specific template is not available"""
        return """You are the Mount Rainier AI Guide. Use the provided context to answer the user's question.

Context: {context}
Current Weather: {weather_info}
Trail Conditions: {trail_conditions}
Seasonal Info: {seasonal_info}

Question: {user_question}

Provide a helpful, accurate, and safety-focused response."""
    
    def get_prompt_template(self, query_type: str = "general") -> str:
        """Get the appropriate prompt template for the query type"""
        return self.templates.get(query_type, self.templates.get("general", self._get_default_template()))
    
    def classify_query_type(self, question: str) -> str:
        """Classify the type of query based on keywords"""
        question_lower = question.lower()
        
        # Weather-related keywords
        weather_keywords = ["weather", "temperature", "rain", "snow", "wind", "forecast", "storm", "sunny", "cloudy"]
        if any(keyword in question_lower for keyword in weather_keywords):
            return "weather"
        
        # Trail-related keywords
        trail_keywords = ["trail", "hike", "hiking", "path", "route", "distance", "elevation", "difficulty", "time"]
        if any(keyword in question_lower for keyword in trail_keywords):
            return "trail"
        
        # Safety-related keywords
        safety_keywords = ["safety", "danger", "emergency", "rescue", "accident", "risk", "hazard"]
        if any(keyword in question_lower for keyword in safety_keywords):
            return "safety"
        
        # Gear-related keywords
        gear_keywords = ["gear", "equipment", "boots", "backpack", "clothing", "pack", "what to bring"]
        if any(keyword in question_lower for keyword in gear_keywords):
            return "gear"
        
        # Permits-related keywords
        permit_keywords = ["permit", "reservation", "registration", "fee", "pass", "entrance"]
        if any(keyword in question_lower for keyword in permit_keywords):
            return "permits"
        
        return "general"
    
    def add_custom_template(self, query_type: str, template: str):
        """Add a custom template for a specific query type"""
        self.templates[query_type] = template
        logger.info(f"Added custom template for {query_type}")
    
    def reload_templates(self):
        """Reload all templates from files"""
        self.templates.clear()
        self._load_templates()
        logger.info("Reloaded all templates") 