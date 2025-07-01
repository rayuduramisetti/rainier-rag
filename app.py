"""
Mount Rainier AI Guide - Main Application
A comprehensive RAG system for Mount Rainier National Park information
"""

import logging
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from config import Config, ENV_TEMPLATE
from src.ui.gradio_app import launch_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mount_rainier_guide.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def check_environment():
    """Check if environment is properly configured"""
    if not Config.validate():
        print("⚠️  Environment configuration incomplete!")
        print("\n📝 Please create a .env file with the following template:")
        print(ENV_TEMPLATE)
        print("\n🔑 Required API Keys:")
        print("- OpenAI API Key (required)")
        print("- Weather API Key (optional - from openweathermap.org)")
        print("- NPS API Key (optional - from nps.gov/subjects/developer)")
        print("- Strava API credentials (optional)")
        print("\n💡 The app will work with just the OpenAI API key for basic functionality.")
        
        # Continue anyway for demo purposes
        return True
    
    return True

def setup_directories():
    """Create necessary directories"""
    directories = [
        "data",
        "data/chroma_db", 
        "static/css",
        "static/js",
        "static/images"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    logger.info("Created necessary directories")

def main():
    """Main application entry point"""
    logger.info("Starting Mount Rainier AI Guide...")
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Setup directories
    setup_directories()
    
    # Print startup information
    print("🏔️ " + "="*60)
    print("🏔️  MOUNT RAINIER AI GUIDE")
    print("🏔️  Your intelligent companion for exploring Mount Rainier National Park")
    print("🏔️ " + "="*60)
    print()
    print("🚀 Starting the application...")
    print("📱 Once started, you can access the app through the provided URL")
    print("🌐 A shareable public link will also be created")
    print()
    print("✨ Features:")
    print("   • Real-time weather information")
    print("   • Trail recommendations and difficulty ratings")
    print("   • Permit and gear guidance")
    print("   • Animated hiking scene with day/night cycles")
    print("   • Safety-focused advice from park experts")
    print()
    
    try:
        # Launch the Gradio app
        launch_app()
    except KeyboardInterrupt:
        print("\n👋 Thanks for using Mount Rainier AI Guide!")
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 