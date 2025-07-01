# 🏔️ Mount Rainier AI Guide

A comprehensive RAG (Retrieval-Augmented Generation) system that serves as your intelligent companion for exploring Mount Rainier National Park. This application combines real-time data from multiple sources with AI-powered responses to provide accurate, safety-focused guidance for hikers and visitors.

## ✨ Features

### 🎨 Beautiful Animated UI
- **Continuous hiking animation** with a hiker moving up and down Mount Rainier
- **Dynamic day/night cycles** that change the visual atmosphere
- **Real-time elevation tracking** showing the hiker's current position
- **Weather-responsive scenes** that reflect current conditions
- **Thinking animations** when processing questions

### 🧠 Intelligent RAG System
- **Multi-source data integration** from NPS, weather APIs, trail databases, and web search
- **Real-time web search** for current conditions, alerts, and transportation info
- **Source attribution** with clickable links to official websites
- **Contextual responses** tailored to query type (trails, weather, safety, gear, permits)
- **Real-time weather integration** with elevation-specific forecasts
- **Transportation guidance** for flights, airports, buses, trains, and driving directions
- **Summit route mapping** with detailed waypoints from Paradise to Columbia Crest
- **Safety-first approach** prioritizing visitor safety in all recommendations
- **Modular prompt templates** for easy customization and updates

### 📊 Comprehensive Data Sources
- **AllTrails Integration** for detailed trail data, user reviews, and current conditions
- **National Park Service API** for official park information and alerts
- **Weather API** for real-time conditions and forecasts
- **Strava API** for popular trail data and difficulty ratings
- **Web Search Integration** for real-time information and current conditions
- **Transportation APIs** for flights, public transit, and driving directions
- **Static knowledge base** with curated Mount Rainier information
- **Source attribution** showing users exactly where information comes from

### 🛡️ Safety-Focused Design
- **Emergency contact information** always readily available
- **Risk assessment** based on current conditions
- **Gear recommendations** tailored to seasons and trail difficulty
- **Weather warnings** and condition-based trail advice

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key (required)
- Weather API key (optional - from OpenWeatherMap)
- NPS API key (optional - from nps.gov)
- Strava API credentials (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd mount-rainer-rag
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   WEATHER_API_KEY=your_weather_api_key_here
   NPS_API_KEY=your_nps_api_key_here
   STRAVA_CLIENT_ID=your_strava_client_id
   STRAVA_CLIENT_SECRET=your_strava_client_secret
   ```

4. **Launch the application**
   ```bash
   python app.py
   ```

5. **Access the interface**
   - Local: `http://localhost:7860`
   - Public link will be displayed in the console

## 🏗️ Architecture

### Project Structure
```
mount-rainer-rag/
├── app.py                     # Main application launcher
├── config.py                  # Configuration management
├── requirements.txt           # Python dependencies
├── templates/                 # Prompt templates
│   ├── system_prompt.txt     # Main system prompt
│   ├── trail_query_prompt.txt # Trail-specific responses
│   ├── weather_query_prompt.txt # Weather-specific responses
│   ├── safety_prompt.txt     # Safety-focused responses
│   └── gear_prompt.txt       # Gear recommendations
├── src/
│   ├── rag_system/           # Core RAG engine
│   │   ├── rag_engine.py     # Main RAG coordinator
│   │   └── prompt_manager.py # Template management
│   ├── data_sources/         # External data integrations
│   │   ├── alltrails_api.py  # AllTrails trail data and reviews
│   │   ├── nps_api.py        # National Park Service API
│   │   ├── weather_api.py    # Weather data integration
│   │   ├── strava_api.py     # Trail and activity data
│   │   ├── web_search_api.py # Real-time web search integration
│   │   └── visit_rainier_api.py # Tourism data integration
│   └── ui/
│       └── gradio_app.py     # Animated Gradio interface
├── data/                     # Data storage
└── static/                   # Static assets
```

### Core Components

#### 🎯 RAG Engine (`src/rag_system/rag_engine.py`)
- Coordinates all data sources and AI processing
- Manages vector storage with ChromaDB
- Handles query classification and response generation
- Integrates real-time data with static knowledge

#### 📊 Data Sources
- **AllTrails API Integration**: Comprehensive trail data with user reviews, ratings, and current conditions
- **NPS API Integration**: Official park information, alerts, and facilities
- **Weather API**: Real-time conditions and forecasts with elevation adjustments
- **Strava API**: Popular trail data and community insights
- **Web Search Integration**: Real-time information and source attribution
- **Static Knowledge**: Curated Mount Rainier facts and guidelines

#### 🎨 UI Components (`src/ui/gradio_app.py`)
- Animated mountain scene with dynamic elements
- Real-time scene updates every 3 seconds
- Responsive chat interface with context awareness
- Example questions for easy interaction

#### 📝 Prompt Management (`src/rag_system/prompt_manager.py`)
- Template-based prompt system for easy modifications
- Automatic query classification
- Context-aware prompt selection
- Extensible prompt categories

## 🎛️ Configuration

### Environment Variables
| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key for AI responses |
| `WEATHER_API_KEY` | No | OpenWeatherMap API key |
| `NPS_API_KEY` | No | National Park Service API key |
| `STRAVA_CLIENT_ID` | No | Strava application client ID |
| `STRAVA_CLIENT_SECRET` | No | Strava application client secret |

### System Configuration
The `config.py` file contains customizable settings:
- Database paths and connection strings
- RAG system parameters (chunk size, overlap, top-k results)
- Animation timing and visual settings
- Mount Rainier specific coordinates and elevation data

## 🔌 API Integrations

### Getting API Keys

#### OpenAI (Required)
1. Visit [OpenAI API](https://platform.openai.com/api-keys)
2. Create an account and generate an API key
3. Add to your `.env` file

#### Weather API (Recommended)
1. Sign up at [OpenWeatherMap](https://openweathermap.org/api)
2. Get a free API key
3. Add to your `.env` file for real-time weather data

#### National Park Service (Optional)
1. Apply at [NPS Developer](https://www.nps.gov/subjects/developer/index.htm)
2. Get an API key for official park data
3. Add to your `.env` file

#### Strava (Optional)
1. Create an application at [Strava Developers](https://developers.strava.com/)
2. Get client ID and secret
3. Add to your `.env` file for trail activity data

## 🚀 Deployment

### Gradio Deployment (Recommended)
The application is designed for easy deployment with Gradio's built-in sharing:

1. **Local Development**
   ```bash
   python app.py
   ```

2. **Gradio Cloud Deployment**
   - The app creates a shareable public link automatically
   - Perfect for quick demos and sharing

3. **Custom Deployment**
   - Modify `gradio_app.py` to set custom `server_name` and `server_port`
   - Deploy to any cloud platform supporting Python web applications

### Docker Deployment (Optional)
Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 7860
CMD ["python", "app.py"]
```

## 🎯 Usage Examples

### Trail Information
```
"What are the best trails for beginners?"
"How difficult is the Skyline Trail?"
"What's the elevation gain on Mount Fremont Lookout?"
```

### Weather Queries
```
"What's the weather like today?"
"Should I hike this weekend?"
"What are conditions like at higher elevations?"
```

### Safety and Gear
```
"What gear do I need for winter hiking?"
"Is it safe to hike alone?"
"What should I do in case of emergency?"
```

### Permits and Planning
```
"Do I need permits for day hiking?"
"How do I make campground reservations?"
"What are the entrance fees?"
```

## 🛠️ Customization

### Adding New Prompt Templates
1. Create a new template file in `/templates/`
2. Update `prompt_manager.py` to load the template
3. Add query classification logic for the new category

### Extending Data Sources
1. Create a new module in `/src/data_sources/`
2. Implement the data fetching and formatting methods
3. Integrate with the main RAG engine

### Modifying the UI
1. Update `gradio_app.py` for interface changes
2. Modify CSS in the `create_mountain_scene()` method
3. Adjust animation timing and visual elements

## 🐛 Troubleshooting

### Common Issues

**Dependencies not installing**
- Ensure Python 3.8+ is installed
- Try using `pip install --upgrade pip` first

**API key errors**
- Verify API keys are correctly set in `.env`
- Check that the `.env` file is in the root directory

**Animation not updating**
- Ensure JavaScript is enabled in your browser
- Check browser console for any errors

**Slow responses**
- Check your internet connection for API calls
- Consider using local models for faster responses

### Performance Optimization
- Adjust `CHUNK_SIZE` and `TOP_K_RESULTS` in config for faster responses
- Enable caching for frequently accessed data
- Use local embeddings models for offline operation

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request with a clear description

### Areas for Contribution
- Additional data source integrations
- Enhanced animation features
- Mobile-responsive UI improvements
- Performance optimizations
- Additional prompt templates

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Mount Rainier National Park** for the inspiration and beauty
- **National Park Service** for providing open data APIs
- **OpenAI** for the powerful language models
- **Gradio** for the amazing UI framework
- **The hiking community** for sharing trail knowledge and safety practices

## 📞 Support

For questions, issues, or suggestions:
- Open an issue on GitHub
- Check the troubleshooting section
- Review the configuration guide

---

**Happy hiking! Stay safe and enjoy exploring Mount Rainier! 🏔️** 