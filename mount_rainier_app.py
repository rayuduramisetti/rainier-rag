#!/usr/bin/env python3
"""
Mount Rainier AI Guide - FATMAP-Style Interactive Experience
A sophisticated RAG-powered hiking companion with real-time hiker simulation
"""

import os
import sys
import asyncio
import json
import uuid
import time
import webbrowser
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import mimetypes
from typing import Dict, Any

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from rag_system.rag_engine import EnhancedRAGEngine

class MountRainierApp:
    def __init__(self):
        self.rag_engine = None
        
    async def initialize_rag(self):
        """Initialize the Enhanced RAG System"""
        try:
            self.rag_engine = EnhancedRAGEngine()
            print("✅ Enhanced RAG System ready!")
        except Exception as e:
            print(f"❌ Error initializing RAG system: {e}")
            self.rag_engine = None



class MountRainierHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass
        
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/':
            self.serve_main_page()

        elif self.path.startswith('/static/'):
            self.serve_static_file()
        else:
            self.send_error(404)
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/ask':
            self.handle_question()
        else:
            self.send_error(404)

    def serve_static_file(self):
        """Serve static files (images, CSS, JS)"""
        try:
            # Remove '/static/' prefix and get file path
            file_path = self.path[8:]  # Remove '/static/'
            full_path = os.path.join('static', file_path)
            
            if os.path.exists(full_path) and os.path.isfile(full_path):
                # Get mime type
                mime_type, _ = mimetypes.guess_type(full_path)
                if mime_type is None:
                    mime_type = 'application/octet-stream'
                
                self.send_response(200)
                self.send_header('Content-type', mime_type)
                self.end_headers()
                
                with open(full_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404)
        except Exception as e:
            print(f"Error serving static file: {e}")
            self.send_error(500)
    
    def serve_main_page(self):
        """Serve the main HTML page"""
        html = self.get_main_html()
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    

    
    def handle_question(self):
        """Handle user questions via RAG system"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode())
        
        question = data.get('question', '').strip()
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        if not question:
            self.send_json_response({"error": "No question provided"})
            return
        
        if not app.rag_engine:
            self.send_json_response({"error": "RAG system not initialized"})
            return
        
        try:
            # Get answer using the RAG system (fix asyncio issue)
            import threading
            result = None
            error = None
            rag_engine = app.rag_engine  # Store reference to avoid None type issues
            
            def run_async_in_thread():
                nonlocal result, error
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(rag_engine.get_answer(question))
                    loop.close()
                except Exception as e:
                    error = e
            
            # Run in separate thread to avoid event loop conflicts
            thread = threading.Thread(target=run_async_in_thread)
            thread.start()
            thread.join(timeout=30)
            
            if error:
                raise error
            
            if result:
                response = {
                    "answer": result.get('answer', 'Sorry, I could not generate an answer.'),
                    "sources": result.get('sources', []),
                    "enhanced_question": result.get('enhanced_question', question),
                    "enhancement_used": result.get('enhancement_used', False),
                    "session_id": session_id
                }
            else:
                response = {
                    "answer": "Sorry, I encountered an error while processing your question.",
                    "sources": [],
                    "enhanced_question": question,
                    "enhancement_used": False,
                    "session_id": session_id
                }
            
            self.send_json_response(response)
            
        except Exception as e:
            print(f"Error processing question: {e}")
            self.send_json_response({
                "error": f"Error processing question: {str(e)}",
                "session_id": session_id
            })
    
    def send_json_response(self, data):
        """Send JSON response"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def get_main_html(self):
        """Generate the main HTML page with FATMAP-style interface"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏔️ Mount Rainier AI Guide - FATMAP Style</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            margin: 0;
            padding: 0;
            font-family: 'Arial', sans-serif;
            background: url('/static/images/mount_rainier.jpg') no-repeat center center fixed;
            background-size: cover;
            color: white;
            overflow: hidden;
        }
        
        /* Remove overlay - make background fully visible */
        body::before {
            content: '';
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: transparent; /* Completely transparent */
            z-index: 1;
        }
        
        /* Chat Interface - Modern Mountain Design */
        .chat-section {
            position: fixed;
            top: 20px; right: 20px;
            width: 420px; height: 680px;
            z-index: 1000;
            background: linear-gradient(145deg, rgba(15, 32, 56, 0.95), rgba(25, 42, 66, 0.90));
            backdrop-filter: blur(20px);
            border-radius: 20px;
            padding: 24px;
            border: 2px solid rgba(135, 206, 235, 0.3);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.6), 
                        0 0 30px rgba(135, 206, 235, 0.1);
            display: flex;
            flex-direction: column;
        }
        
        /* Status Panel - Mountain Theme - Professional */
        .status-panel {
            background: linear-gradient(135deg, rgba(70, 130, 180, 0.4), rgba(100, 149, 237, 0.3));
            border-radius: 20px;
            padding: 16px;
            margin-bottom: 18px;
            border: 2px solid rgba(135, 206, 235, 0.5);
            box-shadow: inset 0 3px 15px rgba(135, 206, 235, 0.15),
                        0 4px 16px rgba(0, 0, 0, 0.2);
            backdrop-filter: blur(15px);
        }
        
        .status-title {
            font-size: 1.2em;
            font-weight: 700;
            background: linear-gradient(45deg, #87CEEB, #E0F6FF, #B0E0E6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-align: center;
            margin: 0;
            text-shadow: 0 2px 15px rgba(135, 206, 235, 0.4);
            letter-spacing: 0.5px;
        }
        
        .chat-history {
            flex: 1;
            overflow-y: auto;
            background: rgba(5, 15, 25, 0.5);
            border-radius: 20px;
            padding: 20px;
            margin-bottom: 12px;
            border: 2px solid rgba(135, 206, 235, 0.3);
            min-height: 250px;
            backdrop-filter: blur(20px);
            box-shadow: inset 0 6px 24px rgba(0, 0, 0, 0.4),
                        0 6px 24px rgba(135, 206, 235, 0.15);
            /* Hide scrollbar */
            scrollbar-width: none; /* Firefox */
            -ms-overflow-style: none; /* IE and Edge */
        }
        
        .chat-history::-webkit-scrollbar {
            display: none; /* Chrome, Safari, Opera */
        }
        
        .message {
            margin-bottom: 16px;
            padding: 16px 20px;
            border-radius: 18px;
            max-width: 90%;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            animation: messageSlide 0.4s ease-out;
            line-height: 1.6;
            font-size: 14px;
            overflow: hidden;
            position: relative;
        }
        
        @keyframes messageSlide {
            from { opacity: 0; transform: translateY(15px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .user-message {
            background: linear-gradient(135deg, rgba(70, 130, 180, 0.8), rgba(100, 149, 237, 0.7));
            margin-left: auto;
            text-align: right;
            border: 2px solid rgba(135, 206, 235, 0.4);
            color: #E0F6FF;
            font-weight: 500;
            box-shadow: 0 4px 12px rgba(70, 130, 180, 0.4);
        }
        
        .ai-message {
            background: linear-gradient(135deg, rgba(25, 25, 40, 0.95), rgba(35, 35, 55, 0.9));
            border: 2px solid rgba(135, 206, 235, 0.4);
            border-left: 4px solid #87CEEB;
            border-radius: 18px;
            color: #F0F8FF;
            line-height: 1.6;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4),
                        inset 0 2px 8px rgba(135, 206, 235, 0.1);
            backdrop-filter: blur(12px);
            overflow: hidden;
        }
        
        /* Welcome message specific styling */
        .ai-message:first-child {
            background: linear-gradient(135deg, rgba(70, 130, 180, 0.3), rgba(100, 149, 237, 0.25));
            border: 2px solid rgba(135, 206, 235, 0.5);
            border-left: 4px solid #87CEEB;
            color: #E0F6FF;
            font-weight: 500;
            font-size: 14px;
            text-align: center;
            margin-bottom: 16px;
        }
        
        .enhanced-query-message {
            background: linear-gradient(135deg, rgba(135, 206, 235, 0.08), rgba(176, 224, 230, 0.06));
            border: 1px solid rgba(135, 206, 235, 0.25);
            border-left: 3px solid #87CEEB;
            border-radius: 12px;
            color: #E0F6FF;
            font-size: 13px;
            line-height: 1.5;
            padding: 12px 16px;
            margin-bottom: 12px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
            backdrop-filter: blur(8px);
        }
        
        .progress-message {
            background: linear-gradient(135deg, rgba(70, 130, 180, 0.2), rgba(100, 149, 237, 0.15));
            border: 2px solid rgba(135, 206, 235, 0.3);
            border-left: 4px solid #87CEEB;
            color: #E0F6FF;
            font-size: 14px;
            line-height: 1.6;
            padding: 16px;
            margin-bottom: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(12px);
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 0.8; }
            50% { opacity: 1; }
            100% { opacity: 0.8; }
        }
        
        .progress-content {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        /* Typography within messages */
        .message strong {
            color: #87CEEB;
            font-weight: 700;
            text-shadow: 0 1px 4px rgba(0, 0, 0, 0.4);
        }
        
        .message br {
            line-height: 2.2;
        }
        
        .message small {
            font-size: 11px;
            opacity: 0.8;
            display: block;
            margin-top: 16px;
            padding-top: 12px;
            border-top: 1px solid rgba(135, 206, 235, 0.25);
        }
        
        .hiker-message {
            background: linear-gradient(135deg, rgba(255, 140, 0, 0.3), rgba(255, 165, 0, 0.2));
            border-left: 4px solid #FFB347;
            font-style: italic;
            color: #FFF8DC;
            border: 1px solid rgba(255, 180, 71, 0.3);
        }
        
        /* Input Section */
        .input-section {
            display: flex;
            gap: 12px;
            margin-top: 0;
        }
        
        .question-input {
            flex: 1;
            padding: 14px;
            border: 2px solid rgba(135, 206, 235, 0.4);
            border-radius: 16px;
            background: rgba(255, 255, 255, 0.97);
            color: #1e293b;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.3s ease;
            box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.1),
                        0 2px 8px rgba(0, 0, 0, 0.1);
        }
        
        .question-input:focus {
            outline: none;
            border-color: #87CEEB;
            box-shadow: 0 0 15px rgba(135, 206, 235, 0.3),
                        inset 0 2px 8px rgba(0, 0, 0, 0.1);
            transform: translateY(-1px);
            background: rgba(255, 255, 255, 1);
        }
        
        .ask-button {
            padding: 14px 22px;
            background: linear-gradient(135deg, #4682B4, #87CEEB, #5A9BD4);
            color: white;
            border: none;
            border-radius: 16px;
            cursor: pointer;
            font-weight: 700;
            font-size: 14px;
            transition: all 0.3s ease;
            box-shadow: 0 3px 12px rgba(70, 130, 180, 0.4);
            text-transform: uppercase;
            letter-spacing: 0.6px;
        }
        
        .ask-button:hover:not(:disabled) {
            background: linear-gradient(135deg, #5A9BD4, #9FD3E8, #6BB6FF);
            transform: translateY(-3px);
            box-shadow: 0 10px 30px rgba(70, 130, 180, 0.7);
        }
        
        .ask-button:disabled {
            background: linear-gradient(135deg, #666, #888);
            cursor: not-allowed;
            transform: none;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
            opacity: 0.7;
        }
        
        /* Quick Questions Section - Fixed positioning and spacing */
        .quick-questions {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px 10px;
            margin-bottom: 18px;
            padding: 0;
        }
        
        .quick-btn {
            display: inline-block;
            padding: 10px 14px;
            background: linear-gradient(135deg, rgba(135, 206, 235, 0.25), rgba(176, 224, 230, 0.2));
            border: 2px solid rgba(135, 206, 235, 0.5);
            border-radius: 16px;
            color: #E0F6FF;
            text-decoration: none;
            font-size: 11px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            backdrop-filter: blur(15px);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2),
                        inset 0 1px 4px rgba(135, 206, 235, 0.1);
            flex: 0 1 calc(50% - 4px);
            text-align: center;
            min-width: 110px;
            letter-spacing: 0.3px;
        }
        
        .quick-btn:hover {
            background: linear-gradient(135deg, rgba(135, 206, 235, 0.4), rgba(176, 224, 230, 0.35));
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(135, 206, 235, 0.3),
                        inset 0 2px 6px rgba(135, 206, 235, 0.15);
            border-color: #87CEEB;
            color: #F0F8FF;
        }
        
        /* Hiker Marker on Map */
        .hiker-marker {
            position: fixed;
            font-size: 24px;
            z-index: 900;
            transition: all 0.8s ease-in-out;
            filter: drop-shadow(2px 2px 4px rgba(0, 0, 0, 0.7));
        }
        
        /* Hiker Speech Bubble */
        .hiker-speech {
            position: fixed;
            background: rgba(255, 255, 255, 0.95);
            color: #333;
            padding: 8px 12px;
            border-radius: 15px;
            font-size: 12px;
            font-weight: 500;
            max-width: min(200px, 40vw);
            z-index: 901;
            transition: all 0.8s ease-in-out;
            border: 2px solid #4CAF50;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            opacity: 0;
            transform: scale(0.8);
            word-wrap: break-word;
        }
        
        .hiker-speech.show {
            opacity: 1;
            transform: scale(1);
        }
        
        .hiker-speech::before {
            content: '';
            position: absolute;
            bottom: -8px;
            left: 20px;
            width: 0;
            height: 0;
            border-left: 8px solid transparent;
            border-right: 8px solid transparent;
            border-top: 8px solid #4CAF50;
        }
        
        .hiker-speech::after {
            content: '';
            position: absolute;
            bottom: -6px;
            left: 22px;
            width: 0;
            height: 0;
            border-left: 6px solid transparent;
            border-right: 6px solid transparent;
            border-top: 6px solid rgba(255, 255, 255, 0.95);
        }
        
        /* Loading Animation */
        .loading {
            color: #4CAF50;
            font-style: italic;
        }
        
        /* Scrollbar Styling */
        .chat-history::-webkit-scrollbar {
            width: 6px;
        }
        
        .chat-history::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 3px;
        }
        
        .chat-history::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.3);
            border-radius: 3px;
        }
        
        /* Responsive Design */
        @media (max-width: 1200px) {
            .chat-section {
                width: 380px;
                height: 610px;
            }
        }
        
        @media (max-width: 768px) {
            .chat-section {
                width: 90%;
                right: 5%;
                top: 10px;
                height: 70vh;
            }
            
            .hiker-speech {
                font-size: 11px;
                padding: 6px 10px;
                max-width: min(180px, 50vw);
            }
            
            .hiker-marker {
                font-size: 20px;
            }
        }
        
        @media (max-width: 480px) {
            .chat-section {
                width: 95%;
                right: 2.5%;
                top: 5px;
                height: 65vh;
            }
            
            .hiker-speech {
                font-size: 9px;
                padding: 4px 6px;
                max-width: min(150px, 60vw);
            }
            
            .hiker-marker {
                font-size: 18px;
            }
        }
    </style>
</head>
<body>
    <!-- Chat Interface -->
    <div class="chat-section">
        <!-- Simplified Status Panel -->
        <div class="status-panel">
            <div class="status-title">Mount Rainier Guide</div>
        </div>
        
        <div class="chat-history" id="chatHistory">
            <div class="ai-message">
                Welcome! I can help you with trails, permits, weather, safety, and gear for Mount Rainier.<br/><br/>
                What would you like to know?
            </div>
        </div>
        
        <!-- Quick Questions - Outside chat history to prevent spacing issues -->
        <div class="quick-questions">
            <div class="quick-btn" onclick="askQuestion('What gear do I need for winter climbing?')">Winter gear? ❄️</div>
            <div class="quick-btn" onclick="askQuestion('Do I need permits for climbing?')">Permits? 📋</div>
            <div class="quick-btn" onclick="askQuestion('What are the weather conditions?')">Weather? 🌤️</div>
            <div class="quick-btn" onclick="askQuestion('Tell me about wildlife safety')">Wildlife? 🐻</div>
        </div>
        
        <div class="input-section">
            <input type="text" id="questionInput" class="question-input" 
                   placeholder="Ask about trails, permits, weather, safety..." 
                   onkeypress="handleKeyPress(event)">
            <button onclick="askQuestion()" class="ask-button" id="askButton">Ask Guide</button>
        </div>
    </div>
    
    <!-- Hiker Marker -->
    <div class="hiker-marker" id="hikerMarker">🚶‍♂️</div>
    
    <!-- Hiker Speech Bubble -->
    <div class="hiker-speech" id="hikerSpeech"></div>
    
    <script>
        let sessionId = null;
        let hikerMovementInterval;
        let startTime = Date.now();
        let currentPathIndex = 0;

        
        // Define the Mount Rainier Disappointment Cleaver route path
        // Coordinates extracted by tracing actual route line colors in the FATMAP image
        // Found 590 route pixels and extracted these precise waypoints
        const routePath = [
            // Paradise Visitor Center (Start) - traced from actual route pixels
            { x: 19.5, y: 92.7, zone: "Paradise", elevation: 5400, message: "🏁 Starting the ascent from Paradise!" },
            
            // Paradise Valley - following traced route
            { x: 21.2, y: 89.2, zone: "Paradise Valley", elevation: 6093, message: "🌲 Climbing through Paradise meadows" },
            
            // Panorama Point area
            { x: 24.9, y: 84.3, zone: "Panorama Point", elevation: 6786, message: "🌄 Beautiful views opening up!" },
            
            // Pebble Creek / Lower Muir Snowfield entry
            { x: 29.5, y: 79.9, zone: "Pebble Creek", elevation: 7479, message: "❄️ Entering the snowfield zone" },
            
            // Lower Muir Snowfield
            { x: 33.8, y: 73.9, zone: "Lower Muir Snowfield", elevation: 8172, message: "⛄ Steady climbing on snow" },
            
            // Mid Muir Snowfield
            { x: 39.2, y: 69.9, zone: "Mid Muir Snowfield", elevation: 8865, message: "⛄ Steep snow climbing ahead" },
            
            // Upper Muir Snowfield approaching Camp Muir
            { x: 41.5, y: 63.4, zone: "Upper Muir Snowfield", elevation: 9558, message: "🏔️ Camp Muir coming into view" },
            
            // Camp Muir (critical rest and gear preparation point)
            { x: 41.6, y: 61.3, zone: "Camp Muir", elevation: 10252, message: "⛺ Reached Camp Muir! Preparing gear..." },
            
            // Above Camp Muir - Cowlitz Glacier
            { x: 39.1, y: 55.5, zone: "Cowlitz Glacier", elevation: 10945, message: "🧗 Technical glacier travel begins" },
            
            // Cathedral Gap approach
            { x: 38.0, y: 48.8, zone: "Cathedral Gap", elevation: 11638, message: "🪨 Approaching the rock band" },
            
            // Disappointment Cleaver (most technical section)
            { x: 43.0, y: 45.8, zone: "Disappointment Cleaver", elevation: 12331, message: "⚡ Most technical section - rock and ice!" },
            
            // Upper Disappointment Cleaver
            { x: 43.2, y: 38.8, zone: "Upper DC", elevation: 13024, message: "🎯 Pushing through the upper cleaver" },
            
            // Crater Rim approach
            { x: 44.6, y: 33.4, zone: "Crater Rim", elevation: 13717, message: "🌋 Almost to the crater rim!" },
            
            // Approaching Columbia Crest
            { x: 45.6, y: 28.8, zone: "Upper Crater", elevation: 14000, message: "🎯 Final push to Columbia Crest!" },
            
            // Near the summit
            { x: 46.2, y: 15.0, zone: "Near Summit", elevation: 14300, message: "🏔️ Almost at the highest point!" },
            
            // Final approach to true summit
            { x: 46.8, y: 8.0, zone: "Summit Approach", elevation: 14400, message: "🚀 Steps away from the summit!" },
            
            // Final steps to summit
            { x: 48.0, y: 5.0, zone: "Final Summit Push", elevation: 14410, message: "🎯 Final steps to the very top!" },
            
            // Columbia Crest Summit - perfect summit position
            { x: 49.0, y: 4.0, zone: "Columbia Crest Summit", elevation: 14411, message: "🏆 Summit achieved at 14,411 feet! 🎉" }
        ];
        
        // Initialize the application
        function init() {
            startHikerMovement();
            
            // Add welcome message with delay
            setTimeout(() => {
                addHikerMessage("The trail conditions look good today. I'm making steady progress through the Paradise area!");
            }, 2000);
        }
        
        // Start the hiker movement animation
        function startHikerMovement() {
            hikerMovementInterval = setInterval(updateHikerPosition, 500); // Update every 500ms for smooth movement
        }
        
        // Update hiker position along the route path
        let isDescending = false;
        
        function updateHikerPosition() {
            const elapsedSeconds = (Date.now() - startTime) / 1000;
            
            // Complete ascent in 60 seconds, descent in 60 seconds (120 total)
            const ascentDuration = 60;
            const descentDuration = 60;
            const totalCycleDuration = ascentDuration + descentDuration;
            
            let progress, routeProgress, currentMessage;
            
            if (elapsedSeconds <= ascentDuration) {
                // Ascending phase
                isDescending = false;
                progress = Math.min(elapsedSeconds / ascentDuration, 1);
                routeProgress = Math.round(progress * 100);
                
                // Find current position on the path (ascending)
                const targetIndex = Math.floor(progress * (routePath.length - 1));
                const nextIndex = Math.min(targetIndex + 1, routePath.length - 1);
                
                // Interpolate between current and next waypoint
                const segmentProgress = (progress * (routePath.length - 1)) - targetIndex;
                const current = routePath[targetIndex];
                const next = routePath[nextIndex];
                
                // No pauses - continuous movement
                
                // Convert percentage coordinates to decimal for positioning
                const currentX = (current.x + (next.x - current.x) * segmentProgress) / 100;
                const currentY = (current.y + (next.y - current.y) * segmentProgress) / 100;
                const currentElevation = Math.round(current.elevation + (next.elevation - current.elevation) * segmentProgress);
                const currentZone = segmentProgress > 0.5 ? next.zone : current.zone;
                currentMessage = segmentProgress > 0.5 ? next.message : current.message;
                
                // Update hiker marker position and speech bubble
                updateHikerMarkerPosition(currentX, currentY);
                updateHikerSpeech(currentX, currentY, currentMessage, routeProgress);
                
                // Update status panel
                updateStatusPanel(currentZone, currentElevation, routeProgress);
                
            } else if (elapsedSeconds <= totalCycleDuration) {
                // Descending phase
                isDescending = true;
                const descentElapsed = elapsedSeconds - ascentDuration;
                progress = Math.min(descentElapsed / descentDuration, 1);
                routeProgress = Math.round(100 - (progress * 100)); // Reverse progress for descent
                
                // Find current position on the path (descending - reverse order)
                const reverseProgress = 1 - progress;
                const targetIndex = Math.floor(reverseProgress * (routePath.length - 1));
                const nextIndex = Math.min(targetIndex + 1, routePath.length - 1);
                
                // Interpolate between current and next waypoint (descending)
                const segmentProgress = (reverseProgress * (routePath.length - 1)) - targetIndex;
                const current = routePath[targetIndex];
                const next = routePath[nextIndex];
                
                // Convert percentage coordinates to decimal for positioning
                const currentX = (current.x + (next.x - current.x) * segmentProgress) / 100;
                const currentY = (current.y + (next.y - current.y) * segmentProgress) / 100;
                const currentElevation = Math.round(current.elevation + (next.elevation - current.elevation) * segmentProgress);
                const currentZone = segmentProgress > 0.5 ? next.zone : current.zone;
                
                // Create descent messages
                const descentMessages = {
                    "Columbia Crest Summit": "🏁 Starting descent from summit!",
                    "Final Summit Push": "⬇️ Descending from the absolute top",
                    "Summit Approach": "⬇️ Descending from the highest point",
                    "Near Summit": "🏔️ Careful descent from near summit",
                    "Upper Crater": "⬇️ Descending through upper crater",
                    "Crater Rim": "⬇️ Descending from crater rim",
                    "Upper DC": "🧗 Carefully descending upper cleaver",
                    "Disappointment Cleaver": "⚡ Technical descent through cleaver",
                    "Cathedral Gap": "🪨 Descending the rock band",
                    "Cowlitz Glacier": "🧗 Glacier descent in progress",
                    "Camp Muir": "⛺ Back at Camp Muir - quick rest",
                    "Upper Muir Snowfield": "❄️ Descending Muir snowfield",
                    "Mid Muir Snowfield": "⛄ Steady descent on snow",
                    "Lower Muir Snowfield": "⛄ Lower snowfield descent",
                    "Pebble Creek": "🌊 Approaching Pebble Creek",
                    "Panorama Point": "🌄 Beautiful descent views",
                    "Paradise Valley": "🌲 Almost back to Paradise",
                    "Paradise": "🏆 Safe return to Paradise! 🎉"
                };
                
                currentMessage = descentMessages[currentZone] || `⬇️ Descending through ${currentZone}`;
                
                // Update hiker marker position and speech bubble
                updateHikerMarkerPosition(currentX, currentY);
                updateHikerSpeech(currentX, currentY, currentMessage, routeProgress);
                
                // Update status panel
                updateStatusPanel(currentZone, currentElevation, routeProgress);
                
            } else {
                // Reset after complete cycle (ascent + descent)
                setTimeout(() => {
                    startTime = Date.now();
                    isDescending = false;
                }, 3000); // Wait 3 seconds before restarting the cycle
            }
        }
        
        // Update hiker marker position on the screen
        function updateHikerMarkerPosition(xPercent, yPercent) {
            const marker = document.getElementById('hikerMarker');
            const windowWidth = window.innerWidth;
            const windowHeight = window.innerHeight;
            
            const currentX = windowWidth * xPercent;
            const currentY = windowHeight * yPercent;
            
            marker.style.left = currentX + 'px';
            marker.style.top = currentY + 'px';
        }
        
        // Status panel is now simplified - no updates needed
        function updateStatusPanel(zone, elevation, progress) {
            // Status panel now shows static "Mount Rainier Guide" text
            // No dynamic updates needed
        }
        
        // Update hiker speech bubble
        let currentSpeechMessage = '';
        function updateHikerSpeech(xPercent, yPercent, message, progress) {
            const speechBubble = document.getElementById('hikerSpeech');
            const windowWidth = window.innerWidth;
            const windowHeight = window.innerHeight;
            
            // Calculate speech bubble position
            let speechX = windowWidth * xPercent + 30;
            let speechY = windowHeight * yPercent - 50;
            
            // Keep speech bubble within screen bounds
            const bubbleRect = speechBubble.getBoundingClientRect();
            const bubbleWidth = bubbleRect.width || 200; // Fallback width
            
            // Adjust X position if too close to right edge
            if (speechX + bubbleWidth > windowWidth - 10) {
                speechX = windowWidth * xPercent - bubbleWidth - 10;
            }
            
            // Adjust Y position if too close to top edge
            if (speechY < 10) {
                speechY = windowHeight * yPercent + 40;
            }
            
            speechBubble.style.left = Math.max(10, speechX) + 'px';
            speechBubble.style.top = Math.max(10, speechY) + 'px';
            
            // Update message if it changed
            if (message !== currentSpeechMessage) {
                currentSpeechMessage = message;
                speechBubble.textContent = message;
                
                // Show bubble with animation
                speechBubble.classList.remove('show');
                setTimeout(() => {
                    speechBubble.classList.add('show');
                }, 100);
                
                // Auto-hide after some time (except at major milestones)
                if (progress % 20 !== 0) {
                    setTimeout(() => {
                        speechBubble.classList.remove('show');
                    }, 4000);
                }
            }
        }
        
        // Handle keyboard input
        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                askQuestion();
            }
        }
        
        // Ask a question to the AI guide
        async function askQuestion(predefinedQuestion = null) {
            const input = document.getElementById('questionInput');
            const button = document.getElementById('askButton');
            const question = predefinedQuestion || input.value.trim();
            
            if (!question) return;
            
            // Add user message to chat
            addMessage(question, 'user');
            
            // Clear input and disable button
            input.value = '';
            button.disabled = true;
            button.textContent = 'Asking...';
            
            // Create progress message container
            const progressContainer = document.createElement('div');
            progressContainer.className = 'message ai-message progress-message';
            progressContainer.innerHTML = '<div class="progress-content">🤔 Processing your question...</div>';
            document.getElementById('chatHistory').appendChild(progressContainer);
            document.getElementById('chatHistory').scrollTop = document.getElementById('chatHistory').scrollHeight;
            
            try {
                const response = await fetch('/ask', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        question: question,
                        session_id: sessionId
                    })
                });
                
                const data = await response.json();
                
                // Remove progress message
                progressContainer.remove();
                
                if (data.error) {
                    addMessage(`❌ ${data.error}`, 'ai');
                } else {
                    // Show enhanced query if it's different from the original
                    if (data.enhanced_question && 
                        data.enhancement_used && 
                        data.enhanced_question !== question &&
                        data.enhanced_question.toLowerCase() !== question.toLowerCase()) {
                        
                        const enhancedQueryContent = `
                            <strong style="color: #87CEEB;">🔍 Rephrased Query:</strong><br/>
                            <em>"${data.enhanced_question}"</em>
                        `;
                        addMessage(enhancedQueryContent, 'enhanced-query');
                    }
                    
                    // Add AI response - cleaner format
                    let response = data.answer;
                    
                    // Add weather data indicator if weather was used
                    if (data.weather_used) {
                        response = `<div style="margin-bottom: 8px; padding: 8px 12px; background: rgba(135, 206, 235, 0.1); border-left: 3px solid #87CEEB; border-radius: 6px; font-size: 12px; color: #E0F6FF;">
                            🌤️ <strong>Real-time weather data included</strong> - Current conditions from Mount Rainier
                        </div>` + response;
                    }
                    
                    // Add sources if available - more subtle
                    if (data.sources && data.sources.length > 0) {
                        const sourceLinks = data.sources.map(src => {
                            if (src.url) {
                                return `<a href="${src.url}" target="_blank" rel="noopener" style="color:#87CEEB;text-decoration:underline;">${src.name}</a>`;
                            } else {
                                return src.name;
                            }
                        });
                        response += `<br/><br/><small style="opacity: 0.7;">📚 ${sourceLinks.join(' • ')}</small>`;
                    }
                    
                    addMessage(response, 'ai');
                    sessionId = data.session_id;
                }
                
            } catch (error) {
                // Remove progress message
                progressContainer.remove();
                addMessage(`❌ Connection error. Please try again.`, 'ai');
            } finally {
                // Re-enable button
                button.disabled = false;
                button.textContent = 'Ask Guide';
                input.focus();
            }
        }
        
        // Add message to chat history
        function addMessage(content, type) {
            const chatHistory = document.getElementById('chatHistory');
            const messageDiv = document.createElement('div');
            
            if (type === 'enhanced-query') {
                messageDiv.className = 'message enhanced-query-message';
            } else {
                messageDiv.className = `message ${type}-message`;
            }
            
            messageDiv.innerHTML = content;
            
            chatHistory.appendChild(messageDiv);
            // Improved scroll: only scroll if needed, keep both previous and new message visible
            messageDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
        

        
        // Initialize when page loads
        window.addEventListener('load', init);
        
        // Handle window resize
        window.addEventListener('resize', () => {
            // Hiker position will automatically adjust on next update
        });
    </script>
</body>
</html>"""

def start_server():
    """Start the web server"""
    server_address = ('localhost', 8888)
    try:
        httpd = HTTPServer(server_address, MountRainierHandler)
        print(f"🌐 Mount Rainier AI Guide server running at http://localhost:8888")
        print("🏔️ Opening your browser...")
        
        # Open browser after a short delay
        def open_browser():
            time.sleep(1)
            webbrowser.open('http://localhost:8888')
        
        threading.Thread(target=open_browser, daemon=True).start()
        
        httpd.serve_forever()
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print("❌ Port 8888 is already in use. Please kill the existing process or use a different port.")
            print("💡 Try: lsof -ti:8888 | xargs kill -9")
        else:
            print(f"❌ Error starting server: {e}")

async def main():
    """Main application entry point"""
    print("🏔️" + "="*60)
    print("🏔️  MOUNT RAINIER AI GUIDE - FATMAP-STYLE EXPERIENCE")
    print("🏔️" + "="*60)
    
    print("🚀 Initializing Enhanced RAG System...")
    await app.initialize_rag()
    
    print("🌐 Starting web server...")
    
    # Start server in a separate thread to avoid blocking
    start_server()

# Global app instance
app = MountRainierApp()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Mount Rainier AI Guide...")
    except Exception as e:
        print(f"❌ Error: {e}") 