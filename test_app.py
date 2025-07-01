"""
Test script for Mount Rainier AI Guide
This script tests the core components without requiring full API setup
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

def test_config():
    """Test configuration loading"""
    print("🧪 Testing configuration...")
    try:
        from config import Config
        config = Config()
        print(f"✅ Configuration loaded successfully")
        print(f"   - Database path: {config.DATABASE_PATH}")
        print(f"   - Embeddings model: {config.EMBEDDINGS_MODEL}")
        print(f"   - Mount Rainier coordinates: {config.PARK_COORDINATES}")
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_prompt_manager():
    """Test prompt template loading"""
    print("\n🧪 Testing prompt manager...")
    try:
        from src.rag_system.prompt_manager import PromptManager
        manager = PromptManager()
        
        # Test template loading
        templates = list(manager.templates.keys())
        print(f"✅ Prompt manager loaded successfully")
        print(f"   - Available templates: {templates}")
        
        # Test query classification
        test_queries = [
            "What's the weather like?",
            "What trails are good for beginners?",
            "What gear do I need?",
            "Do I need permits?",
            "Is it safe to hike alone?"
        ]
        
        print("   - Query classification test:")
        for query in test_queries:
            query_type = manager.classify_query_type(query)
            print(f"     '{query}' -> {query_type}")
        
        return True
    except Exception as e:
        print(f"❌ Prompt manager test failed: {e}")
        return False

def test_data_sources():
    """Test data source initialization"""
    print("\n🧪 Testing data sources...")
    
    # Test weather source
    try:
        from src.data_sources.weather_api import WeatherDataSource
        weather = WeatherDataSource()
        print("✅ Weather data source initialized")
    except Exception as e:
        print(f"❌ Weather data source failed: {e}")
    
    # Test NPS source
    try:
        from src.data_sources.nps_api import NPSDataSource
        nps = NPSDataSource()
        print("✅ NPS data source initialized")
    except Exception as e:
        print(f"❌ NPS data source failed: {e}")
    
    # Test Strava source
    try:
        from src.data_sources.strava_api import StravaDataSource
        strava = StravaDataSource()
        print("✅ Strava data source initialized")
    except Exception as e:
        print(f"❌ Strava data source failed: {e}")
    
    return True

def test_gradio_app():
    """Test Gradio application initialization"""
    print("\n🧪 Testing Gradio application...")
    try:
        from src.ui.gradio_app import MountRainierGradioApp
        app = MountRainierGradioApp()
        
        # Test mountain scene generation
        scene = app.create_mountain_scene()
        print("✅ Gradio app initialized successfully")
        print(f"   - Mountain scene generated: {len(scene)} characters")
        
        # Test basic question processing
        question = "What's the weather like?"
        history = []
        response = app.process_question(question, history)
        print(f"   - Question processing test: {'✅ Success' if len(response[1]) > 0 else '❌ Failed'}")
        
        return True
    except Exception as e:
        print(f"❌ Gradio app test failed: {e}")
        return False

def test_directory_structure():
    """Test that all required directories exist"""
    print("\n🧪 Testing directory structure...")
    
    required_dirs = [
        "templates",
        "src",
        "src/rag_system",
        "src/data_sources",
        "src/ui"
    ]
    
    all_exist = True
    for directory in required_dirs:
        if Path(directory).exists():
            print(f"✅ {directory} exists")
        else:
            print(f"❌ {directory} missing")
            all_exist = False
    
    return all_exist

def test_required_files():
    """Test that all required files exist"""
    print("\n🧪 Testing required files...")
    
    required_files = [
        "config.py",
        "app.py",
        "requirements.txt",
        "templates/system_prompt.txt",
        "templates/trail_query_prompt.txt",
        "templates/weather_query_prompt.txt",
        "templates/safety_prompt.txt",
        "templates/gear_prompt.txt",
        "templates/permits_prompt.txt",
        "src/rag_system/prompt_manager.py",
        "src/ui/gradio_app.py"
    ]
    
    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            all_exist = False
    
    return all_exist

def main():
    """Run all tests"""
    print("🏔️ Mount Rainier AI Guide - Component Tests")
    print("=" * 50)
    
    tests = [
        ("Directory Structure", test_directory_structure),
        ("Required Files", test_required_files),
        ("Configuration", test_config),
        ("Prompt Manager", test_prompt_manager),
        ("Data Sources", test_data_sources),
        ("Gradio Application", test_gradio_app),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application should work correctly.")
        print("💡 Run 'python app.py' to start the Mount Rainier AI Guide")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("💡 You may need to install dependencies: pip install -r requirements.txt")

if __name__ == "__main__":
    main() 