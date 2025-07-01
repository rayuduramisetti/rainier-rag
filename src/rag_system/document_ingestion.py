#!/usr/bin/env python3
"""
Document Ingestion System for Mount Rainier RAG
Loads and indexes documents into ChromaDB vector store
"""

import os
import asyncio
from typing import List, Dict, Any
from datetime import datetime
import logging

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.vectorstores import Chroma

logger = logging.getLogger(__name__)

class MountRainierDocumentIngestion:
    """Ingests Mount Rainier documents into vector store"""
    
    def __init__(self, vector_db_path: str = "./data/chroma_db", embeddings_model: str = "all-MiniLM-L6-v2"):
        self.vector_db_path = vector_db_path
        self.embeddings = SentenceTransformerEmbeddings(model_name=embeddings_model)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self.vector_store = None
        self._initialize_vector_store()
        
    def _initialize_vector_store(self):
        """Initialize ChromaDB vector store"""
        try:
            os.makedirs(self.vector_db_path, exist_ok=True)
            self.vector_store = Chroma(
                persist_directory=self.vector_db_path,
                embedding_function=self.embeddings
            )
            logger.info(f"Initialized vector store at {self.vector_db_path}")
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
            raise
    
    def get_mount_rainier_documents(self) -> List[Dict[str, Any]]:
        """Get comprehensive Mount Rainier documents for indexing"""
        return [
            {
                "title": "Mount Rainier Overview",
                "content": """Mount Rainier National Park is located in Washington State and features the iconic Mount Rainier, an active stratovolcano standing at 14,411 feet. The mountain is heavily glaciated, with 25 major glaciers and numerous smaller ones covering about 35 square miles. 

The park was established in 1899 as the fifth national park in the United States. It encompasses 369 square miles of diverse ecosystems, from old-growth temperate rainforests to alpine meadows and glacial peaks.

Mount Rainier is considered one of the most dangerous volcanoes in the world due to its proximity to the Seattle-Tacoma metropolitan area. The mountain's extensive glacier system poses additional risks due to potential lahars (volcanic mudflows).

The park receives over 2 million visitors annually, with peak visitation during the summer months of July through September when most high-elevation areas become accessible.""",
                "source": "nps_official",
                "type": "general_info"
            },
            {
                "title": "Popular Hiking Trails",
                "content": """Mount Rainier offers over 260 miles of maintained trails ranging from easy nature walks to strenuous backcountry routes.

**Easy Trails (Under 3 miles):**
- Skyline Trail Loop (1.2 miles): Starting from Paradise, this paved trail offers stunning views of the mountain and subalpine meadows. Elevation gain: 200 feet.
- Silver Falls Trail (3 miles): Beautiful waterfall hike through old-growth forest. Moderate elevation gain of 680 feet.
- Trail of the Shadows (0.7 miles): Historic nature trail at Longmire with interpretive signs about the area's natural and cultural history.

**Moderate Trails (3-8 miles):**
- Tolmie Peak Trail (6.5 miles): Leads to a fire lookout with panoramic views. Elevation gain: 1,010 feet.
- Mount Fremont Lookout (5.6 miles): Historic fire lookout accessible from Sunrise area. Elevation gain: 900 feet.
- Naches Peak Loop (3.5 miles): Scenic loop trail with wildflower meadows and mountain views.

**Difficult Trails (8+ miles):**
- Wonderland Trail (93 miles): Circumnavigates Mount Rainier, typically completed as a 10-14 day backpacking trip.
- Northern Loop Trail (34 miles): Multi-day backpacking route through the park's northern wilderness.
- Spray Park Trail (8 miles): Challenging day hike to spectacular wildflower meadows.""",
                "source": "nps_trails",
                "type": "trails"
            },
            {
                "title": "Weather and Seasonal Information",
                "content": """Mount Rainier's weather is highly variable and can change rapidly, especially at elevation. The mountain creates its own weather patterns and can be shrouded in clouds even when surrounding areas are clear.

**Seasonal Patterns:**
Winter (December-February): Heavy snowfall, with most high-elevation areas inaccessible. Paradise area typically receives 600+ inches of snow annually. Only lower elevation trails remain open.

Spring (March-May): Snowmelt begins, but high elevation areas remain snow-covered. Weather is highly variable with frequent rain and occasional snow. Many trails remain closed due to snow conditions.

Summer (June-August): Best hiking weather with most trails accessible by July. Wildflowers peak in July-August. Temperatures range from 50-70°F at Paradise level. High elevation areas may still have snow patches.

Fall (September-November): Beautiful autumn colors, cooler temperatures, and fewer crowds. First snows typically arrive in October at elevation. Many high-elevation trails close by November.

**Weather Safety:**
- Always check current conditions before hiking
- Weather can change from sunny to stormy within hours
- Hypothermia is possible even in summer
- Carry rain gear and warm layers year-round
- Lightning strikes are common during afternoon thunderstorms""",
                "source": "nps_weather",
                "type": "weather"
            },
            {
                "title": "Mountaineering and Climbing",
                "content": """Mount Rainier is one of the most popular mountaineering destinations in the United States, serving as a training ground for climbers preparing for higher peaks like Denali or Everest.

**Climbing Routes:**
The Disappointment Cleaver route is the most popular, accounting for about 75% of summit attempts. The route typically takes 2-3 days:
- Day 1: Paradise (5,400 ft) to Camp Muir (10,080 ft)
- Day 2: Camp Muir to Columbia Crest summit (14,411 ft) and return

Other popular routes include:
- Emmons Glacier Route: Accessed from White River
- Kautz Glacier Route: Technical route with ice climbing
- Liberty Ridge: Advanced technical climbing route

**Climbing Statistics:**
- Annual summit attempts: ~10,000
- Success rate: Approximately 50%
- Climbing season: May through September
- Required permit: $52 per person

**Climbing Requirements:**
- All climbers above 10,000 feet must register and pay fees
- Skills demonstration may be required for inexperienced climbers
- Recommended gear includes mountaineering boots, crampons, ice axe, helmet, and glacier travel equipment
- Most climbers use guide services for their first attempt

**Hazards:**
- Crevasse falls on glaciated terrain
- Rockfall and icefall
- Altitude sickness above 10,000 feet
- Rapidly changing weather conditions
- Volcanic activity (currently minimal risk)""",
                "source": "nps_climbing",
                "type": "climbing"
            },
            {
                "title": "Wildlife and Flora",
                "content": """Mount Rainier National Park hosts diverse wildlife and plant communities across its elevation zones.

**Large Mammals:**
- Black bears: Present throughout the park, most active in summer and fall
- Mountain goats: Found on rocky slopes and alpine areas
- Elk: Roosevelt elk herds roam the park's forests and meadows
- Deer: Columbia black-tailed deer common in forested areas
- Mountain lions: Present but rarely seen

**Small Mammals:**
- Marmots, pikas, and ground squirrels in alpine areas
- Chipmunks and squirrels in forested zones
- Over 65 mammal species total

**Plant Communities:**
Old-growth forest zone (2,000-4,000 ft): 
- Douglas fir, western hemlock, western red cedar
- Understory of salmonberry, Oregon grape, and ferns

Subalpine zone (4,000-6,500 ft):
- Mountain hemlock, subalpine fir, Alaska yellow cedar
- Seasonal wildflower displays in meadows

Alpine zone (6,500+ ft):
- Hardy plants adapted to extreme conditions
- Cushion plants, alpine grasses, and dwarf willows

**Wildflower Season:**
Peak bloom typically occurs July-August, varying by elevation:
- Lower meadows: Early July
- High alpine areas: Late July to early August
- Common species: lupine, Indian paintbrush, avalanche lily, bear grass""",
                "source": "nps_wildlife",
                "type": "wildlife"
            },
            {
                "title": "Safety and Emergency Information",
                "content": """Mount Rainier's alpine environment presents significant risks that require proper preparation and awareness.

**Emergency Contacts:**
- Emergency: 911
- Park Dispatch: (360) 569-6600
- Climbing Ranger: (360) 569-6641

**Common Hazards:**
1. Hypothermia: Possible year-round due to rapid weather changes
2. Falls: On trails, rocks, and snow/ice
3. Getting lost: Weather can reduce visibility quickly
4. Altitude sickness: Above 8,000 feet
5. Stream crossings: Snowmelt can make streams dangerous
6. Wildlife encounters: Proper food storage required

**Prevention:**
- File trip plans with rangers or family/friends
- Carry the 10 essentials: navigation, sun protection, insulation, illumination, first-aid supplies, fire, repair kit, nutrition, hydration, emergency shelter
- Check weather and trail conditions before departing
- Turn around if conditions deteriorate
- Travel in groups when possible

**Rescue Operations:**
The park has a skilled search and rescue team, but rescue operations can be delayed by weather or terrain. Self-rescue capability is essential.

**Water Safety:**
- All water sources should be treated before drinking
- Giardia and other waterborne pathogens present
- Boiling, filtering, or chemical treatment required

**Lightning Safety:**
- Afternoon thunderstorms common in summer
- Avoid exposed ridges and peaks during storms
- Seek shelter in low areas away from tall objects""",
                "source": "nps_safety",
                "type": "safety"
            },
            {
                "title": "Permits and Regulations",
                "content": """Mount Rainier National Park requires various permits and has specific regulations to protect natural resources and ensure visitor safety.

**Park Entrance Fees:**
- 7-day vehicle pass: $30
- Annual Mount Rainier pass: $55
- America the Beautiful Annual Pass: $80
- Senior Pass (62+): $20 (lifetime)
- Access Pass (disabilities): Free

**Wilderness Camping Permits:**
- Required for all backcountry camping
- Cost: $20 per permit (covers up to 12 people)
- Reservations: Available up to 5 months in advance
- High-demand areas fill quickly, especially summer weekends
- Walk-up permits available but limited

**Climbing Registration:**
- Required for all climbs above 10,000 feet or on glaciated terrain
- Annual climbing fee: $52 per person
- Single climb fee: $52 per person
- Skills check may be required for inexperienced climbers

**General Regulations:**
- Pets allowed on leash on designated trails only
- Firearms prohibited except with proper permits
- Drones prohibited without special use permit
- Collecting natural objects (rocks, plants, etc.) prohibited
- Camping only in designated areas
- Food storage requirements in bear country

**Group Size Limits:**
- Day hiking: 12 people maximum
- Backcountry camping: 12 people maximum
- Commercial groups require special use permits

**Seasonal Closures:**
Many areas close seasonally due to snow conditions:
- Paradise area roads typically close November-May
- Sunrise area typically closes October-June
- High elevation trails may be snow-covered until July""",
                "source": "nps_permits",
                "type": "permits"
            }
        ]
    
    async def ingest_documents(self, force_refresh: bool = False) -> int:
        """Ingest Mount Rainier documents into vector store"""
        if not self.vector_store:
            self._initialize_vector_store()
        
        # Get documents to ingest
        raw_documents = self.get_mount_rainier_documents()
        logger.info(f"Processing {len(raw_documents)} documents for ingestion")
        
        # Convert to LangChain documents and split
        documents = []
        for doc_data in raw_documents:
            # Create LangChain Document
            doc = Document(
                page_content=doc_data["content"],
                metadata={
                    "title": doc_data["title"],
                    "source": doc_data["source"],
                    "type": doc_data["type"],
                    "ingested_at": datetime.now().isoformat()
                }
            )
            
            # Split into chunks
            chunks = self.text_splitter.split_documents([doc])
            documents.extend(chunks)
        
        logger.info(f"Created {len(documents)} document chunks")
        
        # Add documents to vector store
        try:
            self.vector_store.add_documents(documents)
            self.vector_store.persist()
            logger.info(f"Successfully ingested {len(documents)} document chunks into vector store")
            return len(documents)
            
        except Exception as e:
            logger.error(f"Error ingesting documents: {e}")
            raise

if __name__ == "__main__":
    async def main():
        ingestion = MountRainierDocumentIngestion()
        doc_count = await ingestion.ingest_documents(force_refresh=True)
        print(f"Ingested {doc_count} document chunks")
    
    asyncio.run(main()) 