#!/usr/bin/env python3
"""
Test the Streaming RAG System with OpenAI API
"""
import os
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.append(str(Path(__file__).parent / 'src'))

from rag_system.rag_engine import EnhancedRAGEngine

async def test_streaming_rag():
    """Test the streaming RAG system with real queries"""
    
    print("🏔️ Testing Mount Rainier Streaming RAG System...")
    print("=" * 60)
    
    # Initialize the RAG engine
    try:
        rag_engine = EnhancedRAGEngine()
        print("✅ RAG Engine initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize RAG Engine: {e}")
        return
    
    # Test queries
    test_queries = [
        "What are good beginner trails?",
        "Do I need permits for climbing?", 
        "What wildlife should I watch for?",
        "Best weather conditions to visit?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}: '{query}'")
        print("-" * 40)
        
        try:
            # Test streaming functionality
            response_generator = rag_engine.get_answer_stream(query)
            
            final_answer = ""
            async for update in response_generator:
                if update.get('step') in ['query_enhancement', 'vector_retrieval', 'response_generation']:
                    print(f"[{update.get('progress', 0)}%] {update.get('message', '')}")
                elif update.get('step') == 'final_result':
                    final_answer = update.get('answer', '')
                    print(f"\n📝 Final Answer:\n{final_answer[:200]}...")
                    break
                    
        except Exception as e:
            print(f"❌ Error processing query: {e}")
    
    print("\n🎉 Testing completed!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_streaming_rag()) 