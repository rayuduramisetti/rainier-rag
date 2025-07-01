import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class VisitRainierDataSource:
    """VisitRainier.com integration for regional tourism information"""
    
    def __init__(self):
        self.base_url = "https://visitrainier.com"
        self.cache = {}
        self.cache_duration = timedelta(hours=24)  # Cache for 24 hours
        
    async def get_tourism_data(self) -> List[Dict[str, Any]]:
        """Get comprehensive tourism data from VisitRainier"""
        documents = []
        
        # Get lodging information
        lodging_docs = await self.get_lodging_info()
        documents.extend(lodging_docs)
        
        # Get activities and attractions
        activities_docs = await self.get_activities_info()
        documents.extend(activities_docs)
        
        # Get community information
        community_docs = await self.get_community_info()
        documents.extend(community_docs)
        
        # Get travel information
        travel_docs = await self.get_travel_info()
        documents.extend(travel_docs)
        
        logger.info(f"Retrieved {len(documents)} tourism documents from VisitRainier")
        return documents
    
    async def get_lodging_info(self) -> List[Dict[str, Any]]:
        """Get lodging options around Mount Rainier"""
        cache_key = "lodging_info"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]["data"]
        
        # Sample lodging data based on VisitRainier information
        lodging_options = [
            {
                "name": "Historic Cabins near Paradise",
                "type": "Cabins",
                "location": "Near Paradise Visitor Center",
                "description": "Rustic cabins with mountain views, perfect for families and groups. Easy access to Paradise trails and visitor center.",
                "amenities": ["Mountain views", "Kitchen facilities", "Parking", "Pet-friendly options"],
                "season": "Year-round availability, weather dependent",
                "booking": "Advanced reservations recommended, especially summer months"
            },
            {
                "name": "Ashford Area Lodging",
                "type": "Hotels & B&B",
                "location": "Ashford, WA",
                "description": "Charming accommodations in the gateway community to Mount Rainier. Historic lodges and modern amenities.",
                "amenities": ["Restaurant", "Gift shop", "Hot tub", "WiFi"],
                "season": "Year-round",
                "booking": "visitrainier.com or direct booking"
            }
        ]
        
        documents = []
        for lodging in lodging_options:
            doc_content = f"""
            Lodging Option: {lodging['name']}
            Type: {lodging['type']}
            Location: {lodging['location']}
            
            Description: {lodging['description']}
            
            Amenities: {', '.join(lodging['amenities'])}
            Season: {lodging['season']}
            Booking: {lodging['booking']}
            """
            
            documents.append({
                "content": doc_content,
                "source": "visit_rainier",
                "type": "lodging",
                "category": lodging['type'],
                "timestamp": datetime.now().isoformat()
            })
        
        self.cache[cache_key] = {
            "data": documents,
            "timestamp": datetime.now()
        }
        
        return documents
    
    async def get_activities_info(self) -> List[Dict[str, Any]]:
        """Get activities and attractions information"""
        activities_data = [
            {
                "name": "Mt. Rainier Scenic Gondola",
                "type": "Scenic Attraction",
                "location": "Crystal Mountain",
                "description": "Year-round gondola rides offering spectacular views of Mount Rainier and surrounding peaks.",
                "season": "Year-round",
                "features": ["360-degree views", "Restaurant at summit", "Hiking trail access"]
            },
            {
                "name": "Wildflower Viewing",
                "type": "Nature Activity", 
                "location": "Paradise and Sunrise areas",
                "description": "World-renowned wildflower displays from July through August.",
                "season": "July - September",
                "features": ["Over 130 varieties", "Photography workshops", "Guided tours available"]
            }
        ]
        
        documents = []
        for activity in activities_data:
            doc_content = f"""
            Activity: {activity['name']}
            Type: {activity['type']}
            Location: {activity['location']}
            
            Description: {activity['description']}
            
            Season: {activity['season']}
            Features: {', '.join(activity['features'])}
            """
            
            documents.append({
                "content": doc_content,
                "source": "visit_rainier",
                "type": "activity",
                "category": activity['type'],
                "timestamp": datetime.now().isoformat()
            })
        
        return documents
    
    async def get_community_info(self) -> List[Dict[str, Any]]:
        """Get information about communities around Mount Rainier"""
        communities = [
            {
                "name": "Ashford",
                "description": "Historic gateway community to Mount Rainier National Park.",
                "features": ["Historic lodges", "Restaurants", "Gift shops", "Gas stations"]
            },
            {
                "name": "Enumclaw",
                "description": "Charming city known as the gateway to Mount Rainier from the north.",
                "features": ["Full services", "Hospital", "Shopping", "Restaurants"]
            }
        ]
        
        documents = []
        for community in communities:
            doc_content = f"""
            Community: {community['name']}
            
            Description: {community['description']}
            
            Features and Services: {', '.join(community['features'])}
            """
            
            documents.append({
                "content": doc_content,
                "source": "visit_rainier",
                "type": "community",
                "name": community['name'],
                "timestamp": datetime.now().isoformat()
            })
        
        return documents
    
    async def get_travel_info(self) -> List[Dict[str, Any]]:
        """Get travel and transportation information"""
        travel_info = [
            {
                "title": "Driving Directions",
                "content": """
                From Seattle (90 miles): Take I-5 South to Exit 142A, then follow signs to Mount Rainier.
                From Portland (150 miles): Take I-5 North to Exit 68, then Highway 12 East to Highway 7 North.
                
                Multiple park entrances available:
                - Nisqually Entrance (Highway 706) - Main entrance, year-round access
                - White River Entrance (Highway 410) - Sunrise area access
                """
            },
            {
                "title": "Permits and Passes",
                "content": """
                Park Entrance Fees:
                - Vehicle Pass: $30 (7 days)
                - Motorcycle Pass: $25 (7 days)
                - Individual Pass: $15 (7 days)
                
                Annual Passes:
                - Mount Rainier Annual Pass: $55
                - America the Beautiful Annual Pass: $80
                """
            }
        ]
        
        documents = []
        for info in travel_info:
            documents.append({
                "content": f"{info['title']}\n\n{info['content']}",
                "source": "visit_rainier",
                "type": "travel_info",
                "category": info['title'].lower().replace(' ', '_'),
                "timestamp": datetime.now().isoformat()
            })
        
        return documents
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self.cache:
            return False
        
        cache_time = self.cache[cache_key]["timestamp"]
        return datetime.now() - cache_time < self.cache_duration
    
    async def update_tourism_data(self):
        """Update cached tourism data"""
        await self.get_tourism_data()
        logger.info("Updated VisitRainier tourism data cache") 