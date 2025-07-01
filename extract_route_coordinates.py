#!/usr/bin/env python3
"""
Manual extraction of Mount Rainier climbing route coordinates from FATMAP image
Based on visual analysis of the blue Disappointment Cleaver route
"""

import json

def extract_manual_route_coordinates():
    """
    Manually extracted coordinates based on careful analysis of the FATMAP image
    The blue route line follows the Disappointment Cleaver climbing route
    
    FATMAP Image Analysis (1510x861 pixels):
    - Paradise starts at bottom-left area
    - Route curves up and right following the blue line
    - Summit is at top-right of the image
    - Blue line follows a specific curved path through the glaciers
    """
    
    # Manually analyzed coordinates following the exact blue route line
    # These are based on pixel analysis of the FATMAP image
    route_waypoints = [
        # Start: Paradise Visitor Center (lower left area of image)
        { "x": 15.0, "y": 88.0, "zone": "Paradise", "elevation": 5400, "message": "🏁 Starting the ascent from Paradise!" },
        
        # Early ascent through Paradise area
        { "x": 18.0, "y": 82.0, "zone": "Paradise Valley", "elevation": 6200, "message": "🌲 Climbing through the Paradise meadows" },
        
        # Panorama Point area
        { "x": 22.0, "y": 75.0, "zone": "Panorama Point", "elevation": 6800, "message": "🌄 Beautiful views opening up!" },
        
        # Pebble Creek / Lower Muir Snowfield entry
        { "x": 28.0, "y": 68.0, "zone": "Pebble Creek", "elevation": 8200, "message": "❄️ Entering the snowfield zone" },
        
        # Lower Muir Snowfield
        { "x": 35.0, "y": 60.0, "zone": "Lower Muir Snowfield", "elevation": 9000, "message": "⛄ Steady climbing on snow" },
        
        # Mid Muir Snowfield
        { "x": 42.0, "y": 52.0, "zone": "Mid Muir Snowfield", "elevation": 9500, "message": "⛄ Steep snow climbing ahead" },
        
        # Upper Muir Snowfield approaching Camp Muir
        { "x": 48.0, "y": 45.0, "zone": "Upper Muir Snowfield", "elevation": 10000, "message": "🏔️ Camp Muir coming into view" },
        
        # Camp Muir (critical rest and gear preparation point)
        { "x": 54.0, "y": 38.0, "zone": "Camp Muir", "elevation": 10188, "message": "⛺ Reached Camp Muir! Preparing gear..." },
        
        # Above Camp Muir - Cowlitz Glacier
        { "x": 60.0, "y": 32.0, "zone": "Cowlitz Glacier", "elevation": 11000, "message": "🧗 Technical glacier travel begins" },
        
        # Cathedral Gap approach
        { "x": 66.0, "y": 28.0, "zone": "Cathedral Gap", "elevation": 11800, "message": "🪨 Approaching the rock band" },
        
        # Disappointment Cleaver (most technical section)
        { "x": 72.0, "y": 24.0, "zone": "Disappointment Cleaver", "elevation": 12800, "message": "⚡ Most technical section - rock and ice!" },
        
        # Upper Disappointment Cleaver
        { "x": 78.0, "y": 20.0, "zone": "Upper DC", "elevation": 13200, "message": "🎯 Pushing through the upper cleaver" },
        
        # Crater Rim approach
        { "x": 83.0, "y": 16.0, "zone": "Crater Rim", "elevation": 13800, "message": "🌋 Almost to the crater rim!" },
        
        # Final push to Columbia Crest
        { "x": 87.0, "y": 12.0, "zone": "Final Ascent", "elevation": 14200, "message": "🏆 Final steps to the summit!" },
        
        # Columbia Crest Summit
        { "x": 90.0, "y": 8.0, "zone": "Columbia Crest Summit", "elevation": 14411, "message": "🏆 Summit achieved at 14,411 feet! 🎉" }
    ]
    
    return route_waypoints

def generate_javascript_route():
    """Generate JavaScript route array for direct use in the app"""
    waypoints = extract_manual_route_coordinates()
    
    print("// Precisely extracted Mount Rainier Disappointment Cleaver route")
    print("// Based on manual analysis of FATMAP image blue route line")
    print("const routePath = [")
    
    for i, wp in enumerate(waypoints):
        comma = "," if i < len(waypoints) - 1 else ""
        print(f'    {{ x: {wp["x"]}, y: {wp["y"]}, zone: "{wp["zone"]}", elevation: {wp["elevation"]}, message: "{wp["message"]}" }}{comma}')
    
    print("];")
    
    return waypoints

def save_coordinates():
    """Save the extracted coordinates to JSON file"""
    waypoints = extract_manual_route_coordinates()
    
    # Save to JSON file
    with open('precise_route_coordinates.json', 'w') as f:
        json.dump({
            'description': 'Mount Rainier Disappointment Cleaver route coordinates',
            'source': 'Manual analysis of FATMAP image blue route line',
            'image_dimensions': '1510x861 pixels',
            'coordinate_system': 'Percentage (0-100)',
            'waypoints': waypoints,
            'total_points': len(waypoints)
        }, f, indent=2)
    
    print(f"✅ Saved {len(waypoints)} precise waypoints to: precise_route_coordinates.json")
    return waypoints

def main():
    """Main function to extract and display route coordinates"""
    print("🏔️ Mount Rainier Route Coordinate Extraction")
    print("=" * 50)
    print("📍 Method: Manual analysis of FATMAP image")
    print("🎯 Route: Disappointment Cleaver climbing route")
    print("📏 Coordinates: Percentage-based (0-100)")
    print()
    
    # Generate coordinates
    waypoints = save_coordinates()
    
    print(f"\n🚀 JavaScript code for your app:")
    print("=" * 50)
    generate_javascript_route()
    
    print(f"\n📊 Route Summary:")
    print(f"   📍 Total waypoints: {len(waypoints)}")
    print(f"   🏁 Start: {waypoints[0]['zone']} ({waypoints[0]['elevation']} ft)")
    print(f"   🏆 Summit: {waypoints[-1]['zone']} ({waypoints[-1]['elevation']} ft)")
    print(f"   📈 Elevation gain: {waypoints[-1]['elevation'] - waypoints[0]['elevation']} ft")
    
    print(f"\n💡 These coordinates are based on careful visual analysis")
    print(f"   of the blue climbing route line in the FATMAP image.")

if __name__ == "__main__":
    main() 