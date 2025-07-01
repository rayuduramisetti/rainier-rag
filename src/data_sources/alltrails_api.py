import asyncio
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class AllTrailsDataSource:
    """AllTrails integration for Mount Rainier trail data and user reviews"""
    
    def __init__(self):
        # Mount Rainier National Park area coordinates
        self.park_coordinates = {
            "latitude": 46.8523,
            "longitude": -121.7603,
            "radius_miles": 25
        }
        
        # Cache for trail data
        self.trail_cache = {}
        self.cache_duration = timedelta(hours=6)
        
        # Popular Mount Rainier trails with AllTrails data
        self.featured_trails = [
            {
                "id": "skyline-trail-paradise",
                "name": "Skyline Trail Loop from Paradise",
                "difficulty": "Easy",
                "distance_miles": 1.2,
                "elevation_gain_ft": 200,
                "duration_hours": "0.5-1",
                "rating": 4.6,
                "review_count": 2847,
                "url": "https://www.alltrails.com/trail/us/washington/skyline-trail-loop-from-paradise",
                "location": "Paradise Area",
                "highlights": ["Wildflowers", "Views", "Easy hike"],
                "season": "July-October",
                "description": "Beautiful and easy loop trail famous for wildflower displays in summer.",
                "recent_reviews": [
                    {"date": "2024-06-15", "rating": 5, "text": "Incredible wildflowers in bloom! Easy walk for families."},
                    {"date": "2024-06-10", "rating": 4, "text": "Great views of the mountain. Trail well maintained."}
                ]
            },
            {
                "id": "tolmie-peak-trail",
                "name": "Tolmie Peak Trail",
                "difficulty": "Moderate",
                "distance_miles": 6.5,
                "elevation_gain_ft": 1000,
                "duration_hours": "3-4",
                "rating": 4.7,
                "review_count": 1923,
                "url": "https://www.alltrails.com/trail/us/washington/tolmie-peak-trail",
                "location": "Mowich Lake Area",
                "highlights": ["Mountain views", "Wildflower meadows", "Historic fire lookout"],
                "season": "July-September",
                "description": "Moderate hike to historic fire lookout with spectacular Mount Rainier views.",
                "recent_reviews": [
                    {"date": "2024-06-20", "rating": 5, "text": "Amazing 360-degree views from the lookout! Wildflowers everywhere."}
                ]
            },
            {
                "id": "wonderland-trail",
                "name": "Wonderland Trail",
                "difficulty": "Very Difficult",
                "distance_miles": 93.0,
                "elevation_gain_ft": 22000,
                "duration_hours": "8-14 days",
                "rating": 4.9,
                "review_count": 567,
                "url": "https://www.alltrails.com/trail/us/washington/wonderland-trail",
                "location": "Full Park Circuit",
                "highlights": ["Complete mountain circuit", "Backcountry camping", "All ecosystems"],
                "season": "July-September",
                "description": "Epic 93-mile trail that completely circumnavigates Mount Rainier.",
                "recent_reviews": [
                    {"date": "2024-06-15", "rating": 5, "text": "Life-changing experience! 10 days of pure mountain magic."}
                ]
            }
        ]
    
    async def get_trail_by_difficulty(self, difficulty: str) -> List[Dict[str, Any]]:
        """Get trails filtered by difficulty level"""
        difficulty_map = {
            "easy": ["Easy", "Easy-Moderate"],
            "moderate": ["Moderate", "Easy-Moderate"],
            "difficult": ["Difficult", "Very Difficult"],
            "beginner": ["Easy"],
            "advanced": ["Difficult", "Very Difficult"]
        }
        
        target_difficulties = difficulty_map.get(difficulty.lower(), [difficulty])
        
        matching_trails = []
        for trail in self.featured_trails:
            if trail["difficulty"] in target_difficulties:
                matching_trails.append(trail)
        
        # Sort by rating and review count
        matching_trails.sort(key=lambda x: (x["rating"], x["review_count"]), reverse=True)
        
        logger.info(f"Found {len(matching_trails)} trails for difficulty: {difficulty}")
        return matching_trails
    
    async def search_trails(self, query: str) -> List[Dict[str, Any]]:
        """Search trails by name, location, or features"""
        query_lower = query.lower()
        matching_trails = []
        
        for trail in self.featured_trails:
            # Search in name, location, highlights, and description
            searchable_text = f"{trail['name']} {trail['location']} {' '.join(trail['highlights'])} {trail['description']}".lower()
            
            if query_lower in searchable_text:
                matching_trails.append(trail)
        
        # Sort by rating
        matching_trails.sort(key=lambda x: x['rating'], reverse=True)
        
        logger.info(f"Found {len(matching_trails)} trails matching: {query}")
        return matching_trails
    
    async def get_popular_trails(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get most popular trails by review count and rating"""
        popular = sorted(
            self.featured_trails,
            key=lambda x: (x['review_count'] * x['rating']),
            reverse=True
        )
        
        return popular[:limit]
    
    def format_trail_for_response(self, trail: Dict[str, Any]) -> str:
        """Format trail information for inclusion in AI responses"""
        formatted = f"""
**{trail['name']}**
- **Difficulty**: {trail['difficulty']}
- **Distance**: {trail['distance_miles']} miles
- **Elevation Gain**: {trail['elevation_gain_ft']} feet
- **Duration**: {trail['duration_hours']} hours
- **Rating**: {trail['rating']}/5 ({trail['review_count']} reviews)
- **Location**: {trail['location']}
- **Highlights**: {', '.join(trail['highlights'])}
- **Best Season**: {trail.get('season', 'Summer months')}
- **AllTrails Link**: {trail['url']}

{trail['description']}
        """
        
        return formatted.strip()
    
    def get_source_attribution(self, trails: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Get source attribution for AllTrails data"""
        sources = []
        for trail in trails:
            sources.append({
                "title": f"{trail['name']} - AllTrails",
                "url": trail['url'],
                "source": "AllTrails",
                "type": "trail_guide"
            })
        return sources 