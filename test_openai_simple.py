#!/usr/bin/env python3
"""
Simple OpenAI client test
"""
import os
from dotenv import load_dotenv
import openai

load_dotenv()

def test_openai_simple():
    """Test OpenAI client with simple configuration"""
    
    print("🔑 Testing OpenAI Client (Simple)...")
    print("=" * 40)
    
    # Check API key directly from environment
    api_key = os.getenv("OPENAI_API_KEY")
    print(f"🔍 Environment variable check: {'✅ Found' if api_key and api_key != 'your_openai_api_key_here' else '❌ Missing or placeholder'}")
    
    if not api_key or api_key == "your_openai_api_key_here":
        print("❌ Please update your .env file with a real OpenAI API key:")
        print("   OPENAI_API_KEY=sk-your-actual-key-here")
        return False
    
    print(f"✅ API key starts with: {api_key[:10]}...")
    
    try:
        # Simple client initialization (no proxy settings)
        print("🔧 Creating OpenAI client...")
        client = openai.OpenAI(
            api_key=api_key,
            timeout=30.0
        )
        print("✅ OpenAI client created successfully")
        
        # Test simple API call
        print("🧠 Testing simple API call...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "What is Mount Rainier? Answer in one sentence."}
            ],
            max_tokens=50,
            temperature=0.5
        )
        
        answer = response.choices[0].message.content or "No response"
        print(f"✅ API call successful!")
        print(f"📝 Response: {answer}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"   Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    success = test_openai_simple()
    if success:
        print("\n🎉 OpenAI client working perfectly!")
        print("✅ Ready to test full RAG system!")
    else:
        print("\n💡 Please fix the API key issue first.") 