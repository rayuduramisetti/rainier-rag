#!/usr/bin/env python3
"""
Trace specific route colors found in the FATMAP image to extract precise coordinates
"""

from PIL import Image
import json

def trace_route_colors():
    """Trace the specific bright cyan/blue colors to find the route line"""
    
    # Load the image
    img = Image.open('static/images/mount_rainier.jpg')
    width, height = img.size
    print(f"Tracing route in {width}x{height} image...")
    
    # Target colors found in the image analysis (likely route line colors)
    target_colors = [
        (72, 233, 241),   # bright cyan
        (82, 197, 215),   # bright blue  
        (63, 235, 249),   # bright cyan
        (42, 239, 248),   # bright cyan
        (66, 222, 245),   # bright blue
        (39, 178, 211),   # blue
        (82, 191, 222),   # light blue
    ]
    
    # Find all pixels that match these colors (with some tolerance)
    route_pixels = []
    
    print("Scanning entire image for route colors...")
    for y in range(0, height, 2):  # Check every 2nd pixel for speed
        for x in range(0, width, 2):
            r, g, b = img.getpixel((x, y))
            
            # Check if this pixel matches any target color (within tolerance)
            for target_r, target_g, target_b in target_colors:
                if (abs(r - target_r) <= 10 and 
                    abs(g - target_g) <= 10 and 
                    abs(b - target_b) <= 10):
                    
                    # Convert to percentage coordinates
                    x_percent = (x / width) * 100
                    y_percent = (y / height) * 100
                    route_pixels.append((x_percent, y_percent, x, y))
                    break
    
    print(f"Found {len(route_pixels)} route pixels")
    
    if route_pixels:
        # Sort by position to trace the route
        route_pixels.sort(key=lambda p: (p[1], p[0]))  # Sort by Y first, then X
        
        print("\nFirst 20 route pixels found:")
        for i, (x_pct, y_pct, x_px, y_px) in enumerate(route_pixels[:20]):
            print(f"  {i+1}: ({x_pct:.1f}%, {y_pct:.1f}%) - pixel ({x_px}, {y_px})")
        
        print(f"\nLast 20 route pixels found:")
        for i, (x_pct, y_pct, x_px, y_px) in enumerate(route_pixels[-20:], len(route_pixels)-19):
            print(f"  {i}: ({x_pct:.1f}%, {y_pct:.1f}%) - pixel ({x_px}, {y_px})")
    
    return route_pixels

def extract_key_waypoints(route_pixels):
    """Extract key waypoints from the route pixels"""
    
    if not route_pixels:
        print("No route pixels found!")
        return []
    
    # Group pixels by approximate Y position to find key waypoints
    y_groups = {}
    for x_pct, y_pct, x_px, y_px in route_pixels:
        y_key = round(y_pct / 5) * 5  # Group by 5% Y intervals
        if y_key not in y_groups:
            y_groups[y_key] = []
        y_groups[y_key].append((x_pct, y_pct, x_px, y_px))
    
    # Extract representative points from each Y group
    waypoints = []
    for y_key in sorted(y_groups.keys(), reverse=True):  # Start from bottom (high Y)
        group = y_groups[y_key]
        # Take the median X position for this Y level
        group.sort(key=lambda p: p[0])
        median_idx = len(group) // 2
        x_pct, y_pct, x_px, y_px = group[median_idx]
        
        waypoints.append({
            "x": round(x_pct, 1),
            "y": round(y_pct, 1),
            "pixel_x": x_px,
            "pixel_y": y_px
        })
    
    return waypoints

def create_climbing_route(waypoints):
    """Convert waypoints to climbing route with zones and elevations"""
    
    if len(waypoints) < 5:
        print("Not enough waypoints found for a complete route")
        return []
    
    # Mount Rainier zone progression
    zones = [
        "Paradise", "Paradise Valley", "Panorama Point", "Pebble Creek",
        "Lower Muir Snowfield", "Mid Muir Snowfield", "Upper Muir Snowfield", 
        "Camp Muir", "Cowlitz Glacier", "Cathedral Gap", "Disappointment Cleaver",
        "Upper DC", "Crater Rim", "Columbia Crest Summit"
    ]
    
    # Elevation progression
    base_elevation = 5400
    summit_elevation = 14411
    
    climbing_route = []
    num_waypoints = min(len(waypoints), len(zones))
    
    for i in range(num_waypoints):
        wp = waypoints[i]
        
        # Calculate elevation based on position
        progress = i / (num_waypoints - 1) if num_waypoints > 1 else 0
        elevation = int(base_elevation + (summit_elevation - base_elevation) * progress)
        
        zone = zones[i] if i < len(zones) else f"Zone {i+1}"
        
        # Generate message
        messages = {
            "Paradise": "🏁 Starting the ascent from Paradise!",
            "Paradise Valley": "🌲 Climbing through Paradise meadows",
            "Panorama Point": "🌄 Beautiful views opening up!",
            "Pebble Creek": "❄️ Entering the snowfield zone",
            "Lower Muir Snowfield": "⛄ Steady climbing on snow",
            "Mid Muir Snowfield": "⛄ Steep snow climbing ahead",
            "Upper Muir Snowfield": "🏔️ Camp Muir coming into view",
            "Camp Muir": "⛺ Reached Camp Muir! Preparing gear...",
            "Cowlitz Glacier": "🧗 Technical glacier travel begins",
            "Cathedral Gap": "🪨 Approaching the rock band",
            "Disappointment Cleaver": "⚡ Most technical section - rock and ice!",
            "Upper DC": "🎯 Pushing through the upper cleaver",
            "Crater Rim": "🌋 Almost to the crater rim!",
            "Columbia Crest Summit": "🏆 Summit achieved at 14,411 feet! 🎉"
        }
        
        message = messages.get(zone, f"Climbing through {zone}")
        
        climbing_route.append({
            "x": wp["x"],
            "y": wp["y"],
            "zone": zone,
            "elevation": elevation,
            "message": message
        })
    
    return climbing_route

def main():
    """Main function to trace the route and create coordinates"""
    
    print("🏔️ TRACING FATMAP ROUTE COLORS")
    print("="*50)
    
    # Trace the route colors
    route_pixels = trace_route_colors()
    
    if not route_pixels:
        print("❌ No route colors found! The route line might use different colors.")
        return
    
    # Extract waypoints
    waypoints = extract_key_waypoints(route_pixels)
    print(f"\n📍 Extracted {len(waypoints)} waypoints from route pixels")
    
    # Create climbing route
    climbing_route = create_climbing_route(waypoints)
    
    # Save results
    with open('traced_route_coordinates.json', 'w') as f:
        json.dump({
            'method': 'Color tracing of FATMAP route line',
            'total_pixels_found': len(route_pixels),
            'waypoints_extracted': len(waypoints),
            'climbing_route': climbing_route
        }, f, indent=2)
    
    print(f"✅ Generated climbing route with {len(climbing_route)} waypoints")
    print("📁 Saved to: traced_route_coordinates.json")
    
    # Generate JavaScript
    if climbing_route:
        print(f"\n🚀 JavaScript route based on traced colors:")
        print("="*50)
        print("const routePath = [")
        for i, wp in enumerate(climbing_route):
            comma = "," if i < len(climbing_route) - 1 else ""
            print(f'    {{ x: {wp["x"]}, y: {wp["y"]}, zone: "{wp["zone"]}", elevation: {wp["elevation"]}, message: "{wp["message"]}" }}{comma}')
        print("];")
    else:
        print("❌ Could not generate climbing route")

if __name__ == "__main__":
    main() 