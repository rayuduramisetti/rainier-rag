#!/usr/bin/env python3
"""
Enhanced RAG Engine for Mount Rainier System
Now includes Query Enhancement + Vector Retrieval + LLM Generation
WITH STREAMING PROGRESS UPDATES
"""

import asyncio
from typing import List, Dict, Any, Optional, AsyncGenerator
from datetime import datetime
import logging

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

logger = logging.getLogger(__name__)

class EnhancedRAGEngine:
    """Enhanced RAG Engine with Query Enhancement and Streaming Updates"""
    
    def __init__(self):
        self.config = Config()
        self.query_enhancer = QueryEnhancer()
        
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
        
        logger.info("Enhanced RAG Engine initialized with streaming capability")
    
    async def get_answer_stream(self, user_question: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Complete Enhanced RAG Pipeline with Streaming Updates:
        1. Query Classification & Conversational Handling
        2. Query Enhancement (LLM) - with progress
        3. Vector Retrieval - with progress
        4. Response Generation (LLM) - with progress
        
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
            
            # Classify query type
            query_type = self.query_enhancer.classify_query_type(user_question)
            
            yield {
                "step": "query_classification", 
                "status": "completed",
                "message": f"🏷️ Detected query type: {query_type}",
                "query_type": query_type,
                "progress": 10
            }
            
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
            
            # STEP 1: Query Enhancement (for informational queries)
            yield {
                "step": "query_enhancement",
                "status": "processing",
                "message": "✨ Enhancing your question for better search...",
                "progress": 20
            }
            
            yield {
                "step": "query_enhancement", 
                "status": "processing",
                "message": f"🏷️ Detected query type: {query_type}",
                "progress": 20
            }
            
            # Enhance the query using LLM
            yield {
                "step": "query_enhancement",
                "status": "processing", 
                "message": "✨ Enhancing your question for better search...",
                "progress": 30
            }
            
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
            
            # STEP 2: Vector Retrieval
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
            
            # STEP 3: Response Generation
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
            
            # Generate response using OpenAI
            response = await self._generate_response(
                original_question=user_question,
                enhanced_question=enhanced_question,
                context=context,
                query_type=query_type
            )
            
            yield {
                "step": "response_generation",
                "status": "completed",
                "message": "✅ Response generated successfully!",
                "progress": 90
            }
            
            # Prepare sources
            sources = []
            for doc in retrieved_docs:
                source_info = doc.metadata.get('source', 'Mount Rainier Knowledge Base')
                if source_info not in sources:
                    sources.append(source_info)
            
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
        query_type: str
    ) -> str:
        """Generate response using OpenAI with context and enhanced question"""
        
        # Create system prompt based on query type
        system_prompt = self._get_system_prompt(query_type)
        
        # Create user message with context
        user_message = f"""Based on the following Mount Rainier information, please answer the user's question.

ORIGINAL USER QUESTION: "{original_question}"
ENHANCED QUESTION: "{enhanced_question}"

RELEVANT INFORMATION:
{context}

Please provide a helpful, accurate answer based on the information provided. If the information doesn't fully answer the question, say so. Always mention specific details from the context when relevant.

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

ANSWER:"""

        try:
            client = openai.OpenAI(api_key=self.config.OPENAI_API_KEY)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content or "I couldn't generate a proper response."
            
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