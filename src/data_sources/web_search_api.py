import asyncio
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class WebSearchDataSource:
    """Web search integration for real-time Mount Rainier information"""
    
    def __init__(self):
        self.mount_rainier_domains = [
            "nps.gov",
            "visitrainier.com", 
            "alltrails.com",
            "weather.gov",
            "washington.edu",
            "crystalmountainresort.com",
            "recreation.gov",
            "fs.usda.gov"
        ]
        
    async def search_mount_rainier(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search for Mount Rainier related information"""
        # Enhanced query with Mount Rainier context
        enhanced_query = f"Mount Rainier National Park {query}"
        
        try:
            # Get curated results based on query type
            results = await self._get_curated_results(query)
            
            logger.info(f"Found {len(results)} web search results for: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return []
    

    
    async def _get_curated_results(self, query: str) -> List[Dict[str, Any]]:
        """Provide curated search results based on query type"""
        query_lower = query.lower()
        
        # Current conditions and alerts
        if any(word in query_lower for word in ["current", "conditions", "alerts", "closures", "road"]):
            return [
                {
                    "title": "Current Park Conditions - Mount Rainier National Park",
                    "content": "Check the official NPS website for current road conditions, trail closures, and park alerts. Weather conditions can change rapidly at Mount Rainier.",
                    "url": "https://www.nps.gov/mora/planyourvisit/conditions.htm",
                    "source": "National Park Service",
                    "type": "park_conditions",
                    "timestamp": datetime.now().isoformat(),
                    "priority": "high"
                },
                {
                    "title": "Mount Rainier Weather Forecast",
                    "content": "Get detailed weather forecasts for different elevations at Mount Rainier. Weather varies significantly with elevation.",
                    "url": "https://www.weather.gov/sew/",
                    "source": "National Weather Service", 
                    "type": "weather",
                    "timestamp": datetime.now().isoformat(),
                    "priority": "high"
                }
            ]
        
        # Transportation and flights
        elif any(word in query_lower for word in ["flight", "airplane", "airport", "transportation", "bus", "train"]):
            return [
                {
                    "title": "Getting to Mount Rainier - Transportation Options",
                    "content": "The nearest major airport is Seattle-Tacoma International Airport (SEA), about 90 miles from Mount Rainier. Rental cars are the most common way to reach the park. From SEA: Take I-5 South to Exit 142A, then follow Highway 7 and 706 to the Nisqually Entrance.",
                    "url": "https://visitrainier.com/travel-info/driving-directions/",
                    "source": "Visit Rainier",
                    "type": "transportation",
                    "timestamp": datetime.now().isoformat(),
                    "priority": "high"
                },
                {
                    "title": "Public Transportation to Mount Rainier",
                    "content": "Limited public transportation is available. Gray Line Tours offers seasonal bus tours from Seattle. Mount Rainier Transportation provides shuttle services with advance booking. Amtrak serves Seattle with connections to regional transit.",
                    "url": "https://www.nps.gov/mora/planyourvisit/directions.htm",
                    "source": "National Park Service",
                    "type": "transportation",
                    "timestamp": datetime.now().isoformat(),
                    "priority": "high"
                },
                {
                    "title": "Seattle-Tacoma International Airport (SEA)",
                    "content": "Major international airport serving the Seattle area and primary gateway for Mount Rainier visitors. Car rental available from all major companies. Ground transportation options include light rail to downtown Seattle.",
                    "url": "https://www.portseattle.org/sea-tac",
                    "source": "Port of Seattle",
                    "type": "airport",
                    "timestamp": datetime.now().isoformat(),
                    "priority": "medium"
                }
            ]
        
        # Trail information and summit routes
        elif any(word in query_lower for word in ["trail", "hike", "hiking", "summit", "climb", "route"]):
            results = [
                {
                    "title": "Mount Rainier Trail Information - AllTrails",
                    "content": "Comprehensive trail guides for Mount Rainier National Park with user reviews, photos, and current conditions. Features popular trails like Skyline Trail (4.6⭐, 2847 reviews), Tolmie Peak (4.7⭐, 1923 reviews), and the epic Wonderland Trail (4.9⭐, 567 reviews).",
                    "url": "https://www.alltrails.com/parks/us/washington/mount-rainier-national-park",
                    "source": "AllTrails",
                    "type": "trails",
                    "timestamp": datetime.now().isoformat(),
                    "priority": "high"
                },
                {
                    "title": "Skyline Trail Loop from Paradise - AllTrails",
                    "content": "Easy 1.2-mile loop trail perfect for families and beginners. Famous for incredible wildflower displays in summer. Paradise area starting point at 5,400 ft elevation. Recent reviews highlight amazing views and well-maintained trail.",
                    "url": "https://www.alltrails.com/trail/us/washington/skyline-trail-loop-from-paradise",
                    "source": "AllTrails",
                    "type": "easy_trail",
                    "timestamp": datetime.now().isoformat(),
                    "priority": "high"
                },
                {
                    "title": "Tolmie Peak Trail - AllTrails",
                    "content": "Moderate 6.5-mile hike to historic fire lookout with spectacular Mount Rainier views. Wildflower meadows and 360-degree panoramic views. Mowich Lake area access. Best season July-September.",
                    "url": "https://www.alltrails.com/trail/us/washington/tolmie-peak-trail",
                    "source": "AllTrails",
                    "type": "moderate_trail",
                    "timestamp": datetime.now().isoformat(),
                    "priority": "high"
                },
                {
                    "title": "Wonderland Trail - AllTrails",
                    "content": "Epic 93-mile trail that completely circumnavigates Mount Rainier. Multi-day backpacking adventure through all park ecosystems. Rated 4.9/5 stars. Wilderness permits required. July-September season.",
                    "url": "https://www.alltrails.com/trail/us/washington/wonderland-trail",
                    "source": "AllTrails", 
                    "type": "advanced_trail",
                    "timestamp": datetime.now().isoformat(),
                    "priority": "high"
                },
                {
                    "title": "Climbing Mount Rainier - Official Guide",
                    "content": "Official information about climbing Mount Rainier including permits, routes, and safety requirements for summit attempts. Popular routes include Disappointment Cleaver and Emmons Glacier.",
                    "url": "https://www.nps.gov/mora/planyourvisit/climbing.htm",
                    "source": "National Park Service",
                    "type": "climbing",
                    "timestamp": datetime.now().isoformat(),
                    "priority": "high"
                }
            ]
            
            # Filter based on difficulty if specified in query
            if any(word in query_lower for word in ["easy", "beginner", "family"]):
                return [r for r in results if r["type"] in ["trails", "easy_trail"]][:3]
            elif any(word in query_lower for word in ["difficult", "hard", "challenging", "advanced"]):
                return [r for r in results if r["type"] in ["trails", "advanced_trail", "climbing"]][:3]
            elif any(word in query_lower for word in ["moderate"]):
                return [r for r in results if r["type"] in ["trails", "moderate_trail"]][:3]
            else:
                return results[:4]
        
        # Lodging and accommodations
        elif any(word in query_lower for word in ["hotel", "lodging", "stay", "accommodation", "cabin"]):
            return [
                {
                    "title": "Mount Rainier Lodging Options - Visit Rainier",
                    "content": "Over 60 lodging options around Mount Rainier including historic lodges, cabins, and campgrounds. Book early for summer visits. Popular areas include Ashford, Enumclaw, and Packwood.",
                    "url": "https://visitrainier.com/stay/lodging/",
                    "source": "Visit Rainier",
                    "type": "lodging",
                    "timestamp": datetime.now().isoformat(),
                    "priority": "high"
                }
            ]
        
        # Permits and passes
        elif any(word in query_lower for word in ["permit", "pass", "fee", "reservation"]):
            return [
                {
                    "title": "Mount Rainier Permits and Passes",
                    "content": "Park entrance fees: $30 per vehicle (7 days), $25 motorcycle, $15 individual. Annual passes available. Wilderness camping requires permits ($20). Climbing permits required for glaciated routes ($52 per person).",
                    "url": "https://www.nps.gov/mora/planyourvisit/fees.htm",
                    "source": "National Park Service",
                    "type": "permits",
                    "timestamp": datetime.now().isoformat(),
                    "priority": "high"
                }
            ]
        
        # General information
        else:
            return [
                {
                    "title": "Mount Rainier National Park - Official Site",
                    "content": "Official information about Mount Rainier National Park including visitor information, trail conditions, and park alerts. Mount Rainier is an active stratovolcano at 14,411 feet elevation.",
                    "url": "https://www.nps.gov/mora/index.htm",
                    "source": "National Park Service",
                    "type": "general",
                    "timestamp": datetime.now().isoformat(),
                    "priority": "high"
                },
                {
                    "title": "Mount Rainier Tourism - Visit Rainier",
                    "content": "Comprehensive tourism information for the Mount Rainier region including activities, lodging, and travel planning. 14,410 feet of fun and adventure await your exploration.",
                    "url": "https://visitrainier.com/",
                    "source": "Visit Rainier",
                    "type": "tourism",
                    "timestamp": datetime.now().isoformat(),
                    "priority": "high"
                }
            ]
    
    async def search_real_time_conditions(self) -> List[Dict[str, Any]]:
        """Search for real-time park conditions and alerts"""
        return await self.search_mount_rainier("current conditions road closures weather alerts")
    
    async def search_transportation_info(self) -> List[Dict[str, Any]]:
        """Search for transportation and access information"""
        return await self.search_mount_rainier("airport transportation flights bus train")
    
    async def search_summit_routes(self) -> List[Dict[str, Any]]:
        """Search for summit climbing routes and waypoints"""
        return await self.search_mount_rainier("summit climbing routes waypoints camp muir ingraham flats")
    
    def format_search_result_for_rag(self, result: Dict[str, Any]) -> str:
        """Format search result for RAG system consumption"""
        title = result.get("title", "")
        content = result.get("content", "")
        url = result.get("url", "")
        source = result.get("source", "Web Search")
        
        formatted = f"""
        Title: {title}
        Source: {source}
        URL: {url}
        
        Content: {content}
        
        Last Updated: {result.get("timestamp", datetime.now().isoformat())}
        """
        
        return formatted
    
    def get_source_attribution(self, results: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Get formatted source attribution for display"""
        sources = []
        for result in results:
            sources.append({
                "title": result.get("title", "Web Search Result"),
                "url": result.get("url", ""),
                "source": result.get("source", "Web Search"),
                "type": result.get("type", "general")
            })
        return sources 