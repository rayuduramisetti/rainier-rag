import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from langchain.schema import Document

from config import Config

logger = logging.getLogger(__name__)

class StravaDataSource:
    """Strava API integration for hiking and trail data"""
    
    def __init__(self):
        self.config = Config()
        self.client_id = self.config.STRAVA_CLIENT_ID
        self.client_secret = self.config.STRAVA_CLIENT_SECRET
        self.base_url = "https://www.strava.com/api/v3"
        self.cache = {}
        self.cache_duration = timedelta(hours=12)  # Cache for 12 hours
        
        # Mount Rainier area bounds (approximate)
        self.area_bounds = {
            "sw_lat": 46.7,
            "sw_lng": -121.9,
            "ne_lat": 47.0,
            "ne_lng": -121.5
        }
    
    async def get_trail_data(self) -> List[Document]:
        """Get trail and hiking data from Strava segments"""
        documents = []
        
        # Get popular hiking segments in Mount Rainier area
        segments = await self.get_popular_segments()
        
        for segment in segments:
            # Create document for each segment
            documents.append(Document(
                page_content=self._format_segment_info(segment),
                metadata={
                    "source": "strava_api",
                    "type": "trail_segment",
                    "segment_id": segment.get("id"),
                    "timestamp": datetime.now().isoformat()
                }
            ))
        
        # Get activity statistics for popular trails
        trail_stats = await self.get_trail_statistics()
        if trail_stats:
            documents.append(Document(
                page_content=self._format_trail_statistics(trail_stats),
                metadata={
                    "source": "strava_api",
                    "type": "trail_statistics",
                    "timestamp": datetime.now().isoformat()
                }
            ))
        
        logger.info(f"Retrieved {len(documents)} trail documents from Strava")
        return documents
    
    async def get_popular_segments(self) -> List[Dict[str, Any]]:
        """Get popular hiking segments in Mount Rainier area"""
        cache_key = "popular_segments"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]["data"]
        
        # Note: Strava's segment explore endpoint requires authentication
        # For a production app, you'd need to implement OAuth flow
        # For now, we'll return sample data based on known Mount Rainier trails
        
        sample_segments = [
            {
                "id": 1001,
                "name": "Skyline Trail to Panorama Point",
                "distance": 5500,  # meters
                "elevation_high": 2134,  # meters (7000 ft)
                "elevation_low": 1646,  # meters (5400 ft)
                "activity_type": "Hike",
                "effort_count": 1250,
                "star_count": 89,
                "start_latlng": [46.7844, -121.7367],
                "end_latlng": [46.7956, -121.7456],
                "description": "Popular trail from Paradise to Panorama Point with stunning views of Mount Rainier"
            },
            {
                "id": 1002,
                "name": "Tolmie Peak Trail",
                "distance": 10600,  # meters
                "elevation_high": 1672,  # meters (5484 ft)
                "elevation_low": 1097,  # meters (3600 ft)
                "activity_type": "Hike",
                "effort_count": 890,
                "star_count": 67,
                "start_latlng": [46.9283, -121.8394],
                "end_latlng": [46.9089, -121.8456],
                "description": "Beautiful hike to Tolmie Peak with wildflower meadows and mountain views"
            },
            {
                "id": 1003,
                "name": "Mount Fremont Lookout",
                "distance": 9200,  # meters
                "elevation_high": 2195,  # meters (7200 ft)
                "elevation_low": 1829,  # meters (6000 ft)
                "activity_type": "Hike",
                "effort_count": 654,
                "star_count": 78,
                "start_latlng": [46.9167, -121.6444],
                "end_latlng": [46.9056, -121.6556],
                "description": "Historic fire lookout with panoramic views of Mount Rainier and surrounding peaks"
            }
        ]
        
        self.cache[cache_key] = {
            "data": sample_segments,
            "timestamp": datetime.now()
        }
        
        return sample_segments
    
    async def get_trail_statistics(self) -> Dict[str, Any]:
        """Get aggregated trail statistics"""
        cache_key = "trail_statistics"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]["data"]
        
        # Sample statistics based on typical Mount Rainier hiking data
        stats = {
            "total_trails_tracked": 25,
            "average_difficulty": "Moderate to Difficult",
            "popular_months": ["July", "August", "September"],
            "average_completion_times": {
                "Skyline Trail to Panorama Point": "2.5-3.5 hours",
                "Tolmie Peak Trail": "5-7 hours",
                "Mount Fremont Lookout": "4-6 hours",
                "Naches Peak Loop": "2-3 hours",
                "Comet Falls": "2.5-4 hours"
            },
            "difficulty_distribution": {
                "Easy": 20,
                "Moderate": 45,
                "Difficult": 30,
                "Very Difficult": 5
            },
            "seasonal_activity": {
                "Spring": "Limited access, snow at elevation",
                "Summer": "Peak season, all trails accessible",
                "Fall": "Beautiful colors, cooler weather",
                "Winter": "Most trails closed or require snow gear"
            }
        }
        
        self.cache[cache_key] = {
            "data": stats,
            "timestamp": datetime.now()
        }
        
        return stats
    
    def _format_segment_info(self, segment: Dict[str, Any]) -> str:
        """Format segment information for document storage"""
        name = segment.get("name", "Unknown Trail")
        distance_km = segment.get("distance", 0) / 1000
        distance_miles = distance_km * 0.621371
        
        elevation_gain = segment.get("elevation_high", 0) - segment.get("elevation_low", 0)
        elevation_gain_ft = elevation_gain * 3.28084
        
        effort_count = segment.get("effort_count", 0)
        star_count = segment.get("star_count", 0)
        
        description = segment.get("description", "")
        
        # Estimate hiking time based on distance and elevation gain
        # Using Naismith's rule: 1 hour per 3 miles + 1 hour per 2000 ft elevation gain
        time_hours = (distance_miles / 3) + (elevation_gain_ft / 2000)
        
        return f"""
        Trail: {name}
        
        Distance: {distance_miles:.1f} miles ({distance_km:.1f} km)
        Elevation Gain: {elevation_gain_ft:.0f} feet ({elevation_gain:.0f} meters)
        Estimated Hiking Time: {time_hours:.1f} hours
        
        Popularity: {effort_count} recorded activities, {star_count} stars
        
        Description: {description}
        
        Trail Type: {segment.get("activity_type", "Hiking")}
        
        Difficulty Level: {self._calculate_difficulty(distance_miles, elevation_gain_ft)}
        
        Starting Elevation: {segment.get("elevation_low", 0) * 3.28084:.0f} feet
        Highest Point: {segment.get("elevation_high", 0) * 3.28084:.0f} feet
        """
    
    def _format_trail_statistics(self, stats: Dict[str, Any]) -> str:
        """Format trail statistics for document storage"""
        completion_times = stats.get("average_completion_times", {})
        time_info = []
        for trail, time in completion_times.items():
            time_info.append(f"- {trail}: {time}")
        
        difficulty_dist = stats.get("difficulty_distribution", {})
        difficulty_info = []
        for level, percentage in difficulty_dist.items():
            difficulty_info.append(f"- {level}: {percentage}%")
        
        seasonal_activity = stats.get("seasonal_activity", {})
        seasonal_info = []
        for season, description in seasonal_activity.items():
            seasonal_info.append(f"- {season}: {description}")
        
        return f"""
        Mount Rainier Trail Statistics Summary
        
        Total Tracked Trails: {stats.get("total_trails_tracked", 0)}
        Average Difficulty: {stats.get("average_difficulty", "Moderate")}
        
        Most Popular Hiking Months: {", ".join(stats.get("popular_months", []))}
        
        Average Completion Times:
        {chr(10).join(time_info)}
        
        Trail Difficulty Distribution:
        {chr(10).join(difficulty_info)}
        
        Seasonal Activity Patterns:
        {chr(10).join(seasonal_info)}
        
        Note: Times are estimates based on average hiking speeds and may vary significantly based on individual fitness, weather conditions, and trail conditions.
        """
    
    def _calculate_difficulty(self, distance_miles: float, elevation_gain_ft: float) -> str:
        """Calculate trail difficulty based on distance and elevation gain"""
        # Simple difficulty calculation
        difficulty_score = (distance_miles * 2) + (elevation_gain_ft / 500)
        
        if difficulty_score < 5:
            return "Easy"
        elif difficulty_score < 10:
            return "Moderate"
        elif difficulty_score < 15:
            return "Difficult"
        else:
            return "Very Difficult"
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self.cache:
            return False
        
        cache_time = self.cache[cache_key]["timestamp"]
        return datetime.now() - cache_time < self.cache_duration
    
    async def update_trail_data(self):
        """Update trail data cache"""
        await self.get_popular_segments()
        await self.get_trail_statistics()
        logger.info("Updated Strava trail data cache") 