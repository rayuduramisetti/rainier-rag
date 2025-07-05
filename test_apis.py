#!/usr/bin/env python3
"""
Test script for Weather and NPS API integration
"""

import asyncio
import sys
from config import Config

async def test_weather_api():
    """Test weather API integration"""
    print("🌤️ Testing Weather API...")
    
    try:
        from src.data_sources.weather_api import WeatherDataSource
        
        weather = WeatherDataSource()
        
        # Check if API key is set
        if not weather.api_key or weather.api_key == "your_weather_api_key_here":
            print("❌ Weather API key not set in .env file")
            print("   Get free key from: https://openweathermap.org/")
            return False
        
        print(f"✅ Weather API key found: {weather.api_key[:10]}...")
        
        # Test current weather
        print("🌡️ Fetching current weather...")
        current_weather = await weather.get_current_weather()
        
        if current_weather and current_weather.get('temperature'):
            temp = current_weather['temperature']['current']
            conditions = current_weather['conditions']['description']
            location = current_weather['location']
            
            print(f"✅ Weather API working!")
            print(f"   Location: {location}")
            print(f"   Temperature: {temp}°F")
            print(f"   Conditions: {conditions}")
            return True
        else:
            print("❌ Weather API returned invalid data")
            return False
            
    except Exception as e:
        print(f"❌ Weather API error: {e}")
        return False

async def test_nps_api():
    """Test NPS API integration"""
    print("\n🏞️ Testing NPS API...")
    
    try:
        from src.data_sources.nps_api import NPSDataSource
        
        nps = NPSDataSource()
        
        # Check if API key is set
        if not nps.api_key or nps.api_key == "your_nps_api_key_here":
            print("❌ NPS API key not set in .env file")
            print("   Get free key from: https://www.nps.gov/subjects/developer/get-started.htm")
            return False
        
        print(f"✅ NPS API key found: {nps.api_key[:10]}...")
        
        # Test park info
        print("🏔️ Fetching Mount Rainier park info...")
        park_info = await nps.get_park_details()
        
        if park_info and park_info.get('name'):
            name = park_info['name']
            description = park_info.get('description', '')[:100] + "..."
            
            print(f"✅ NPS API working!")
            print(f"   Park: {name}")
            print(f"   Description: {description}")
            return True
        else:
            print("❌ NPS API returned invalid data")
            return False
            
    except Exception as e:
        print(f"❌ NPS API error: {e}")
        return False

async def main():
    """Main test function"""
    print("🔧 API Integration Test")
    print("=" * 50)
    
    # Test weather API
    weather_ok = await test_weather_api()
    
    # Test NPS API
    nps_ok = await test_nps_api()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   Weather API: {'✅ Working' if weather_ok else '❌ Failed'}")
    print(f"   NPS API: {'✅ Working' if nps_ok else '❌ Failed'}")
    
    if not weather_ok or not nps_ok:
        print("\n🔧 Setup Instructions:")
        print("1. Get free API keys from the websites above")
        print("2. Update your .env file with the real keys")
        print("3. Restart the application")
    else:
        print("\n🎉 All APIs working! Ready to test the full application.")

if __name__ == "__main__":
    asyncio.run(main()) 