#!/usr/bin/env python3
"""
Fresh OpenAI API test - completely isolated
"""
import os

def test_fresh_openai():
    """Test OpenAI API with completely fresh approach"""
    
    print("🔬 Fresh OpenAI API Test...")
    print("=" * 40)
    
    # Read API key directly from .env file
    api_key = None
    try:
        with open('.env', 'r') as f:
            env_content = f.read()
            for line in env_content.split('\n'):
                if line.startswith('OPENAI_API_KEY='):
                    api_key = line.split('=', 1)[1].strip()
                    break
            
        if not api_key:
            print("❌ No OPENAI_API_KEY found in .env file")
            return False
            
    except FileNotFoundError:
        print("❌ .env file not found")
        return False
    
    if not api_key or api_key == "your_openai_api_key_here":
        print("❌ API key is placeholder")
        return False
        
    print(f"✅ API key found: {api_key[:15]}...")
    
    try:
        # Import and test OpenAI with minimal configuration
        import openai
        
        print("🔧 Creating minimal OpenAI client...")
        client = openai.OpenAI(api_key=api_key)
        
        print("🧠 Testing API call...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'Mount Rainier RAG test successful' in one sentence."}],
            max_tokens=20
        )
        
        result = response.choices[0].message.content
        print(f"✅ SUCCESS: {result}")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print(f"   Type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    success = test_fresh_openai()
    if success:
        print("\n🎉 OpenAI API working perfectly!")
    else:
        print("\n❌ OpenAI API test failed") 