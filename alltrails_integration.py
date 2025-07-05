"""
AllTrails Integration Module
Provides Mount Rainier hiking information and links to AllTrails
"""

import json
from typing import List, Dict, Optional

# Predefined Mount Rainier hikes with metadata
MOUNT_RAINIER_HIKES = [
    {
        "name": "Skyline Trail Loop",
        "url": "https://www.alltrails.com/trail/us/washington/skyline-trail-loop",
        "difficulty": "Moderate",
        "length": "5.5 miles",
        "elevation_gain": "1,700 ft",
        "type": "Loop",
        "description": "Popular trail with stunning views of Mount Rainier and wildflowers in summer",
        "category": "Day Hikes"
    },
    {
        "name": "Burroughs Mountain Trail",
        "url": "https://www.alltrails.com/trail/us/washington/burroughs-mountain-trail",
        "difficulty": "Hard",
        "length": "9.4 miles",
        "elevation_gain": "2,500 ft",
        "type": "Out & Back",
        "description": "Challenging hike with incredible views of Mount Rainier and surrounding peaks",
        "category": "Day Hikes"
    },
    {
        "name": "Naches Peak Loop",
        "url": "https://www.alltrails.com/trail/us/washington/naches-peak-loop",
        "difficulty": "Easy",
        "length": "3.2 miles",
        "elevation_gain": "600 ft",
        "type": "Loop",
        "description": "Easy loop with beautiful wildflowers and views of Mount Rainier",
        "category": "Day Hikes"
    },
    {
        "name": "Mount Fremont Lookout Trail",
        "url": "https://www.alltrails.com/trail/us/washington/mount-fremont-lookout-trail",
        "difficulty": "Moderate",
        "length": "5.7 miles",
        "elevation_gain": "1,200 ft",
        "type": "Out & Back",
        "description": "Historic fire lookout with panoramic views of Mount Rainier",
        "category": "Day Hikes"
    },
    {
        "name": "Tolmie Peak Trail",
        "url": "https://www.alltrails.com/trail/us/washington/tolmie-peak-trail",
        "difficulty": "Moderate",
        "length": "6.5 miles",
        "elevation_gain": "1,100 ft",
        "type": "Out & Back",
        "description": "Beautiful trail to a historic fire lookout with lake views",
        "category": "Day Hikes"
    },
    {
        "name": "Comet Falls Trail",
        "url": "https://www.alltrails.com/trail/us/washington/comet-falls-trail",
        "difficulty": "Moderate",
        "length": "3.8 miles",
        "elevation_gain": "1,250 ft",
        "type": "Out & Back",
        "description": "Spectacular waterfall hike with views of Mount Rainier",
        "category": "Waterfall Hikes"
    },
    {
        "name": "Narada Falls Trail",
        "url": "https://www.alltrails.com/trail/us/washington/narada-falls-trail",
        "difficulty": "Easy",
        "length": "0.2 miles",
        "elevation_gain": "50 ft",
        "type": "Out & Back",
        "description": "Short walk to a beautiful waterfall",
        "category": "Waterfall Hikes"
    },
    {
        "name": "Crystal Lakes Trail",
        "url": "https://www.alltrails.com/trail/us/washington/crystal-lakes-trail",
        "difficulty": "Hard",
        "length": "6.2 miles",
        "elevation_gain": "2,300 ft",
        "type": "Out & Back",
        "description": "Challenging hike to beautiful alpine lakes",
        "category": "Alpine Lakes"
    },
    {
        "name": "Reflection Lakes Trail",
        "url": "https://www.alltrails.com/trail/us/washington/reflection-lakes-trail",
        "difficulty": "Easy",
        "length": "3.0 miles",
        "elevation_gain": "200 ft",
        "type": "Loop",
        "description": "Easy lakeside trail with perfect Mount Rainier reflections",
        "category": "Alpine Lakes"
    },
    {
        "name": "Wonderland Trail",
        "url": "https://www.alltrails.com/trail/us/washington/wonderland-trail",
        "difficulty": "Hard",
        "length": "93.0 miles",
        "elevation_gain": "22,000 ft",
        "type": "Loop",
        "description": "Epic multi-day backpacking trail around Mount Rainier",
        "category": "Backpacking"
    },
    {
        "name": "Northern Loop Trail",
        "url": "https://www.alltrails.com/trail/us/washington/northern-loop-trail",
        "difficulty": "Hard",
        "length": "35.0 miles",
        "elevation_gain": "8,000 ft",
        "type": "Loop",
        "description": "Challenging multi-day backpacking route in the northern part of the park",
        "category": "Backpacking"
    },
    {
        "name": "Grove of the Patriarchs Trail",
        "url": "https://www.alltrails.com/trail/us/washington/grove-of-the-patriarchs-trail",
        "difficulty": "Easy",
        "length": "1.1 miles",
        "elevation_gain": "50 ft",
        "type": "Loop",
        "description": "Easy walk through ancient giant trees",
        "category": "Family Friendly"
    },
    {
        "name": "Silver Falls Trail",
        "url": "https://www.alltrails.com/trail/us/washington/silver-falls-trail",
        "difficulty": "Easy",
        "length": "3.0 miles",
        "elevation_gain": "400 ft",
        "type": "Loop",
        "description": "Family-friendly trail to a beautiful waterfall",
        "category": "Family Friendly"
    }
]

# AllTrails category pages
ALLTRAILS_CATEGORIES = {
    "Mount Rainier National Park": "https://www.alltrails.com/parks/us/washington/mount-rainier-national-park",
    "Day Hikes": "https://www.alltrails.com/parks/us/washington/mount-rainier-national-park?activityType=hiking&difficulty=moderate&length=1-10",
    "Waterfall Hikes": "https://www.alltrails.com/parks/us/washington/mount-rainier-national-park?activityType=hiking&poiType=waterfall",
    "Alpine Lakes": "https://www.alltrails.com/parks/us/washington/mount-rainier-national-park?activityType=hiking&poiType=lake",
    "Backpacking": "https://www.alltrails.com/parks/us/washington/mount-rainier-national-park?activityType=hiking&length=10-50",
    "Family Friendly": "https://www.alltrails.com/parks/us/washington/mount-rainier-national-park?activityType=hiking&difficulty=easy&length=0-5"
}


class AllTrailsIntegration:
    """AllTrails integration for Mount Rainier hiking information"""
    
    def __init__(self):
        self.hikes = MOUNT_RAINIER_HIKES
        self.categories = ALLTRAILS_CATEGORIES
    
    def get_all_hikes(self) -> List[Dict]:
        """Get all available hikes"""
        return self.hikes
    
    def get_hikes_by_category(self, category: str) -> List[Dict]:
        """Get hikes filtered by category"""
        return [hike for hike in self.hikes if hike.get("category") == category]
    
    def get_hikes_by_difficulty(self, difficulty: str) -> List[Dict]:
        """Get hikes filtered by difficulty"""
        return [hike for hike in self.hikes if hike.get("difficulty") == difficulty]
    
    def search_hikes(self, query: str) -> List[Dict]:
        """Search hikes by name or description"""
        query = query.lower()
        results = []
        for hike in self.hikes:
            if (query in hike["name"].lower() or 
                query in hike["description"].lower() or
                query in hike["category"].lower()):
                results.append(hike)
        return results
    
    def get_categories(self) -> Dict[str, str]:
        """Get available categories with their AllTrails URLs"""
        return self.categories
    
    def get_hike_details(self, hike_name: str) -> Optional[Dict]:
        """Get detailed information for a specific hike"""
        for hike in self.hikes:
            if hike["name"].lower() == hike_name.lower():
                return hike
        return None
    
    def get_recommendations(self, difficulty: str = None, max_length: float = None) -> List[Dict]:
        """Get hike recommendations based on criteria"""
        recommendations = self.hikes.copy()
        
        if difficulty:
            recommendations = [h for h in recommendations if h["difficulty"] == difficulty]
        
        if max_length:
            recommendations = [h for h in recommendations if 
                             float(h["length"].split()[0]) <= max_length]
        
        return recommendations[:5]  # Return top 5 recommendations


def format_hike_info(hike: Dict) -> str:
    """Format hike information for display as HTML"""
    info = f"<strong>{hike['name']}</strong> ({hike['difficulty']}, {hike['length']})<br/>"
    info += f"{hike['description']}<br/>"
    info += f"🔗 <a href=\"{hike['url']}\" target=\"_blank\">View on AllTrails</a><br/><br/>"
    return info


def get_alltrails_response(query: str) -> str:
    """Generate a response about AllTrails hikes based on user query, using HTML formatting"""
    integration = AllTrailsIntegration()
    query_lower = query.lower()
    
    # Check for specific hike requests
    if "hike" in query_lower or "trail" in query_lower:
        if "easy" in query_lower or "family" in query_lower:
            hikes = integration.get_hikes_by_difficulty("Easy")
            response = "<strong>Here are some easy, family-friendly hikes in Mount Rainier National Park:</strong><br/><br/>"
        elif "moderate" in query_lower:
            hikes = integration.get_hikes_by_difficulty("Moderate")
            response = "<strong>Here are some moderate hikes in Mount Rainier National Park:</strong><br/><br/>"
        elif "hard" in query_lower or "challenging" in query_lower:
            hikes = integration.get_hikes_by_difficulty("Hard")
            response = "<strong>Here are some challenging hikes in Mount Rainier National Park:</strong><br/><br/>"
        elif "waterfall" in query_lower:
            hikes = integration.get_hikes_by_category("Waterfall Hikes")
            response = "<strong>Here are some waterfall hikes in Mount Rainier National Park:</strong><br/><br/>"
        elif "lake" in query_lower:
            hikes = integration.get_hikes_by_category("Alpine Lakes")
            response = "<strong>Here are some alpine lake hikes in Mount Rainier National Park:</strong><br/><br/>"
        elif "backpacking" in query_lower or "multi-day" in query_lower:
            hikes = integration.get_hikes_by_category("Backpacking")
            response = "<strong>Here are some backpacking options in Mount Rainier National Park:</strong><br/><br/>"
        else:
            hikes = integration.get_recommendations()
            response = "<strong>Here are some popular hikes in Mount Rainier National Park:</strong><br/><br/>"
        
        for i, hike in enumerate(hikes[:5], 1):
            response += f"{i}. {format_hike_info(hike)}"
        
        response += f"📋 <strong>Browse all hikes:</strong> <a href=\"{integration.categories['Mount Rainier National Park']}\" target=\"_blank\">Mount Rainier on AllTrails</a>"
    else:
        response = "<strong>AllTrails Mount Rainier National Park</strong><br/><br/>"
        response += "AllTrails is a great resource for discovering and planning hikes in Mount Rainier National Park. "
        response += "You can find detailed trail information, reviews, photos, and more.<br/><br/>"
        response += "<strong>Popular Categories:</strong><br/>"
        for category, url in integration.categories.items():
            response += f"• <a href=\"{url}\" target=\"_blank\">{category}</a><br/>"
        response += f"<br/><strong>Browse all trails:</strong> <a href=\"{integration.categories['Mount Rainier National Park']}\" target=\"_blank\">Mount Rainier National Park</a>"
    return response


if __name__ == "__main__":
    # Test the integration
    integration = AllTrailsIntegration()
    print(f"Total hikes: {len(integration.get_all_hikes())}")
    print(f"Easy hikes: {len(integration.get_hikes_by_difficulty('Easy'))}")
    print(f"Waterfall hikes: {len(integration.get_hikes_by_category('Waterfall Hikes'))}")
    
    # Test search
    results = integration.search_hikes("skyline")
    print(f"Search results for 'skyline': {len(results)}")
    if results:
        print(format_hike_info(results[0])) 