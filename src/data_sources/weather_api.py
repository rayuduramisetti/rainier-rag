import asyncio
import aiohttp
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from config import Config

logger = logging.getLogger(__name__)

class WeatherDataSource:
    """Weather API integration for Mount Rainier area"""
    
    def __init__(self):
        self.config = Config()
        self.api_key = self.config.WEATHER_API_KEY
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.coords = self.config.PARK_COORDINATES  # Mount Rainier coordinates
        self.cache = {}
        self.cache_duration = timedelta(minutes=15)  # Cache for 15 minutes
    
    async def get_current_weather(self) -> Dict[str, Any]:
        """Get current weather conditions for Mount Rainier area"""
        cache_key = "current_weather"
        
        # Check cache first
        if self._is_cache_valid(cache_key):
            logger.info("Returning cached weather data")
            return self.cache[cache_key]["data"]
        
        try:
            url = f"{self.base_url}/weather"
            params = {
                "lat": self.coords[0],
                "lon": self.coords[1],
                "appid": self.api_key,
                "units": "imperial"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        weather_info = self._format_current_weather(data)
                        
                        # Cache the result
                        self.cache[cache_key] = {
                            "data": weather_info,
                            "timestamp": datetime.now()
                        }
                        
                        logger.info("Retrieved current weather data")
                        return weather_info
                    else:
                        logger.error(f"Weather API error: {response.status}")
                        return self._get_fallback_weather()
        
        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            return self._get_fallback_weather()
    
    async def get_weather_forecast(self, days: int = 5) -> Dict[str, Any]:
        """Get weather forecast for Mount Rainier area"""
        cache_key = f"forecast_{days}days"
        
        # Check cache first
        if self._is_cache_valid(cache_key):
            logger.info("Returning cached forecast data")
            return self.cache[cache_key]["data"]
        
        try:
            url = f"{self.base_url}/forecast"
            params = {
                "lat": self.coords[0],
                "lon": self.coords[1],
                "appid": self.api_key,
                "units": "imperial"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        forecast_info = self._format_forecast(data, days)
                        
                        # Cache the result
                        self.cache[cache_key] = {
                            "data": forecast_info,
                            "timestamp": datetime.now()
                        }
                        
                        logger.info(f"Retrieved {days}-day forecast data")
                        return forecast_info
                    else:
                        logger.error(f"Forecast API error: {response.status}")
                        return self._get_fallback_forecast()
        
        except Exception as e:
            logger.error(f"Error fetching forecast data: {e}")
            return self._get_fallback_forecast()
    
    def _format_current_weather(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format raw weather API data into useful information"""
        try:
            main = data.get("main", {})
            weather = data.get("weather", [{}])[0]
            wind = data.get("wind", {})
            clouds = data.get("clouds", {})
            
            return {
                "temperature": {
                    "current": round(main.get("temp", 0)),
                    "feels_like": round(main.get("feels_like", 0)),
                    "min": round(main.get("temp_min", 0)),
                    "max": round(main.get("temp_max", 0))
                },
                "conditions": {
                    "main": weather.get("main", "Unknown"),
                    "description": weather.get("description", "").title(),
                    "icon": weather.get("icon", "")
                },
                "wind": {
                    "speed": round(wind.get("speed", 0)),
                    "direction": wind.get("deg", 0)
                },
                "humidity": main.get("humidity", 0),
                "pressure": main.get("pressure", 0),
                "clouds": clouds.get("all", 0),
                "visibility": data.get("visibility", 0) / 1000,  # Convert to km
                "sunrise": datetime.fromtimestamp(data.get("sys", {}).get("sunrise", 0)),
                "sunset": datetime.fromtimestamp(data.get("sys", {}).get("sunset", 0)),
                "location": data.get("name", "Mount Rainier Area"),
                "timestamp": datetime.now(),
                "elevation_notes": self._get_elevation_weather_notes()
            }
        except Exception as e:
            logger.error(f"Error formatting weather data: {e}")
            return self._get_fallback_weather()
    
    def _format_forecast(self, data: Dict[str, Any], days: int) -> Dict[str, Any]:
        """Format forecast data"""
        try:
            forecasts = []
            forecast_list = data.get("list", [])
            
            # Group by day and take midday forecast
            current_date = None
            for item in forecast_list[:days * 8]:  # 8 forecasts per day (3-hour intervals)
                forecast_time = datetime.fromtimestamp(item.get("dt", 0))
                forecast_date = forecast_time.date()
                
                # Take the midday forecast (around 12 PM)
                if forecast_time.hour == 12 or (current_date != forecast_date and len(forecasts) < days):
                    if current_date != forecast_date:
                        main = item.get("main", {})
                        weather = item.get("weather", [{}])[0]
                        wind = item.get("wind", {})
                        
                        forecasts.append({
                            "date": forecast_date,
                            "temperature": {
                                "high": round(main.get("temp_max", 0)),
                                "low": round(main.get("temp_min", 0))
                            },
                            "conditions": {
                                "main": weather.get("main", "Unknown"),
                                "description": weather.get("description", "").title()
                            },
                            "wind_speed": round(wind.get("speed", 0)),
                            "precipitation_chance": item.get("pop", 0) * 100
                        })
                        current_date = forecast_date
            
            return {
                "forecasts": forecasts,
                "location": "Mount Rainier Area",
                "timestamp": datetime.now()
            }
        except Exception as e:
            logger.error(f"Error formatting forecast data: {e}")
            return self._get_fallback_forecast()
    
    def _get_elevation_weather_notes(self) -> str:
        """Get elevation-specific weather notes"""
        return """Weather conditions vary significantly with elevation:
        - Base elevation (2000-3000 ft): Milder conditions, rain more likely than snow
        - Mid-elevation (5000-8000 ft): 10-20°F cooler, snow possible year-round
        - High elevation (8000+ ft): 20-30°F cooler, snow likely, strong winds common
        - Summit (14,411 ft): Extreme conditions, temperatures can be 40-50°F below base"""
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self.cache:
            return False
        
        cache_time = self.cache[cache_key]["timestamp"]
        return datetime.now() - cache_time < self.cache_duration
    
    def _get_fallback_weather(self) -> Dict[str, Any]:
        """Return fallback weather data when API is unavailable"""
        return {
            "temperature": {"current": "N/A", "feels_like": "N/A", "min": "N/A", "max": "N/A"},
            "conditions": {"main": "Unknown", "description": "Weather data temporarily unavailable"},
            "wind": {"speed": "N/A", "direction": "N/A"},
            "humidity": "N/A",
            "pressure": "N/A",
            "clouds": "N/A",
            "visibility": "N/A",
            "location": "Mount Rainier Area",
            "timestamp": datetime.now(),
            "elevation_notes": self._get_elevation_weather_notes(),
            "note": "Please check current conditions before hiking"
        }
    
    def _get_fallback_forecast(self) -> Dict[str, Any]:
        """Return fallback forecast data when API is unavailable"""
        return {
            "forecasts": [],
            "location": "Mount Rainier Area",
            "timestamp": datetime.now(),
            "note": "Forecast data temporarily unavailable. Please check current conditions before hiking."
        }
    
    async def update_weather_data(self):
        """Update cached weather data"""
        await self.get_current_weather()
        await self.get_weather_forecast()
        logger.info("Updated weather cache") 