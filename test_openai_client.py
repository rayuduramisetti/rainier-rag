#!/usr/bin/env python3
"""
Test OpenAI Client initialization
"""
import os
from dotenv import load_dotenv
import openai

load_dotenv()

def test_openai_client():
    """Test basic OpenAI client functionality"""
    
    print("🔑 Testing OpenAI Client...")
    print("=" * 40)
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        print("❌ No valid OpenAI API key found")
        return
    
    print(f"✅ API key found: {api_key[:10]}...")
    
    try:
        # Test client initialization
        print("🔧 Creating OpenAI client...")
        client = openai.OpenAI(api_key=api_key)
        print("✅ OpenAI client created successfully")
        
        # Test simple API call
        print("🧠 Testing simple API call...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "What is Mount Rainier?"}
            ],
            max_tokens=50
        )
        
        answer = response.choices[0].message.content or "No response"
        print(f"✅ API call successful!")
        print(f"📝 Response: {answer[:100]}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"   Error type: {type(e).__name__}")

if __name__ == "__main__":
    test_openai_client() 