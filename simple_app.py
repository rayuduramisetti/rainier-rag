#!/usr/bin/env python3
"""
Simple Mount Rainier RAG App - Testing Version
"""
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from rag_system.rag_engine import EnhancedRAGEngine

async def test_rag_system():
    """Test the Enhanced RAG system with sample queries"""
    
    print("🏔️" + "="*60)
    print("🏔️  MOUNT RAINIER AI GUIDE - TESTING VERSION")
    print("🏔️" + "="*60)
    print()
    
    # Initialize RAG engine
    print("🚀 Initializing Enhanced RAG System...")
    try:
        rag = EnhancedRAGEngine()
        print("✅ RAG System ready!")
        print()
    except Exception as e:
        print(f"❌ Error initializing RAG: {e}")
        return
    
    # Test queries
    test_queries = [
        "What are the best beginner trails?",
        "Do I need permits for climbing Mount Rainier?",
        "What wildlife should I watch for?",
        "What's the best time to visit for weather?",
        "What gear do I need for winter hiking?"
    ]
    
    print("🧪 Testing RAG System with sample queries...")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}: '{query}'")
        print("-" * 40)
        
        try:
            # Get streaming response
            async for update in rag.get_answer_stream(query):
                step = update.get("step", "")
                progress = update.get("progress", 0)
                message = update.get("message", "")
                
                if step in ["query_enhancement", "vector_retrieval", "response_generation"]:
                    print(f"[{progress:3d}%] {message}")
                
                elif step == "final_result":
                    answer = update.get("answer", "No answer generated")
                    sources = update.get("sources", [])
                    enhanced = update.get("enhancement_used", False)
                    
                    print(f"\n📝 Answer:")
                    print(f"{answer[:200]}...")
                    print(f"\n📚 Sources: {', '.join(sources)}")
                    print(f"✨ Query Enhanced: {'Yes' if enhanced else 'No'}")
                    break
                    
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()
    
    print("🎉 RAG System testing completed!")
    print("\n💡 If all tests passed, your Enhanced RAG System is working perfectly!")
    print("   The issue is only with the Gradio UI compatibility.")

def interactive_mode():
    """Simple interactive mode for testing"""
    
    print("\n" + "="*60)
    print("🗣️  INTERACTIVE MODE")
    print("="*60)
    print("Type your questions about Mount Rainier!")
    print("Type 'quit' to exit.\n")
    
    # Initialize RAG
    try:
        rag = EnhancedRAGEngine()
        print("✅ Ready for your questions!\n")
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    while True:
        try:
            user_input = input("🏔️ Ask me: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Thanks for using Mount Rainier AI Guide!")
                break
                
            if not user_input:
                continue
            
            print(f"\n🤔 Processing: '{user_input}'")
            print("-" * 30)
            
            # Get answer (non-streaming for simplicity)
            result = asyncio.run(rag.get_answer(user_input))
            
            if result:
                print(f"\n📝 Answer:")
                print(f"{result.get('answer', 'No answer available')}")
                
                sources = result.get('sources', [])
                if sources:
                    print(f"\n📚 Sources: {', '.join(sources)}")
                    
                enhanced = result.get('enhancement_used', False)
                if enhanced:
                    enhanced_q = result.get('enhanced_question', '')
                    print(f"\n✨ Enhanced Question: {enhanced_q}")
            
            print("\n" + "-"*50 + "\n")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("Choose mode:")
    print("1. Run automated tests")
    print("2. Interactive Q&A mode")
    
    choice = input("\nEnter 1 or 2: ").strip()
    
    if choice == "1":
        asyncio.run(test_rag_system())
    elif choice == "2":
        interactive_mode()
    else:
        print("Running both modes...")
        asyncio.run(test_rag_system())
        interactive_mode() 