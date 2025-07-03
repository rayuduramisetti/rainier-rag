#!/usr/bin/env python3
"""
Query Enhancement Module for Mount Rainier RAG System
Uses LLM to improve user questions before RAG retrieval
"""

import openai
import logging
from typing import Dict, Any
from config import Config

logger = logging.getLogger(__name__)

class QueryEnhancer:
    """Enhances user queries using LLM before RAG retrieval"""
    
    def __init__(self):
        self.config = Config()
    
    async def enhance_query(self, raw_question: str, query_type: str = "general") -> Dict[str, Any]:
        """
        Enhance a user's raw question for better RAG retrieval
        
        Args:
            raw_question: User's original question
            query_type: Type of query (trail, weather, permits, etc.)
            
        Returns:
            Dict with enhanced query and metadata
        """
        try:
            # Create enhancement prompt based on query type
            enhancement_prompt = self._get_enhancement_prompt(query_type)
            
            # Create user message with the raw question
            user_message = f"""
Original User Question: "{raw_question}"

Please rewrite this question to be more specific and effective for searching Mount Rainier National Park information. Focus on:
- Making the question clear and specific
- Including relevant Mount Rainier context
- Using better search terms
- Maintaining the user's intent

Enhanced Question:"""

            # Call OpenAI to enhance the query
            client = openai.OpenAI(api_key=self.config.OPENAI_API_KEY)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": enhancement_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=150,
                temperature=0.3  # Lower temperature for more focused enhancement
            )
            
            enhanced_query = response.choices[0].message.content
            if enhanced_query:
                enhanced_query = enhanced_query.strip()
            else:
                enhanced_query = raw_question  # Fallback to original
            
            return {
                "original_question": raw_question,
                "enhanced_question": enhanced_query,
                "query_type": query_type,
                "enhancement_successful": True,
                "enhancement_method": "openai_gpt35"
            }
            
        except Exception as e:
            logger.error(f"Error enhancing query: {e}")
            # Fallback to original question if enhancement fails
            return {
                "original_question": raw_question,
                "enhanced_question": raw_question,
                "query_type": query_type,
                "enhancement_successful": False,
                "error": str(e)
            }
    
    def _get_enhancement_prompt(self, query_type: str) -> str:
        """Get system prompt for query enhancement based on type"""
        
        base_prompt = """You are a Mount Rainier National Park information specialist. Your job is to rewrite user questions to make them more effective for searching park information.

Rewrite questions to be:
- Specific to Mount Rainier National Park
- Clear and unambiguous  
- Using relevant search terms
- Focused on actionable information

Keep the user's original intent but make the question more searchable."""

        type_specific_prompts = {
            "trail": f"{base_prompt}\n\nFocus on trail-specific terms like: difficulty, distance, elevation gain, trailhead, conditions, permits required.",
            
            "weather": f"{base_prompt}\n\nFocus on weather-specific terms like: current conditions, seasonal patterns, elevation effects, safety considerations.",
            
            "permits": f"{base_prompt}\n\nFocus on permit-specific terms like: requirements, reservations, fees, wilderness permits, climbing permits.",
            
            "safety": f"{base_prompt}\n\nFocus on safety-specific terms like: hazards, emergency procedures, gear requirements, risk factors.",
            
            "gear": f"{base_prompt}\n\nFocus on equipment-specific terms like: recommended gear, seasonal equipment, climbing gear, safety equipment.",
            
            "climbing": f"{base_prompt}\n\nFocus on mountaineering terms like: routes, permits, technical difficulty, gear requirements, conditions."
        }
        
        return type_specific_prompts.get(query_type, base_prompt)
    
    def classify_query_type(self, question: str) -> str:
        """Simple rule-based query type classification"""
        question_lower = question.lower().strip()
        
        # Handle empty or very short queries
        if len(question_lower) == 0:
            return "empty"
        
        # Conversational/Greeting keywords - HIGHEST PRIORITY
        greeting_patterns = [
            "hello", "hi", "hey", "good morning", "good afternoon", "good evening",
            "greetings", "howdy", "what's up", "how are you", "how's it going"
        ]
        if any(pattern in question_lower for pattern in greeting_patterns):
            return "greeting"
        
        # Conversational questions about the system itself
        system_patterns = [
            "who are you", "what are you", "what can you do", "help me",
            "what do you know", "can you help", "how do you work"
        ]
        if any(pattern in question_lower for pattern in system_patterns):
            return "system_info"
        
        # Thank you / goodbye patterns
        if any(word in question_lower for word in ["thank", "thanks", "goodbye", "bye", "see you"]):
            return "courtesy"
        
        # Check for obviously off-topic questions (common non-Mount Rainier topics)
        off_topic_indicators = [
            "capital of", "president of", "what is the weather in", "how to cook",
            "stock market", "movie", "sports", "politics", "celebrity"
        ]
        if any(indicator in question_lower for indicator in off_topic_indicators):
            return "off_topic"
        
        # Trail-related keywords
        if any(word in question_lower for word in ["trail", "hike", "hiking", "walk", "path", "route", "trek"]):
            return "trail"
        
        # Weather-related keywords  
        elif any(word in question_lower for word in ["weather", "temperature", "rain", "snow", "conditions", "forecast"]):
            return "weather"
        
        # Permit-related keywords
        elif any(word in question_lower for word in ["permit", "reservation", "fee", "cost", "book", "register"]):
            return "permits"
        
        # Safety-related keywords
        elif any(word in question_lower for word in ["safety", "dangerous", "hazard", "emergency", "rescue", "risk"]):
            return "safety"
        
        # Gear-related keywords
        elif any(word in question_lower for word in ["gear", "equipment", "pack", "clothing", "boots", "backpack"]):
            return "gear"
        
        # Climbing-related keywords
        elif any(word in question_lower for word in ["climb", "summit", "mountaineer", "ascent", "glacier", "technical"]):
            return "climbing"
        
        else:
            return "general"

# Example usage and testing
async def test_query_enhancement():
    """Test the query enhancement functionality"""
    
    enhancer = QueryEnhancer()
    
    test_questions = [
        "what trails are good?",
        "is it cold there?", 
        "do i need permits?",
        "what should i bring?",
        "how do i get to the top?",
        "is it safe to hike alone?"
    ]
    
    print("🔍 Query Enhancement Testing")
    print("=" * 50)
    
    for question in test_questions:
        print(f"\n📝 Original: '{question}'")
        
        # Classify query type
        query_type = enhancer.classify_query_type(question)
        print(f"🏷️  Type: {query_type}")
        
        # Enhance query
        if enhancer.config.OPENAI_API_KEY and enhancer.config.OPENAI_API_KEY != "your_openai_api_key_here":
            result = await enhancer.enhance_query(question, query_type)
            print(f"✨ Enhanced: '{result['enhanced_question']}'")
            print(f"✅ Success: {result['enhancement_successful']}")
        else:
            print("⚠️  No API key - cannot enhance")
        
        print("-" * 60)

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_query_enhancement()) 