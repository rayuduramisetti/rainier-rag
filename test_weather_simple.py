#!/usr/bin/env python3
import asyncio
from src.data_sources.weather_api import WeatherDataSource

async def test_weather():
    weather = WeatherDataSource()
    if weather.api_key:
        print(f"Weather API Key: {weather.api_key[:10]}...")
    else:
        print("Weather API Key: Not set")
        return
    
    try:
        result = await weather.get_current_weather()
        print(f"Temperature: {result.get('temperature', 'N/A')}")
        print(f"Conditions: {result.get('conditions', 'N/A')}")
        print(f"Location: {result.get('location', 'N/A')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_weather()) 