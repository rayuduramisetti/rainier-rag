#!/usr/bin/env python3
"""
🏔️ Mount Rainier AI Guide - Interactive Hiking Experience
Beautiful HTML interface with animated hiker and real mountain simulation
"""
import asyncio
import json
import sys
import threading
import time
from pathlib import Path
from typing import Dict, Any
import webbrowser

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from rag_system.rag_engine import EnhancedRAGEngine
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import uuid

class MountRainierApp:
    def __init__(self):
        self.rag_engine = None
        self.hiker_position = 0  # 0 = base, 100 = summit
        self.hiker_direction = 1  # 1 = ascending, -1 = descending
        self.sessions = {}  # Store chat sessions
        
    async def initialize_rag(self):
        """Initialize the RAG system"""
        try:
            self.rag_engine = EnhancedRAGEngine()
            print("✅ Enhanced RAG System ready!")
            return True
        except Exception as e:
            print(f"❌ Error initializing RAG: {e}")
            return False
    
    def get_hiker_status(self) -> Dict[str, Any]:
        """Get current hiker position and status"""
        # Calculate elevation based on position (Mount Rainier: 14,411 ft)
        base_elevation = 4000  # Starting elevation
        summit_elevation = 14411
        current_elevation = base_elevation + (self.hiker_position / 100) * (summit_elevation - base_elevation)
        
        # Determine hiker's message based on position and direction (real Mount Rainier experience)
        if self.hiker_position < 25:
            if self.hiker_direction == 1:
                message = "🥾 Starting from Paradise! The Skyline Trail ahead looks perfect. What can I help you plan for your adventure?"
            else:
                message = "🎉 Back at Paradise after an epic climb! That view of the Nisqually Glacier was incredible. Ready for your next question?"
        elif self.hiker_position < 50:
            if self.hiker_direction == 1:
                message = "🌲 Climbing toward Panorama Point! Can see the Muir Snowfield ahead. The views are opening up beautifully!"
            else:
                message = "🌲 Descending from Panorama Point. Perfect time to ask about gear or trail conditions!"
        elif self.hiker_position < 75:
            if self.hiker_direction == 1:
                message = "🏔️ Approaching Camp Muir! The glaciers and crevasses are stunning. This is serious mountaineering territory!"
            else:
                message = "🏔️ Descending from Camp Muir. The alpine glow on the surrounding peaks is magical. What would you like to know?"
        elif self.hiker_position < 90:
            if self.hiker_direction == 1:
                message = "⛰️ On the Disappointment Cleaver route! Almost at the summit crater. The exposure is incredible up here!"
            else:
                message = "⛰️ Carefully navigating down the Disappointment Cleaver. Technical terrain requires full attention!"
        else:
            if self.hiker_direction == 1:
                message = "🎯 SUMMIT! At Columbia Crest, 14,411 feet! The 360° views are absolutely life-changing!"
            else:
                message = "🏆 Starting the long descent from the summit. What an achievement! Ask me anything about this incredible mountain!"
        
        return {
            "position": self.hiker_position,
            "elevation": int(current_elevation),
            "direction": "ascending" if self.hiker_direction == 1 else "descending",
            "message": message,
            "zone": self.get_current_zone()
        }
    
    def get_current_zone(self) -> str:
        """Get the current hiking zone based on position (real Mount Rainier zones)"""
        if self.hiker_position < 25:
            return "Paradise (5,400 ft)"
        elif self.hiker_position < 50:
            return "Panorama Point"
        elif self.hiker_position < 75:
            return "Camp Muir (10,188 ft)"
        elif self.hiker_position < 90:
            return "Disappointment Cleaver"
        else:
            return "Columbia Crest Summit"
    
    def update_hiker_position(self):
        """Update hiker position for continuous animation"""
        while True:
            # Move hiker (slower, more realistic pace)
            self.hiker_position += self.hiker_direction * 0.5
            
            # Reverse direction at endpoints
            if self.hiker_position >= 100:
                self.hiker_position = 100
                self.hiker_direction = -1
            elif self.hiker_position <= 0:
                self.hiker_position = 0
                self.hiker_direction = 1
            
            time.sleep(2)  # Update every 2 seconds for smooth animation

app = MountRainierApp()

class MountRainierHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/':
            self.serve_main_page()
        elif self.path == '/hiker-status':
            self.serve_hiker_status()
        else:
            self.send_error(404)
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/ask':
            self.handle_question()
        else:
            self.send_error(404)
    
    def serve_main_page(self):
        """Serve the main HTML page"""
        html = self.get_main_html()
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def serve_hiker_status(self):
        """Serve current hiker status as JSON"""
        status = app.get_hiker_status()
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(status).encode())
    
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
                    "session_id": session_id,
                    "hiker_status": app.get_hiker_status()
                }
            else:
                response = {
                    "answer": "Sorry, I encountered an error while processing your question.",
                    "sources": [],
                    "enhanced_question": question,
                    "enhancement_used": False,
                    "session_id": session_id,
                    "hiker_status": app.get_hiker_status()
                }
            
            self.send_json_response(response)
            
        except Exception as e:
            print(f"Error processing question: {e}")
            self.send_json_response({
                "error": f"Error processing question: {str(e)}",
                "session_id": session_id,
                "hiker_status": app.get_hiker_status()
            })
    
    def send_json_response(self, data):
        """Send JSON response"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def get_main_html(self):
        """Generate the main HTML page"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏔️ Mount Rainier AI Guide - Interactive Hiking Experience</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: url('https://images.unsplash.com/photo-1506905925346-21bda4d32df4?ixlib=rb-4.0.3&auto=format&fit=crop&w=2340&q=80') center center fixed;
            background-size: cover;
            min-height: 100vh; 
            color: white;
            position: relative;
        }
        
        /* Dark overlay for better text readability */
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.4);
            z-index: -1;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { font-size: 3em; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); }
        .header p { font-size: 1.2em; opacity: 0.9; }
        .main-content { position: relative; height: 80vh; margin-bottom: 30px; }
        .mountain-section {
            position: absolute; top: 0; left: 0; right: 0; bottom: 0;
            background: none; border-radius: 15px; padding: 0;
        }
        .chat-section {
            position: absolute; top: 20px; right: 20px; width: 400px; height: calc(100% - 40px);
            background: rgba(0,0,0,0.8); border-radius: 15px; padding: 20px;
            backdrop-filter: blur(15px); border: 1px solid rgba(255,255,255,0.3);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        }
        .mountain-visualization {
            position: relative; height: 500px;
            background: url('https://images.unsplash.com/photo-1544550285-f813152fb2fd?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2340&q=80'AAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAH0AeADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD6/ooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAoooo') no-repeat center center;
            background-size: cover;
            border-radius: 10px; overflow: hidden; margin-bottom: 20px;
            border: 2px solid rgba(255,255,255,0.3);
        }
        .hiker {
            position: absolute; width: 30px; height: 30px; border-radius: 50%;
            background: radial-gradient(circle, #ff6b6b 30%, #ff4444 70%);
            border: 3px solid #ffffff; transition: all 2s ease-in-out; z-index: 10;
            box-shadow: 0 0 10px rgba(255, 107, 107, 0.6);
        }
        .hiker::before {
            content: '🥾'; position: absolute; top: -8px; left: -8px;
            font-size: 20px; z-index: 11;
        }
        .trail {
            position: absolute; bottom: 0; left: 0; right: 0; height: 5px;
            background: repeating-linear-gradient(90deg, #8B4513 0px, #8B4513 10px, #A0522D 10px, #A0522D 20px);
        }
        .status-panel { background: rgba(0,0,0,0.3); border-radius: 10px; padding: 20px; }
        .status-item {
            display: flex; justify-content: space-between; margin-bottom: 10px;
            padding: 8px; background: rgba(255,255,255,0.1); border-radius: 5px;
        }
        .hiker-message {
            background: rgba(76, 175, 80, 0.3); border-radius: 15px; padding: 15px;
            margin-bottom: 20px; border-left: 4px solid #4CAF50;
        }
        .chat-history {
            height: 300px; overflow-y: auto; background: rgba(0,0,0,0.2);
            border-radius: 10px; padding: 15px; margin-bottom: 20px;
        }
        .message { margin-bottom: 15px; padding: 10px; border-radius: 8px; }
        .user-message { background: rgba(33, 150, 243, 0.3); text-align: right; }
        .ai-message { background: rgba(76, 175, 80, 0.3); }
        .input-section { display: flex; gap: 10px; }
        .question-input {
            flex: 1; padding: 15px; border: none; border-radius: 10px;
            background: rgba(255,255,255,0.9); color: #333; font-size: 16px;
        }
        .ask-button {
            padding: 15px 25px; background: #4CAF50; color: white; border: none;
            border-radius: 10px; cursor: pointer; font-size: 16px; font-weight: bold;
            transition: background 0.3s;
        }
        .ask-button:hover { background: #45a049; }
        .ask-button:disabled { background: #666; cursor: not-allowed; }
        .suggestions { margin-top: 15px; }
        .suggestion-button {
            display: inline-block; margin: 5px; padding: 8px 15px;
            background: rgba(255,255,255,0.2); border: 1px solid rgba(255,255,255,0.3);
            border-radius: 20px; color: white; text-decoration: none; cursor: pointer;
            transition: all 0.3s;
        }
        .suggestion-button:hover { background: rgba(255,255,255,0.3); transform: translateY(-2px); }
        .loading { text-align: center; padding: 20px; color: #4CAF50; }
        @media (max-width: 768px) {
            .main-content { grid-template-columns: 1fr; }
            .header h1 { font-size: 2em; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏔️ Mount Rainier AI Guide</h1>
            <p>Your intelligent companion for exploring Mount Rainier National Park</p>
        </div>
        <div class="main-content">
            <div class="mountain-section">
                <h2>🥾 Live Hiking Experience</h2>
                <div class="mountain-visualization">
                    <div class="climbing-route"></div>
                    <div class="paradise-base" title="Paradise Base (5,400 ft)"></div>
                    <div class="camp-muir-real" title="Camp Muir (10,188 ft)"></div>
                    <div class="summit-real" title="Columbia Crest Summit (14,411 ft)"></div>
                    <div class="hiker" id="hiker"></div>
                </div>
                <div class="status-panel">
                    <div class="status-item"><span>📍 Current Zone:</span><span id="current-zone">Loading...</span></div>
                    <div class="status-item"><span>⛰️ Elevation:</span><span id="elevation">Loading...</span></div>
                    <div class="status-item"><span>🧭 Direction:</span><span id="direction">Loading...</span></div>
                    <div class="status-item"><span>📈 Progress:</span><span id="progress">Loading...</span></div>
                </div>
            </div>
            <div class="chat-section">
                <h2>💬 Chat with Your Guide</h2>
                <div class="hiker-message" id="hiker-message">
                    🥾 Starting my hike up Mount Rainier! The trail looks great today. What can I help you with?
                </div>
                <div class="chat-history" id="chat-history">
                    <div class="message ai-message">
                        <strong>🏔️ Mount Rainier Guide:</strong> Welcome! I'm your AI hiking companion. I can help you with trails, permits, weather, safety, gear recommendations, and anything else about Mount Rainier. Ask me anything!
                    </div>
                </div>
                <div class="input-section">
                    <input type="text" class="question-input" id="question-input" 
                           placeholder="Ask about trails, weather, permits, safety, or anything else..."
                           onkeypress="handleKeyPress(event)">
                    <button class="ask-button" id="ask-button" onclick="askQuestion()">Ask Guide</button>
                </div>
                <div class="suggestions">
                    <p><strong>💡 Try asking:</strong></p>
                    <span class="suggestion-button" onclick="setQuestion('What are the best beginner trails?')">Best beginner trails?</span>
                    <span class="suggestion-button" onclick="setQuestion('Do I need permits for climbing?')">Climbing permits?</span>
                    <span class="suggestion-button" onclick="setQuestion('What gear do I need for winter hiking?')">Winter gear?</span>
                    <span class="suggestion-button" onclick="setQuestion('What wildlife should I watch for?')">Wildlife safety?</span>
                    <span class="suggestion-button" onclick="setQuestion('Best time to visit for weather?')">Best weather times?</span>
                </div>
            </div>
        </div>
    </div>
    <script>
        let sessionId = null;
        function updateHikerStatus() {
            fetch('/hiker-status').then(response => response.json()).then(data => {
                const hiker = document.getElementById('hiker');
                const position = data.position;
                // REAL Mount Rainier Disappointment Cleaver Route (following FATMAP path)
                let leftPos, bottomPos;
                if (position < 20) {
                    // Paradise to Panorama Point (5,400 ft → 6,800 ft)
                    leftPos = 45 + (position * 0.3);
                    bottomPos = 50 + (position * 2.0);
                } else if (position < 40) {
                    // Muir Snowfield climb to Camp Muir (6,800 ft → 10,188 ft)
                    leftPos = 51 + ((position - 20) * 0.05);
                    bottomPos = 90 + ((position - 20) * 5.5);
                } else if (position < 70) {
                    // Camp Muir to Disappointment Cleaver (10,188 ft → 12,300 ft)
                    leftPos = 52 + ((position - 40) * 0.1);
                    bottomPos = 200 + ((position - 40) * 6.0);
                } else if (position < 90) {
                    // Disappointment Cleaver to Crater Rim (12,300 ft → 14,000 ft)
                    leftPos = 55 - ((position - 70) * 0.15);
                    bottomPos = 380 + ((position - 70) * 4.5);
                } else {
                    // Final summit push to Columbia Crest (14,000 ft → 14,411 ft)
                    leftPos = 52 - ((position - 90) * 0.2);
                    bottomPos = 470 + ((position - 90) * 0.5);
                }
                hiker.style.left = leftPos + '%';
                hiker.style.bottom = bottomPos + 'px';
                document.getElementById('current-zone').textContent = data.zone;
                document.getElementById('elevation').textContent = data.elevation.toLocaleString() + ' ft';
                document.getElementById('direction').textContent = data.direction;
                document.getElementById('progress').textContent = Math.round(position) + '%';
                document.getElementById('hiker-message').innerHTML = '🥾 ' + data.message;
            }).catch(error => console.error('Error updating hiker status:', error));
        }
        function askQuestion() {
            const input = document.getElementById('question-input');
            const question = input.value.trim();
            if (!question) return;
            const button = document.getElementById('ask-button');
            addMessage('user', question);
            input.value = '';
            button.disabled = true;
            button.textContent = 'Thinking...';
            const loadingId = 'loading-' + Date.now();
            addMessage('ai', '<div class="loading" id="' + loadingId + '">🤔 Analyzing your question and searching Mount Rainier knowledge base...</div>');
            fetch('/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: question, session_id: sessionId })
            }).then(response => response.json()).then(data => {
                const loadingElement = document.getElementById(loadingId);
                if (loadingElement) loadingElement.remove();
                if (data.error) {
                    addMessage('ai', '❌ Error: ' + data.error);
                } else {
                    sessionId = data.session_id;
                    let response = '<strong>🏔️ Mount Rainier Guide:</strong><br>' + data.answer;
                    if (data.sources && data.sources.length > 0) {
                        response += '<br><br><small><strong>📚 Sources:</strong> ' + data.sources.join(', ') + '</small>';
                    }
                    if (data.enhancement_used && data.enhanced_question !== question) {
                        response += '<br><br><small><strong>✨ Enhanced Question:</strong> ' + data.enhanced_question + '</small>';
                    }
                    addMessage('ai', response);
                }
                button.disabled = false;
                button.textContent = 'Ask Guide';
            }).catch(error => {
                console.error('Error:', error);
                const loadingElement = document.getElementById(loadingId);
                if (loadingElement) loadingElement.remove();
                addMessage('ai', '❌ Sorry, I encountered an error while processing your question. Please try again.');
                button.disabled = false;
                button.textContent = 'Ask Guide';
            });
        }
        function addMessage(type, content) {
            const chatHistory = document.getElementById('chat-history');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message ' + (type === 'user' ? 'user-message' : 'ai-message');
            if (type === 'user') {
                messageDiv.innerHTML = '<strong>🧗 You:</strong> ' + content;
            } else {
                messageDiv.innerHTML = content;
            }
            chatHistory.appendChild(messageDiv);
            chatHistory.scrollTop = chatHistory.scrollHeight;
        }
        function setQuestion(question) { document.getElementById('question-input').value = question; }
        function handleKeyPress(event) { if (event.key === 'Enter') askQuestion(); }
        function initApp() { updateHikerStatus(); setInterval(updateHikerStatus, 3000); }
        window.addEventListener('load', initApp);
    </script>
</body>
</html>"""

def start_server():
    """Start the HTTP server"""
    port = 8888  # Use different port to avoid conflicts
    server_address = ('', port)
    httpd = HTTPServer(server_address, MountRainierHandler)
    print(f"🌐 Mount Rainier AI Guide server running at http://localhost:{port}")
    print("🏔️ Opening your browser...")
    
    # Open browser after a short delay
    threading.Timer(2, lambda: webbrowser.open(f'http://localhost:{port}')).start()
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Shutting down server...")
        httpd.shutdown()

async def main():
    """Main application entry point"""
    print("🏔️" + "="*60)
    print("🏔️  MOUNT RAINIER AI GUIDE - INTERACTIVE HIKING EXPERIENCE")
    print("🏔️" + "="*60)
    print()
    
    # Initialize RAG system
    print("🚀 Initializing Enhanced RAG System...")
    success = await app.initialize_rag()
    
    if not success:
        print("❌ Failed to initialize RAG system. Exiting.")
        return
    
    # Start hiker animation in background
    print("🥾 Starting hiker animation...")
    hiker_thread = threading.Thread(target=app.update_hiker_position, daemon=True)
    hiker_thread.start()
    
    # Start web server
    print("🌐 Starting web server...")
    start_server()

if __name__ == "__main__":
    asyncio.run(main()) 