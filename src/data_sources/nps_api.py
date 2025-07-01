import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from langchain.schema import Document

from config import Config

logger = logging.getLogger(__name__)

class NPSDataSource:
    """National Park Service API integration for Mount Rainier"""
    
    def __init__(self):
        self.config = Config()
        self.api_key = self.config.NPS_API_KEY
        self.base_url = "https://developer.nps.gov/api/v1"
        self.park_code = "mora"  # Mount Rainier National Park code
        self.cache = {}
        self.cache_duration = timedelta(hours=6)  # Cache for 6 hours
    
    async def get_park_information(self) -> List[Document]:
        """Get comprehensive park information from NPS API"""
        documents = []
        
        # Get basic park info
        park_info = await self.get_park_details()
        if park_info:
            documents.append(Document(
                page_content=self._format_park_info(park_info),
                metadata={
                    "source": "nps_api",
                    "type": "park_info",
                    "timestamp": datetime.now().isoformat()
                }
            ))
        
        # Get alerts and news
        alerts = await self.get_alerts()
        for alert in alerts:
            documents.append(Document(
                page_content=self._format_alert(alert),
                metadata={
                    "source": "nps_api",
                    "type": "alert",
                    "timestamp": datetime.now().isoformat(),
                    "category": alert.get("category", "general")
                }
            ))
        
        # Get visitor centers info
        visitor_centers = await self.get_visitor_centers()
        for center in visitor_centers:
            documents.append(Document(
                page_content=self._format_visitor_center(center),
                metadata={
                    "source": "nps_api",
                    "type": "visitor_center",
                    "timestamp": datetime.now().isoformat()
                }
            ))
        
        # Get campgrounds info
        campgrounds = await self.get_campgrounds()
        for campground in campgrounds:
            documents.append(Document(
                page_content=self._format_campground(campground),
                metadata={
                    "source": "nps_api",
                    "type": "campground",
                    "timestamp": datetime.now().isoformat()
                }
            ))
        
        logger.info(f"Retrieved {len(documents)} documents from NPS API")
        return documents
    
    async def get_park_details(self) -> Optional[Dict[str, Any]]:
        """Get basic park information"""
        cache_key = "park_details"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]["data"]
        
        try:
            url = f"{self.base_url}/parks"
            params = {
                "parkCode": self.park_code,
                "api_key": self.api_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        parks = data.get("data", [])
                        if parks:
                            park_info = parks[0]
                            self.cache[cache_key] = {
                                "data": park_info,
                                "timestamp": datetime.now()
                            }
                            return park_info
        except Exception as e:
            logger.error(f"Error fetching park details: {e}")
        
        return None
    
    async def get_alerts(self) -> List[Dict[str, Any]]:
        """Get current park alerts and notifications"""
        cache_key = "alerts"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]["data"]
        
        try:
            url = f"{self.base_url}/alerts"
            params = {
                "parkCode": self.park_code,
                "api_key": self.api_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        alerts = data.get("data", [])
                        self.cache[cache_key] = {
                            "data": alerts,
                            "timestamp": datetime.now()
                        }
                        return alerts
        except Exception as e:
            logger.error(f"Error fetching alerts: {e}")
        
        return []
    
    async def get_visitor_centers(self) -> List[Dict[str, Any]]:
        """Get visitor center information"""
        cache_key = "visitor_centers"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]["data"]
        
        try:
            url = f"{self.base_url}/visitorcenters"
            params = {
                "parkCode": self.park_code,
                "api_key": self.api_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        centers = data.get("data", [])
                        self.cache[cache_key] = {
                            "data": centers,
                            "timestamp": datetime.now()
                        }
                        return centers
        except Exception as e:
            logger.error(f"Error fetching visitor centers: {e}")
        
        return []
    
    async def get_campgrounds(self) -> List[Dict[str, Any]]:
        """Get campground information"""
        cache_key = "campgrounds"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]["data"]
        
        try:
            url = f"{self.base_url}/campgrounds"
            params = {
                "parkCode": self.park_code,
                "api_key": self.api_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        campgrounds = data.get("data", [])
                        self.cache[cache_key] = {
                            "data": campgrounds,
                            "timestamp": datetime.now()
                        }
                        return campgrounds
        except Exception as e:
            logger.error(f"Error fetching campgrounds: {e}")
        
        return []
    
    def _format_park_info(self, park_info: Dict[str, Any]) -> str:
        """Format park information for document storage"""
        name = park_info.get("fullName", "Mount Rainier National Park")
        description = park_info.get("description", "")
        weather_info = park_info.get("weatherInfo", "")
        directions = park_info.get("directionsInfo", "")
        
        operating_hours = ""
        if "operatingHours" in park_info and park_info["operatingHours"]:
            hours = park_info["operatingHours"][0]
            operating_hours = f"Operating Hours: {hours.get('description', '')}"
        
        entrance_fees = ""
        if "entranceFees" in park_info and park_info["entranceFees"]:
            fees = park_info["entranceFees"]
            fee_info = []
            for fee in fees:
                fee_info.append(f"{fee.get('title', '')}: ${fee.get('cost', '0')}")
            entrance_fees = "Entrance Fees: " + ", ".join(fee_info)
        
        return f"""
        {name}
        
        Description: {description}
        
        Weather Information: {weather_info}
        
        Directions: {directions}
        
        {operating_hours}
        
        {entrance_fees}
        
        Contact: {park_info.get('contacts', {}).get('phoneNumbers', [{}])[0].get('phoneNumber', 'N/A')}
        
        Website: {park_info.get('url', '')}
        """
    
    def _format_alert(self, alert: Dict[str, Any]) -> str:
        """Format alert information"""
        title = alert.get("title", "Park Alert")
        description = alert.get("description", "")
        category = alert.get("category", "General")
        
        return f"""
        PARK ALERT - {category.upper()}
        
        Title: {title}
        
        Description: {description}
        
        Last Updated: {alert.get('lastIndexedDate', 'Unknown')}
        """
    
    def _format_visitor_center(self, center: Dict[str, Any]) -> str:
        """Format visitor center information"""
        name = center.get("name", "Visitor Center")
        description = center.get("description", "")
        
        operating_hours = ""
        if "operatingHours" in center and center["operatingHours"]:
            hours = center["operatingHours"][0]
            operating_hours = f"Hours: {hours.get('description', '')}"
        
        contact_info = ""
        if "contacts" in center and "phoneNumbers" in center["contacts"]:
            phones = center["contacts"]["phoneNumbers"]
            if phones:
                contact_info = f"Phone: {phones[0].get('phoneNumber', '')}"
        
        return f"""
        {name}
        
        Description: {description}
        
        {operating_hours}
        
        {contact_info}
        
        Location: {center.get('directionsInfo', 'See park website for directions')}
        """
    
    def _format_campground(self, campground: Dict[str, Any]) -> str:
        """Format campground information"""
        name = campground.get("name", "Campground")
        description = campground.get("description", "")
        
        # Get amenities
        amenities = []
        if "amenities" in campground:
            for amenity_type, amenity_list in campground["amenities"].items():
                if amenity_list:
                    amenities.extend([a.get("name", "") for a in amenity_list])
        
        amenities_text = "Amenities: " + ", ".join(amenities) if amenities else ""
        
        # Get reservation info
        reservation_info = ""
        if "reservationInfo" in campground:
            res_info = campground["reservationInfo"]
            reservation_info = f"Reservations: {res_info.get('description', 'See park website')}"
        
        return f"""
        {name} Campground
        
        Description: {description}
        
        {amenities_text}
        
        {reservation_info}
        
        Contact: {campground.get('contacts', {}).get('phoneNumbers', [{}])[0].get('phoneNumber', 'See park website')}
        """
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self.cache:
            return False
        
        cache_time = self.cache[cache_key]["timestamp"]
        return datetime.now() - cache_time < self.cache_duration
    
    async def update_alerts(self):
        """Update alert information"""
        await self.get_alerts()
        logger.info("Updated NPS alerts") 