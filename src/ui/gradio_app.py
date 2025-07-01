import gradio as gr
import asyncio
import time
import logging
from typing import Dict, Any, Tuple
import json
from datetime import datetime

from config import Config
from src.rag_system.rag_engine import EnhancedRAGEngine

logger = logging.getLogger(__name__)

class MountRainierGradioApp:
    """Main Gradio application for Mount Rainier AI Guide with Enhanced RAG"""
    
    def __init__(self):
        self.config = Config()
        self.rag_engine = EnhancedRAGEngine()
        self.hiker_position = 0  # 0-100 representing position on mountain
        self.is_ascending = True
        self.day_time_cycle = 0  # 0-100 representing time of day
        self.is_thinking = False
        
    async def initialize(self):
        """Initialize the RAG system"""
        logger.info("Initializing Mount Rainier AI Guide with Enhanced RAG...")
        # Enhanced RAG engine is ready to use immediately
        logger.info("Mount Rainier AI Guide ready!")
    
    def create_mountain_scene(self) -> str:
        """Create the animated mountain scene with hiker"""
        # Calculate hiker position and time of day for animation
        current_time = time.time()
        
        # Continuous movement cycle (120 seconds full cycle)
        cycle_position = (current_time % 120) / 120
        
        # Hiker goes up and down
        if cycle_position < 0.5:
            # Ascending
            self.hiker_position = cycle_position * 2 * 100  # 0 to 100
            self.is_ascending = True
        else:
            # Descending
            self.hiker_position = (2 - cycle_position * 2) * 100  # 100 to 0
            self.is_ascending = False
        
        # Day/night cycle (240 seconds full cycle)
        day_cycle_position = (current_time % 240) / 240
        self.day_time_cycle = day_cycle_position * 100
        
        # Generate HTML for the mountain scene
        scene_html = f"""
        <div id="mountain-scene">
            <style>
                #mountain-scene {{
                    width: 100%;
                    height: 500px;
                    position: relative;
                    overflow: hidden;
                    border-radius: 15px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                    background: linear-gradient(to bottom, {self._get_sky_gradient()});
                    transition: all 2s ease-in-out;
                }}
                
                .mountain {{
                    position: absolute;
                    bottom: 0;
                    left: 50%;
                    transform: translateX(-50%);
                    width: 300px;
                    height: 400px;
                    background: linear-gradient(45deg, #2c3e50, #34495e);
                    clip-path: polygon(50% 0%, 0% 100%, 100% 100%);
                }}
                
                .hiker {{
                    position: absolute;
                    bottom: {20 + (self.hiker_position * 0.6)}%;
                    left: {45 + (self.hiker_position * 0.1)}%;
                    transform: translateX(-50%);
                    z-index: 10;
                    transition: all 2s ease-in-out;
                    font-size: 24px;
                }}
                
                .hiker-status {{
                    background: rgba(0,0,0,0.7);
                    color: white;
                    padding: 5px 10px;
                    border-radius: 15px;
                    font-size: 12px;
                    margin-top: 5px;
                    text-align: center;
                    white-space: nowrap;
                }}
                
                .info-panel {{
                    position: absolute;
                    top: 20px;
                    right: 20px;
                    background: rgba(255,255,255,0.9);
                    padding: 15px;
                    border-radius: 10px;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                }}
            </style>
            
            <div class="mountain"></div>
            <div class="hiker">
                🥾
                <div class="hiker-status">
                    {"🧗‍♂️ Ascending" if self.is_ascending else "🏃‍♂️ Descending"}
                    {" 🤔 Thinking..." if self.is_thinking else ""}
                </div>
            </div>
            <div class="info-panel">
                <div><strong>Elevation:</strong> {int(2000 + (self.hiker_position * 124.11))} ft</div>
                <div><strong>Time:</strong> {self._get_time_of_day_text()}</div>
            </div>
        </div>
        """
        
        return scene_html
    
    def _get_sky_gradient(self) -> str:
        """Get sky gradient based on time of day"""
        if self.day_time_cycle < 20:  # Night
            return "#0d1b2a, #1b263b"
        elif self.day_time_cycle < 30:  # Dawn
            return "#ff6b6b, #feca57"
        elif self.day_time_cycle < 70:  # Day
            return "#87ceeb, #add8e6"
        elif self.day_time_cycle < 80:  # Dusk
            return "#ff9500, #ff6348"
        else:  # Night
            return "#0d1b2a, #1b263b"
    
    def _get_time_of_day_text(self) -> str:
        """Get time of day text"""
        if self.day_time_cycle < 20:
            return "🌙 Night"
        elif self.day_time_cycle < 30:
            return "🌅 Dawn"
        elif self.day_time_cycle < 70:
            return "☀️ Day"
        elif self.day_time_cycle < 80:
            return "🌇 Dusk"
        else:
            return "🌙 Night"
    
    async def process_question(self, question: str, history: list) -> Tuple[str, list, str, str]:
        """Process user question using RAG and return response with sources"""
        if not question.strip():
            return "", history, self.create_mountain_scene(), ""
        
        # Set thinking state
        self.is_thinking = True
        
        try:
            # Initialize streaming response
            streaming_answer = ""
            streaming_sources = ""
            final_answer = ""
            final_sources = []
            
            # Create progress updates list to show user
            progress_updates = []
            
            # Get streaming response from Enhanced RAG engine
            async for update in self.rag_engine.get_answer_stream(question):
                step = update.get("step", "unknown")
                status = update.get("status", "unknown") 
                message = update.get("message", "")
                progress = update.get("progress", 0)
                
                # Add progress update
                progress_updates.append(f"[{progress:3d}%] {message}")
                
                # Show streaming progress in answer area
                streaming_answer = "🔄 **Processing Your Question**\n\n" + "\n".join(progress_updates[-5:])  # Show last 5 updates
                
                # Add progress bar
                progress_bar = "▓" * (progress // 5) + "░" * (20 - progress // 5)
                streaming_answer += f"\n\n`{progress_bar}` {progress}%"
                
                # Update history with streaming response
                if history and history[-1][0] == question:
                    history[-1] = [question, streaming_answer]
                else:
                    history.append([question, streaming_answer])
                
                # Show sources found during retrieval
                if step == "vector_retrieval" and status == "completed":
                    sources_found = update.get("sources_found", [])
                    if sources_found:
                        streaming_sources = self._format_streaming_sources(sources_found)
                
                # Handle final result
                if step == "final_result" and status == "completed":
                    final_answer = update.get("answer", "I couldn't process your question.")
                    final_sources = update.get("sources", [])
                    enhancement_used = update.get("enhancement_used", False)
                    
                    # Format the final answer
                    formatted_answer = final_answer
                    
                    # Add query enhancement info if used
                    if enhancement_used and update.get("enhanced_question") != question:
                        formatted_answer += f"\n\n🔍 *Query enhanced from: '{question}' → '{update.get('enhanced_question')}'*"
                    
                    # Add timestamp
                    timestamp = datetime.now().strftime("%I:%M %p")
                    formatted_answer += f"\n\n*Completed at: {timestamp}*"
                    
                    # Update final history
                    if history and history[-1][0] == question:
                        history[-1] = [question, formatted_answer]
                    else:
                        history.append([question, formatted_answer])
                    
                    # Format final sources
                    streaming_sources = self._format_sources_html(final_sources, [])
                    break
                
                # Handle errors
                if step == "error":
                    error_message = f"🏔️ I encountered a technical difficulty: {update.get('error', 'Unknown error')}"
                    if history and history[-1][0] == question:
                        history[-1] = [question, error_message]
                    else:
                        history.append([question, error_message])
                    streaming_sources = ""
                    break
            
        except Exception as e:
            logger.error(f"Error processing question: {e}")
            error_response = "🏔️ I'm experiencing some technical difficulties right now. Please try asking your question again!"
            history.append([question, error_response])
            streaming_sources = ""
        
        # Reset thinking state
        self.is_thinking = False
        
        return "", history, self.create_mountain_scene(), streaming_sources
    
    def _format_streaming_sources(self, sources: list) -> str:
        """Format sources found during streaming for display"""
        if not sources:
            return ""
        
        sources_html = """
        <div style="background: linear-gradient(135deg, #e3f2fd, #bbdefb); 
                    padding: 15px; border-radius: 10px; margin-top: 10px;">
            <h4 style="margin: 0 0 10px 0; color: #1565c0;">
                📚 Sources Found
            </h4>
        """
        
        for source in sources:
            source_name = source.replace('nps_', '').replace('_', ' ').title()
            sources_html += f"""
            <div style="background: rgba(255,255,255,0.7); padding: 8px; 
                       border-radius: 5px; margin: 5px 0;">
                <span style="font-weight: bold; color: #0d47a1;">📄 {source_name}</span>
            </div>
            """
        
        sources_html += "</div>"
        return sources_html
    
    def _classify_query(self, question: str) -> str:
        """Classify the query type based on keywords"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ["weather", "temperature", "rain", "snow", "forecast", "conditions"]):
            return "weather"
        elif any(word in question_lower for word in ["trail", "hike", "hiking", "route", "path"]):
            return "trail"
        elif any(word in question_lower for word in ["gear", "equipment", "pack", "bring", "clothing"]):
            return "gear"
        elif any(word in question_lower for word in ["permit", "reservation", "fee", "pass", "cost"]):
            return "permits"
        elif any(word in question_lower for word in ["safety", "dangerous", "risk", "emergency"]):
            return "safety"
        elif any(word in question_lower for word in ["flight", "airport", "bus", "train", "transportation", "driving"]):
            return "transportation"
        elif any(word in question_lower for word in ["summit", "climb", "climbing", "mountaineering"]):
            return "climbing"
        else:
            return "general"
    
    def _format_sources_html(self, sources: list, web_results: list) -> str:
        """Format sources into HTML for display"""
        if not sources and not web_results:
            return ""
        
        html = "<div style='background: #f8f9fa; padding: 15px; border-radius: 10px; margin-top: 15px;'>"
        html += "<h4 style='margin-top: 0; color: #2c5aa0;'>📚 Sources & References</h4>"
        
        # Add web search sources
        if web_results:
            html += "<div style='margin-bottom: 15px;'>"
            html += "<h5 style='color: #28a745; margin-bottom: 10px;'>🌐 Real-time Information:</h5>"
            for i, result in enumerate(web_results, 1):
                title = result.get("title", "Web Search Result")
                url = result.get("url", "")
                source = result.get("source", "Web Search")
                result_type = result.get("type", "general")
                
                # Create clickable link if URL is available
                if url:
                    html += f"<div style='margin-bottom: 8px;'>"
                    html += f"<strong>{i}.</strong> <a href='{url}' target='_blank' style='color: #007bff; text-decoration: none;'>{title}</a>"
                    html += f"<br><small style='color: #6c757d;'>Source: {source} • Type: {result_type.replace('_', ' ').title()}</small>"
                    html += "</div>"
                else:
                    html += f"<div style='margin-bottom: 8px;'>"
                    html += f"<strong>{i}.</strong> {title}"
                    html += f"<br><small style='color: #6c757d;'>Source: {source}</small>"
                    html += "</div>"
            html += "</div>"
        
        # Add static sources if any
        if sources:
            html += "<div style='margin-bottom: 10px;'>"
            html += "<h5 style='color: #17a2b8; margin-bottom: 10px;'>📖 Additional References:</h5>"
            for i, source in enumerate(sources, 1):
                title = source.get("title", "Reference")
                url = source.get("url", "")
                source_name = source.get("source", "Mount Rainier Database")
                
                if url:
                    html += f"<div style='margin-bottom: 5px;'>"
                    html += f"<strong>{i}.</strong> <a href='{url}' target='_blank' style='color: #007bff; text-decoration: none;'>{title}</a>"
                    html += f"<br><small style='color: #6c757d;'>Source: {source_name}</small>"
                    html += "</div>"
                else:
                    html += f"<div style='margin-bottom: 5px;'>"
                    html += f"<strong>{i}.</strong> {title} <small style='color: #6c757d;'>({source_name})</small>"
                    html += "</div>"
            html += "</div>"
        
        html += "<p style='margin-bottom: 0; font-size: 12px; color: #6c757d; font-style: italic;'>"
        html += "💡 Click links to visit official sources for the most up-to-date information"
        html += "</p>"
        html += "</div>"
        
        return html
    
    def create_interface(self):
        """Create the Gradio interface"""
        with gr.Blocks(
            theme=gr.themes.Soft(),
            css="""
            .main-container { max-width: 1200px; margin: 0 auto; }
            .mountain-scene { margin: 20px 0; }
            .chat-container { height: 400px; }
            .title { text-align: center; margin-bottom: 30px; }
            """,
            title=self.config.GRADIO_TITLE
        ) as app:
            
            gr.Markdown(
                """
                # 🏔️ Mount Rainier AI Guide
                ### Your intelligent companion for exploring Mount Rainier National Park
                
                Ask me anything about trails, weather, permits, gear, safety, or planning your adventure!
                Watch the animated hiker as they journey up and down the mountain through day and night cycles.
                """,
                elem_classes=["title"]
            )
            
            with gr.Row():
                with gr.Column(scale=2):
                    # Mountain scene
                    scene_display = gr.HTML(value=self.create_mountain_scene())
                
                with gr.Column(scale=3):
                    # Chat interface
                    chatbot = gr.Chatbot(
                        elem_classes=["chat-container"],
                        show_label=False,
                        avatar_images=["🧗‍♂️", "🏔️"]
                    )
                    
                    with gr.Row():
                        msg = gr.Textbox(
                            placeholder="Ask me about Mount Rainier trails, weather, permits, or anything else!",
                            show_label=False,
                            scale=4
                        )
                        submit_btn = gr.Button("Ask Guide", scale=1, variant="primary")
                    
                    # Sources display
                    sources_display = gr.HTML(
                        value="",
                        label="Sources & References",
                        visible=False
                    )
            
            # Example questions
            gr.Markdown("### 💡 Try asking:")
            with gr.Row():
                gr.Button("What's the weather like?", size="sm").click(
                    lambda: "What's the weather like on Mount Rainier today?",
                    outputs=msg
                )
                gr.Button("Best trails for beginners?", size="sm").click(
                    lambda: "What are the best trails for beginner hikers?",
                    outputs=msg
                )
                gr.Button("Gear recommendations?", size="sm").click(
                    lambda: "What gear do I need for hiking Mount Rainier?",
                    outputs=msg
                )
                gr.Button("Permit requirements?", size="sm").click(
                    lambda: "Do I need permits for hiking Mount Rainier?",
                    outputs=msg
                )
            
            # Set up chat functionality
            def handle_question(question, history):
                """Wrapper to handle async process_question"""
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(self.process_question(question, history))
                    # result is (msg, history, scene, sources)
                    msg_out, history_out, scene_out, sources_out = result
                    
                    # Show sources if available
                    sources_visible = bool(sources_out.strip())
                    
                    return msg_out, history_out, scene_out, sources_out, gr.update(visible=sources_visible)
                finally:
                    loop.close()
            
            submit_btn.click(
                fn=handle_question,
                inputs=[msg, chatbot],
                outputs=[msg, chatbot, scene_display, sources_display, sources_display]
            )
            
            msg.submit(
                fn=handle_question,
                inputs=[msg, chatbot], 
                outputs=[msg, chatbot, scene_display, sources_display, sources_display]
            )
            
            # Auto-refresh scene every 3 seconds
            app.load(
                fn=lambda: self.create_mountain_scene(),
                outputs=scene_display,
                every=3
            )
        
        return app

async def create_app():
    """Create and initialize the Gradio app"""
    app_instance = MountRainierGradioApp()
    await app_instance.initialize()
    return app_instance.create_interface()

def launch_app():
    """Launch the Gradio application"""
    import asyncio
    import os
    
    # Create event loop for async operations
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Create app
    app = loop.run_until_complete(create_app())
    
    # Get port from environment variable or use default
    port = int(os.environ.get("GRADIO_SERVER_PORT", 7860))
    
    # Launch with Gradio
    app.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=True,  # Creates public link for easy sharing
        show_error=True
    ) 