#!/usr/bin/env python3
"""
🏔️ Mount Rainier AI Guide - Interactive Hiking Experience with FATMAP-style interface
Beautiful HTML interface with animated hiker following the actual climbing route
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
                "session_id": session_id
            })
    
    def send_json_response(self, data):
        """Send JSON response"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def get_main_html(self):
        """Generate the main HTML page with FATMAP-style layout"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏔️ Mount Rainier AI Guide - FATMAP Style</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #1a1a1a;
            color: white;
            overflow: hidden;
            height: 100vh;
        }
        
        .header {
            position: absolute;
            top: 20px;
            left: 20px;
            z-index: 1000;
            background: rgba(0,0,0,0.8);
            backdrop-filter: blur(10px);
            border-radius: 10px;
            padding: 15px 20px;
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        .header h1 {
            font-size: 1.5em;
            margin-bottom: 5px;
            color: #4CAF50;
        }
        
        .header p {
            font-size: 0.9em;
            opacity: 0.8;
        }
        
        .mountain-map {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: url('https://images.unsplash.com/photo-1519904981063-b0cf448d479e?ixlib=rb-4.0.3&auto=format&fit=crop&w=2560&q=80') center center;
            background-size: cover;
        }
        
        .hiker {
            position: absolute;
            width: 16px;
            height: 16px;
            background: #ff4444;
            border: 3px solid white;
            border-radius: 50%;
            box-shadow: 0 0 10px rgba(255, 68, 68, 0.8);
            z-index: 500;
            transition: all 2s ease-in-out;
        }
        
        .hiker::before {
            content: '🥾';
            position: absolute;
            top: -20px;
            left: -10px;
            font-size: 16px;
        }
        
        .status-overlay {
            position: absolute;
            bottom: 20px;
            left: 20px;
            background: rgba(0,0,0,0.8);
            backdrop-filter: blur(10px);
            border-radius: 10px;
            padding: 15px;
            border: 1px solid rgba(255,255,255,0.2);
            min-width: 280px;
        }
        
        .status-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 0.9em;
        }
        
        .status-item:last-child {
            margin-bottom: 0;
        }
        
        .chat-panel {
            position: absolute;
            top: 20px;
            right: 20px;
            width: 380px;
            height: calc(100vh - 40px);
            background: rgba(0,0,0,0.9);
            backdrop-filter: blur(15px);
            border-radius: 15px;
            border: 1px solid rgba(255,255,255,0.2);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .chat-header {
            padding: 20px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            background: rgba(76, 175, 80, 0.2);
        }
        
        .chat-header h2 {
            color: #4CAF50;
            margin-bottom: 10px;
            font-size: 1.2em;
        }
        
        .hiker-message {
            background: rgba(76, 175, 80, 0.1);
            border-radius: 10px;
            padding: 12px;
            font-size: 0.9em;
            border-left: 3px solid #4CAF50;
        }
        
        .chat-history {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            max-height: 400px;
        }
        
        .message {
            margin-bottom: 15px;
            padding: 12px;
            border-radius: 10px;
            font-size: 0.9em;
            line-height: 1.4;
        }
        
        .user-message {
            background: rgba(33, 150, 243, 0.2);
            text-align: right;
            border-right: 3px solid #2196F3;
        }
        
        .ai-message {
            background: rgba(76, 175, 80, 0.2);
            border-left: 3px solid #4CAF50;
        }
        
        .input-section {
            padding: 20px;
            border-top: 1px solid rgba(255,255,255,0.1);
        }
        
        .question-input {
            width: 100%;
            padding: 12px;
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 8px;
            background: rgba(255,255,255,0.1);
            color: white;
            font-size: 0.9em;
            margin-bottom: 10px;
        }
        
        .question-input::placeholder {
            color: rgba(255,255,255,0.6);
        }
        
        .ask-button {
            width: 100%;
            padding: 12px;
            background: #4CAF50;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.9em;
            font-weight: bold;
            transition: background 0.3s;
        }
        
        .ask-button:hover {
            background: #45a049;
        }
        
        .ask-button:disabled {
            background: #666;
            cursor: not-allowed;
        }
        
        .suggestions {
            margin-top: 15px;
        }
        
        .suggestion-button {
            display: inline-block;
            margin: 4px;
            padding: 6px 12px;
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 15px;
            color: white;
            text-decoration: none;
            cursor: pointer;
            font-size: 0.8em;
            transition: all 0.3s;
        }
        
        .suggestion-button:hover {
            background: rgba(255,255,255,0.2);
            transform: translateY(-1px);
        }
        
        .loading {
            text-align: center;
            padding: 15px;
            color: #4CAF50;
            font-style: italic;
        }
        
        /* Route visualization (placeholder for blue line) */
        .route-line {
            position: absolute;
            pointer-events: none;
            z-index: 100;
        }
        
        @media (max-width: 768px) {
            .chat-panel {
                width: 100%;
                right: 0;
                top: 50%;
                height: 50%;
                border-radius: 15px 15px 0 0;
            }
            
            .header {
                font-size: 0.8em;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏔️ Mount Rainier AI Guide</h1>
        <p>Interactive FATMAP-style experience</p>
    </div>

    <div class="mountain-map">
        <div class="hiker" id="hiker"></div>
    </div>

    <div class="status-overlay">
        <div class="status-item">
            <span>📍 Zone:</span>
            <span id="current-zone">Loading...</span>
        </div>
        <div class="status-item">
            <span>⛰️ Elevation:</span>
            <span id="elevation">Loading...</span>
        </div>
        <div class="status-item">
            <span>🧭 Direction:</span>
            <span id="direction">Loading...</span>
        </div>
        <div class="status-item">
            <span>📈 Progress:</span>
            <span id="progress">Loading...</span>
        </div>
    </div>

    <div class="chat-panel">
        <div class="chat-header">
            <h2>💬 Your AI Guide</h2>
            <div class="hiker-message" id="hiker-message">
                🥾 Ready to explore Mount Rainier! What can I help you with?
            </div>
        </div>
        
        <div class="chat-history" id="chat-history">
            <div class="message ai-message">
                <strong>🏔️ Mount Rainier Guide:</strong> Welcome! I'm your AI hiking companion with access to comprehensive Mount Rainier knowledge. Ask me about trails, permits, weather, safety, gear, or anything else about this amazing mountain!
            </div>
        </div>
        
        <div class="input-section">
            <input type="text" class="question-input" id="question-input" 
                   placeholder="Ask about trails, permits, weather, safety..."
                   onkeypress="handleKeyPress(event)">
            <button class="ask-button" id="ask-button" onclick="askQuestion()">Ask Guide</button>
            
            <div class="suggestions">
                <span class="suggestion-button" onclick="setQuestion('What are the best beginner trails?')">Beginner trails?</span>
                <span class="suggestion-button" onclick="setQuestion('Do I need permits for climbing?')">Permits?</span>
                <span class="suggestion-button" onclick="setQuestion('What gear do I need for winter?')">Winter gear?</span>
                <span class="suggestion-button" onclick="setQuestion('Current weather conditions?')">Weather?</span>
                <span class="suggestion-button" onclick="setQuestion('Wildlife safety tips?')">Wildlife safety?</span>
            </div>
        </div>
    </div>

    <script>
        let sessionId = null;
        
        function updateHikerStatus() {
            fetch('/hiker-status')
                .then(response => response.json())
                .then(data => {
                    const hiker = document.getElementById('hiker');
                    const position = data.position;
                    
                    // FATMAP-style route following the blue line (Disappointment Cleaver)
                    let leftPos, topPos;
                    
                    if (position < 15) {
                        // Paradise to Panorama Point
                        leftPos = 40 + (position * 0.8);
                        topPos = 85 - (position * 1.2);
                    } else if (position < 35) {
                        // Panorama Point to Muir Snowfield
                        const localPos = position - 15;
                        leftPos = 52 + (localPos * 0.3);
                        topPos = 67 - (localPos * 1.0);
                    } else if (position < 55) {
                        // Muir Snowfield to Camp Muir
                        const localPos = position - 35;
                        leftPos = 58 + (localPos * 0.2);
                        topPos = 47 - (localPos * 0.8);
                    } else if (position < 75) {
                        // Camp Muir to Disappointment Cleaver
                        const localPos = position - 55;
                        leftPos = 62 + (localPos * 0.15);
                        topPos = 31 - (localPos * 0.6);
                    } else if (position < 95) {
                        // Disappointment Cleaver to Crater Rim
                        const localPos = position - 75;
                        leftPos = 65 + (localPos * 0.1);
                        topPos = 19 - (localPos * 0.4);
                    } else {
                        // Final push to Columbia Crest Summit
                        const localPos = position - 95;
                        leftPos = 67 + (localPos * 0.05);
                        topPos = 11 - (localPos * 0.2);
                    }
                    
                    hiker.style.left = leftPos + '%';
                    hiker.style.top = topPos + '%';
                    
                    // Update status display
                    document.getElementById('current-zone').textContent = data.zone;
                    document.getElementById('elevation').textContent = data.elevation.toLocaleString() + ' ft';
                    document.getElementById('direction').textContent = data.direction;
                    document.getElementById('progress').textContent = Math.round(position) + '%';
                    document.getElementById('hiker-message').innerHTML = '🥾 ' + data.message;
                })
                .catch(error => console.error('Error updating hiker status:', error));
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
            addMessage('ai', '<div class="loading" id="' + loadingId + '">🤔 Searching Mount Rainier knowledge base...</div>');
            
            fetch('/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: question, session_id: sessionId })
            })
            .then(response => response.json())
            .then(data => {
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
                        response += '<br><br><small><strong>✨ Enhanced:</strong> ' + data.enhanced_question + '</small>';
                    }
                    
                    addMessage('ai', response);
                }
                
                button.disabled = false;
                button.textContent = 'Ask Guide';
            })
            .catch(error => {
                console.error('Error:', error);
                const loadingElement = document.getElementById(loadingId);
                if (loadingElement) loadingElement.remove();
                addMessage('ai', '❌ Sorry, I encountered an error. Please try again.');
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
        
        function setQuestion(question) {
            document.getElementById('question-input').value = question;
        }
        
        function handleKeyPress(event) {
            if (event.key === 'Enter') askQuestion();
        }
        
        function initApp() {
            updateHikerStatus();
            setInterval(updateHikerStatus, 3000);
        }
        
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
    print("🏔️  MOUNT RAINIER AI GUIDE - FATMAP STYLE EXPERIENCE")
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