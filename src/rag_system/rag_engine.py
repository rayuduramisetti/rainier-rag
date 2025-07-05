#!/usr/bin/env python3
"""
Enhanced RAG Engine for Mount Rainier System
Now includes Query Enhancement + Vector Retrieval + LLM Generation
WITH STREAMING PROGRESS UPDATES + REAL-TIME WEATHER INTEGRATION
"""

import asyncio
from typing import List, Dict, Any, Optional, AsyncGenerator
from datetime import datetime
import logging
import re

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_community.vectorstores.chroma import Chroma
from langchain.schema import Document
import openai

from config import Config
from src.data_sources.nps_api import NPSDataSource
from src.data_sources.weather_api import WeatherDataSource
from src.data_sources.strava_api import StravaDataSource
from src.data_sources.visit_rainier_api import VisitRainierDataSource
from src.data_sources.web_search_api import WebSearchDataSource
from src.data_sources.alltrails_api import AllTrailsDataSource
from src.rag_system.prompt_manager import PromptManager
from .query_enhancement import QueryEnhancer
from alltrails_integration import AllTrailsIntegration, get_alltrails_response

logger = logging.getLogger(__name__)

class EnhancedRAGEngine:
    """Enhanced RAG Engine with Query Enhancement, Streaming Updates, and Real-time Weather Integration"""
    
    def __init__(self):
        self.config = Config()
        self.query_enhancer = QueryEnhancer()
        
        # Initialize data sources
        self.weather_source = WeatherDataSource()
        self.alltrails_integration = AllTrailsIntegration()
        
        # Initialize embeddings
        self.embeddings = SentenceTransformerEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Initialize ChromaDB
        self.vectorstore = Chroma(
            persist_directory="./data/chroma_db", 
            embedding_function=self.embeddings,
            collection_name="langchain"  # Using the existing collection with documents
        )
        
        logger.info("RAG Engine initialized")
    
    async def get_answer_stream(self, user_question: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Complete Enhanced RAG Pipeline with Streaming Updates and Weather Integration:
        1. Query Classification & Conversational Handling
        2. Weather Data Fetching (if weather-related)
        3. Query Enhancement (LLM) - with progress
        4. Vector Retrieval - with progress
        5. Response Generation (LLM) - with progress
        
        Args:
            user_question: Raw user question
            
        Yields:
            Dict with step updates and final result
        """
        try:
            # STEP 0: Query Classification (NEW - Handle conversational inputs)
            yield {
                "step": "query_classification",
                "status": "processing",
                "message": "🤔 Understanding your question...",
                "progress": 5
            }
            
            # LLM-based classification
            classification = await self.query_enhancer.classify_query_type(user_question)
            query_type = classification.get("type", "general")
            user_name = classification.get("name")
            
            yield {
                "step": "query_classification", 
                "status": "completed",
                "message": f"🏷️ Detected query type: {query_type}",
                "query_type": query_type,
                "user_name": user_name,
                "progress": 10
            }
            
            # Handle user introduction
            if query_type == "user_introduction" and user_name:
                response = f"<strong>Nice to meet you, {user_name}!</strong><br/><br/>How can I help you with Mount Rainier today?"
                yield {
                    "step": "final_result",
                    "status": "completed",
                    "original_question": user_question,
                    "enhanced_question": user_question,
                    "query_type": query_type,
                    "answer": response,
                    "sources": [],
                    "enhancement_used": False,
                    "conversation_mode": True,
                    "progress": 100,
                    "message": "✨ Personalized greeting ready!"
                }
                return
            
            # Handle conversational inputs directly (skip RAG pipeline)
            if query_type in ["greeting", "system_info", "courtesy", "off_topic", "empty"]:
                conversational_response = self._handle_conversational_input(user_question, query_type)
                
                yield {
                    "step": "final_result",
                    "status": "completed",
                    "original_question": user_question,
                    "enhanced_question": user_question,
                    "query_type": query_type,
                    "answer": conversational_response,
                    "sources": [],
                    "enhancement_used": False,
                    "conversation_mode": True,
                    "progress": 100,
                    "message": "✨ Conversational response ready!"
                }
                return
            
            # Handle AllTrails queries directly (list/recommendation only)
            if query_type == "alltrails" or self._is_alltrails_related(user_question):
                yield {
                    "step": "alltrails_lookup",
                    "status": "processing",
                    "message": "🥾 Looking up hiking information on AllTrails...",
                    "progress": 30
                }
                alltrails_response = get_alltrails_response(user_question)
                yield {
                    "step": "final_result",
                    "status": "completed",
                    "original_question": user_question,
                    "enhanced_question": user_question,
                    "query_type": "alltrails",
                    "answer": alltrails_response,
                    "sources": [{"title": "AllTrails Mount Rainier", "url": "https://www.alltrails.com/parks/us/washington/mount-rainier-national-park"}],
                    "enhancement_used": False,
                    "alltrails_mode": True,
                    "progress": 100,
                    "message": "🥾 AllTrails hiking information ready!"
                }
                return
                
                yield {
                    "step": "final_result",
                    "status": "completed",
                    "original_question": user_question,
                    "enhanced_question": user_question,
                    "query_type": query_type,
                    "answer": conversational_response,
                    "sources": [],
                    "enhancement_used": False,
                    "conversation_mode": True,
                    "progress": 100,
                    "message": "✨ Conversational response ready!"
                }
                return
            
            # STEP 1: Weather Data Fetching (if weather-related)
            current_weather = None
            weather_forecast = None
            
            if query_type == "weather" or self._is_weather_related(user_question):
                yield {
                    "step": "weather_fetch",
                    "status": "processing",
                    "message": "🌤️ Fetching current weather data from Mount Rainier...",
                    "progress": 15
                }
                
                try:
                    # Fetch current weather
                    current_weather = await self.weather_source.get_current_weather()
                    
                    yield {
                        "step": "weather_fetch",
                        "status": "processing",
                        "message": f"🌡️ Current: {current_weather['temperature']['current']}°F, {current_weather['conditions']['description']}",
                        "weather_data": current_weather,
                        "progress": 18
                    }
                    
                    # Fetch forecast if needed
                    if "forecast" in user_question.lower() or "tomorrow" in user_question.lower() or "week" in user_question.lower():
                        yield {
                            "step": "weather_fetch",
                            "status": "processing",
                            "message": "📅 Fetching weather forecast...",
                            "progress": 20
                        }
                        
                        weather_forecast = await self.weather_source.get_weather_forecast(days=5)
                        
                        yield {
                            "step": "weather_fetch",
                            "status": "completed",
                            "message": f"✅ Weather data ready! Current: {current_weather['temperature']['current']}°F",
                            "weather_data": current_weather,
                            "forecast_data": weather_forecast,
                            "progress": 25
                        }
                    else:
                        yield {
                            "step": "weather_fetch",
                            "status": "completed",
                            "message": f"✅ Current weather: {current_weather['temperature']['current']}°F, {current_weather['conditions']['description']}",
                            "weather_data": current_weather,
                            "progress": 25
                        }
                        
                except Exception as e:
                    logger.error(f"Error fetching weather data: {e}")
                    yield {
                        "step": "weather_fetch",
                        "status": "error",
                        "message": "⚠️ Weather data unavailable - using cached knowledge",
                        "progress": 25
                    }
            
            # STEP 2: Query Enhancement (for informational queries)
            yield {
                "step": "query_enhancement",
                "status": "processing",
                "message": "✨ Enhancing your question for better search...",
                "progress": 30
            }
            
            # Enhance the query using LLM
            enhancement_result = await self.query_enhancer.enhance_query(user_question, query_type)
            enhanced_question = enhancement_result["enhanced_question"]
            
            if enhancement_result["enhancement_successful"]:
                yield {
                    "step": "query_enhancement",
                    "status": "completed",
                    "message": f"✅ Enhanced question: '{enhanced_question}'",
                    "original_question": user_question,
                    "enhanced_question": enhanced_question,
                    "query_type": query_type,
                    "progress": 35
                }
            else:
                yield {
                    "step": "query_enhancement",
                    "status": "skipped",
                    "message": "⚠️ Query enhancement unavailable - using original question",
                    "original_question": user_question,
                    "enhanced_question": user_question,
                    "query_type": query_type,
                    "progress": 35
                }
            
            # STEP 3: Vector Retrieval
            yield {
                "step": "vector_retrieval",
                "status": "processing",
                "message": "🔍 Searching Mount Rainier knowledge base...",
                "progress": 45
            }
            
            retrieved_docs = self.vectorstore.similarity_search(
                enhanced_question, 
                k=3  # Get top 3 most relevant documents
            )
            
            if not retrieved_docs:
                yield {
                    "step": "vector_retrieval",
                    "status": "no_results",
                    "message": "❌ No relevant documents found",
                    "progress": 55
                }
                
                yield {
                    "step": "final_result",
                    "status": "completed",
                    "answer": "I couldn't find relevant information about that topic in my Mount Rainier knowledge base.",
                    "sources": [],
                    "progress": 100
                }
                return
            
            # Show retrieval results
            doc_sources = [doc.metadata.get('source', 'Unknown') for doc in retrieved_docs]
            unique_sources = list(set(doc_sources))
            
            yield {
                "step": "vector_retrieval",
                "status": "completed", 
                "message": f"📚 Found {len(retrieved_docs)} relevant documents from {len(unique_sources)} sources",
                "sources_found": unique_sources,
                "progress": 55
            }
            
            # STEP 4: Response Generation
            yield {
                "step": "response_generation",
                "status": "processing",
                "message": "🧠 Generating intelligent response...",
                "progress": 70
            }
            
            # Prepare context from retrieved documents
            context = "\n\n".join([
                f"Document {i+1}: {doc.page_content}" 
                for i, doc in enumerate(retrieved_docs)
            ])
            
            # Generate response using OpenAI with weather data if available
            response = await self._generate_response(
                original_question=user_question,
                enhanced_question=enhanced_question,
                context=context,
                query_type=query_type,
                current_weather=current_weather,
                weather_forecast=weather_forecast
            )
            
            yield {
                "step": "response_generation",
                "status": "completed",
                "message": "✅ Response generated successfully!",
                "progress": 90
            }
            
            # Prepare sources (with URLs if available)
            sources = []
            for doc in retrieved_docs:
                source_info = doc.metadata.get('source', 'Mount Rainier Knowledge Base')
                url = doc.metadata.get('url')
                # Avoid duplicates by name+url
                if not any(s['name'] == source_info and s.get('url') == url for s in sources):
                    sources.append({'name': source_info, 'url': url} if url else {'name': source_info})
            # Add weather source if used
            if current_weather:
                sources.append({'name': 'Real-time Weather Data'})
            
            # After generating the RAG/LLM answer for 'trail' queries, append AllTrails link if available
            if query_type == "trail":
                # Try to find a matching hike in AllTrailsIntegration
                trail_name = user_question.strip()
                alltrails_hikes = self.alltrails_integration.search_hikes(trail_name)
                if alltrails_hikes:
                    # Append AllTrails link to the answer
                    alltrails_link = alltrails_hikes[0]["url"]
                    alltrails_html = f'<br/><br/>🔗 <a href="{alltrails_link}" target="_blank">View this trail on AllTrails</a>'
                    # Add to sources as well
                    sources.append({"name": "AllTrails", "url": alltrails_link})
                    response += alltrails_html
            
            # FINAL RESULT
            yield {
                "step": "final_result",
                "status": "completed",
                "original_question": user_question,
                "enhanced_question": enhanced_question,
                "query_type": query_type,
                "retrieved_documents": [
                    {
                        "content": doc.page_content[:200] + "...",
                        "source": doc.metadata.get('source', 'Unknown')
                    }
                    for doc in retrieved_docs
                ],
                "answer": response,
                "sources": sources,
                "enhancement_used": enhancement_result["enhancement_successful"],
                "weather_used": current_weather is not None,
                "weather_data": current_weather,
                "forecast_data": weather_forecast,
                "progress": 100,
                "message": "🎉 Complete! Your Mount Rainier guide is ready."
            }
            
        except Exception as e:
            logger.error(f"Error in Enhanced RAG pipeline: {e}")
            yield {
                "step": "error",
                "status": "error",
                "message": f"❌ Error: {str(e)}",
                "error": str(e),
                "progress": 0
            }
    
    def _is_weather_related(self, question: str) -> bool:
        """Check if question is weather-related"""
        weather_keywords = [
            "weather", "temperature", "rain", "snow", "wind", "forecast", 
            "storm", "sunny", "cloudy", "cold", "hot", "precipitation",
            "conditions", "climate", "humidity", "visibility", "fog"
        ]
        question_lower = question.lower()
        return any(keyword in question_lower for keyword in weather_keywords)
    
    def _is_alltrails_related(self, question: str) -> bool:
        """Check if question is AllTrails/hiking-related"""
        alltrails_keywords = [
            'hike', 'hiking', 'trail', 'alltrails', 'trails', 'backpacking',
            'day hike', 'waterfall', 'lake', 'alpine', 'family friendly',
            'easy hike', 'moderate hike', 'hard hike', 'challenging hike',
            'wonderland trail', 'skyline trail', 'burroughs', 'naches peak',
            'comet falls', 'narada falls', 'crystal lakes', 'reflection lakes',
            'tolmie peak', 'mount fremont', 'grove of the patriarchs'
        ]
        question_lower = question.lower()
        return any(keyword in question_lower for keyword in alltrails_keywords)
    
    async def get_answer(self, user_question: str) -> Dict[str, Any]:
        """
        Non-streaming version for backward compatibility
        """
        final_result = None
        async for update in self.get_answer_stream(user_question):
            if update.get("step") == "final_result":
                final_result = update
                break
        
        return final_result or {
            "original_question": user_question,
            "enhanced_question": user_question,
            "query_type": "unknown",
            "retrieved_documents": [],
            "answer": "Sorry, I encountered an error while processing your question.",
            "sources": [],
            "enhancement_used": False
        }
    
    async def _generate_response(
        self, 
        original_question: str,
        enhanced_question: str, 
        context: str, 
        query_type: str,
        current_weather: Optional[Dict[str, Any]] = None,
        weather_forecast: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate response using OpenAI with context, enhanced question, and weather data"""
        
        # Create system prompt based on query type
        system_prompt = self._get_system_prompt(query_type)
        
        # Prepare weather context if available
        weather_context = ""
        if current_weather:
            weather_context = f"""
CURRENT WEATHER DATA:
Temperature: {current_weather['temperature']['current']}°F (feels like {current_weather['temperature']['feels_like']}°F)
Conditions: {current_weather['conditions']['description']}
Wind: {current_weather['wind']['speed']} mph
Humidity: {current_weather['humidity']}%
Visibility: {current_weather['visibility']} km
Location: {current_weather['location']}
Elevation Notes: {current_weather['elevation_notes']}

"""
        
        if weather_forecast and weather_forecast.get('forecasts'):
            weather_context += f"""
WEATHER FORECAST:
"""
            for i, forecast in enumerate(weather_forecast['forecasts'][:3]):  # Show next 3 days
                weather_context += f"Day {i+1}: High {forecast['temperature']['high']}°F, Low {forecast['temperature']['low']}°F, {forecast['conditions']['description']}, {forecast['precipitation_chance']:.0f}% chance of precipitation\n"
        
        # Create user message with context and weather data
        user_message = f"""Based on the following Mount Rainier information and current weather data, please answer the user's question.

ORIGINAL USER QUESTION: "{original_question}"
ENHANCED QUESTION: "{enhanced_question}"

{weather_context}RELEVANT INFORMATION:
{context}

Please provide a helpful, accurate answer based on the information provided. If weather data is available, incorporate it into your response and provide specific recommendations based on current conditions. If the information doesn't fully answer the question, say so. Always mention specific details from the context when relevant.

CRITICAL: Follow this EXACT formatting template:

<strong>Response Title Here</strong><br/><br/>

1. <strong>First Category:</strong> Brief description here<br/><br/>

2. <strong>Second Category:</strong> Brief description here<br/><br/>

3. <strong>Third Category:</strong> Brief description here<br/><br/>

MANDATORY RULES:
- Use HTML only (never markdown **text**)
- Every numbered section must end with <br/><br/>
- Never put multiple items on the same line
- Use <strong>text</strong> for bold formatting
- If you need to list multiple items within a section, separate them with " - " (dash-space)
- Keep each numbered section on its own paragraph
- If weather data is provided, include current conditions and recommendations in your response

ANSWER:"""

        try:
            client = openai.OpenAI(api_key=self.config.OPENAI_API_KEY)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=600,  # Increased for weather responses
                temperature=0.7
            )
            
            response_text = response.choices[0].message.content or "I couldn't generate a proper response."
            response_text = self._fix_numbered_list_formatting(response_text)
            return response_text
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"I found relevant information but couldn't generate a proper response. Error: {str(e)}"
    
    def _get_system_prompt(self, query_type: str) -> str:
        """Get system prompt based on query type"""
        
        base_prompt = """You are a knowledgeable Mount Rainier National Park guide. Provide helpful, accurate information about the park based on the context provided.

IMPORTANT FORMATTING RULES:
- Use HTML formatting for your response (not markdown)
- Use <strong>text</strong> for bold headings and important terms
- Use <br/><br/> for paragraph breaks  
- Use numbered lists with proper spacing: 1. <strong>Item:</strong> Description<br/><br/>
- Keep responses clear, well-structured, and easy to read
- Always use HTML tags instead of markdown formatting"""
        
        type_specific_prompts = {
            "trail": f"{base_prompt} Focus on trail details, difficulty levels, distances, and practical hiking advice.",
            "weather": f"{base_prompt} Focus on weather patterns, seasonal conditions, and safety considerations.",
            "permits": f"{base_prompt} Focus on permit requirements, fees, reservation processes, and regulations.",
            "safety": f"{base_prompt} Focus on safety guidelines, hazards, emergency procedures, and risk management.",
            "gear": f"{base_prompt} Focus on equipment recommendations, seasonal gear needs, and preparation advice.",
            "climbing": f"{base_prompt} Focus on mountaineering routes, technical requirements, and climbing safety."
        }
        
        return type_specific_prompts.get(query_type, base_prompt)
    
    def _handle_conversational_input(self, user_question: str, query_type: str) -> str:
        """Handle conversational inputs that don't need RAG processing"""
        
        question_lower = user_question.lower().strip()
        
        if query_type == "greeting":
            return (
                "<strong>Hello! 🏔️</strong><br/><br/>"
                "I'm your Mount Rainier guide. I can help you with trails, climbing routes, permits, "
                "gear recommendations, weather conditions, and safety information.<br/><br/>"
                "What would you like to know?"
            )
        
        elif query_type == "system_info":
            return (
                "I'm your Mount Rainier AI guide with knowledge about the park's 260+ miles of trails, "
                "climbing routes to the 14,411-foot summit, permits, safety guidelines, and gear recommendations. "
                "How can I help you plan your Mount Rainier adventure? 🗻"
            )
        
        elif query_type == "courtesy":
            if any(word in question_lower for word in ["thank", "thanks"]):
                return (
                    "You're welcome! 😊 Stay safe and enjoy your Mount Rainier adventure! 🏔️"
                )
            else:  # goodbye
                return (
                    "Safe travels! 👋 Remember to check conditions and carry the 10 essentials. Enjoy Mount Rainier! 🏔️"
                )
        
        elif query_type == "off_topic":
            return (
                "I specialize in Mount Rainier National Park information! 🏔️ "
                "I can help with trails, climbing routes, permits, weather, safety, and gear. "
                "What would you like to know about Mount Rainier? 🗻"
            )
        
        elif query_type == "empty":
            return (
                "I'm here to help with your Mount Rainier questions! 🏔️ "
                "Ask me about trails, climbing, permits, weather, safety, or gear. What interests you? 🗻"
            )
        
        else:
            # Fallback for any other conversational type
            return (
                "Hello! I'm your Mount Rainier guide. 🏔️ "
                "What would you like to know about hiking, climbing, permits, weather, or safety? 🗻"
            )

    def _fix_numbered_list_formatting(self, text: str) -> str:
        """Ensure each numbered item starts on a new line and ends with <br/> (compact look)"""
        # Add a newline before each number at the start of a line or after a <br/>
        text = re.sub(r'(\d+)\.\s*<strong>', r'<br/>\1. <strong>', text)
        # Remove extra <br/> at the very start
        text = re.sub(r'^(<br/>)+', '', text)
        # Ensure every numbered item ends with <br/>
        text = re.sub(r'(\d+\.\s*<strong>.*?</strong>.*?)(?=(\d+\.\s*<strong>|$))', lambda m: m.group(1).rstrip() + '<br/>', text, flags=re.DOTALL)
        return text

# For backward compatibility, keep the original class as an alias
class RAGEngine(EnhancedRAGEngine):
    """Alias for backward compatibility"""
    pass

# Test the streaming RAG system
async def test_streaming_rag():
    """Test the streaming RAG pipeline"""
    
    print("🚀 Streaming RAG System Test")
    print("=" * 50)
    
    rag = EnhancedRAGEngine()
    
    test_question = "what trails are good for beginners?"
    
    print(f"Question: '{test_question}'")
    print("-" * 30)
    
    async for update in rag.get_answer_stream(test_question):
        step = update.get("step", "unknown")
        status = update.get("status", "unknown")
        message = update.get("message", "")
        progress = update.get("progress", 0)
        
        print(f"[{progress:3d}%] {step.upper()}: {message}")
        
        if step == "final_result" and status == "completed":
            print("\n" + "="*50)
            print("FINAL ANSWER:")
            print(update.get("answer", "No answer"))
            print(f"\nSOURCES: {', '.join(update.get('sources', []))}")
            break
        
        # Small delay to simulate real processing
        await asyncio.sleep(0.5)

if __name__ == "__main__":
    asyncio.run(test_streaming_rag()) 