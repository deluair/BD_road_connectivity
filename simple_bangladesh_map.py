#!/usr/bin/env python3
"""
Simple Bangladesh Road Map Generator
A lightweight version that creates an interactive map quickly
"""

import folium
import osmnx as ox
import geopandas as gpd
from folium import plugins
import warnings
warnings.filterwarnings('ignore')

def create_simple_bangladesh_map():
    """
    Create a simple interactive map of Bangladesh with major roads and cities
    """
    print("Creating simple Bangladesh road map...")
    
    # Bangladesh coordinates
    bangladesh_center = [23.6850, 90.3563]  # Dhaka coordinates
    
    # Create base map
    m = folium.Map(
        location=bangladesh_center,
        zoom_start=7,
        tiles='OpenStreetMap'
    )
    
    # Add different tile layers
    folium.TileLayer(
        'Stamen Terrain', 
        attr='Map tiles by <a href="http://stamen.com">Stamen Design</a>, under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. Data by <a href="http://openstreetmap.org">OpenStreetMap</a>, under <a href="http://www.openstreetmap.org/copyright">ODbL</a>.'
    ).add_to(m)
    
    folium.TileLayer(
        'CartoDB positron', 
        attr='Map tiles by <a href="https://carto.com/attributions">CARTO</a>, under <a href="https://creativecommons.org/licenses/by/3.0/">CC BY 3.0</a>. Data by <a href="http://openstreetmap.org">OpenStreetMap</a>, under <a href="http://www.openstreetmap.org/copyright">ODbL</a>.'
    ).add_to(m)
    
    # Major cities in Bangladesh
    major_cities = {
        'Dhaka': [23.8103, 90.4125],
        'Chittagong': [22.3569, 91.7832],
        'Sylhet': [24.8949, 91.8687],
        'Rajshahi': [24.3636, 88.6241],
        'Khulna': [22.8456, 89.5403],
        'Barisal': [22.7010, 90.3535],
        'Rangpur': [25.7439, 89.2752],
        'Mymensingh': [24.7471, 90.4203],
        'Comilla': [23.4682, 91.1788],
        'Narayanganj': [23.6238, 90.4990]
    }
    
    # Add major cities
    print("Adding major cities...")
    cities_group = folium.FeatureGroup(name="Major Cities")
    
    for city, coords in major_cities.items():
        folium.Marker(
            location=coords,
            popup=f"<b>{city}</b><br>Major City",
            tooltip=city,
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(cities_group)
    
    cities_group.add_to(m)
    
    # Try to add some major highways (simplified approach)
    print("Adding major highways...")
    try:
        # Get major highways around Dhaka (smaller area for performance)
        dhaka_area = ox.graph_from_point(
            bangladesh_center, 
            dist=50000,  # 50km radius
            network_type='drive'
        )
        
        # Convert to GeoDataFrame
        _, edges_gdf = ox.graph_to_gdfs(dhaka_area)
        
        # Filter for major roads only
        major_roads = edges_gdf[
            edges_gdf['highway'].astype(str).str.contains(
                'motorway|trunk|primary', 
                case=False, 
                na=False
            )
        ]
        
        print(f"Adding {len(major_roads)} major road segments...")
        
        # Add roads to map
        roads_group = folium.FeatureGroup(name="Major Roads")
        
        for idx, road in major_roads.iterrows():
            highway_type = str(road.get('highway', 'road'))
            
            # Color coding for different road types
            if 'motorway' in highway_type.lower():
                color = '#FF0000'  # Red
                weight = 4
            elif 'trunk' in highway_type.lower():
                color = '#FF4500'  # Orange Red
                weight = 3
            elif 'primary' in highway_type.lower():
                color = '#FFA500'  # Orange
                weight = 2
            else:
                color = '#808080'  # Gray
                weight = 1
            
            folium.GeoJson(
                road.geometry,
                style_function=lambda x, color=color, weight=weight: {
                    'color': color,
                    'weight': weight,
                    'opacity': 0.7
                },
                popup=f"Road Type: {highway_type}",
                tooltip=f"{highway_type.title()} Road"
            ).add_to(roads_group)
        
        roads_group.add_to(m)
        
    except Exception as e:
        print(f"Could not load road network: {e}")
        print("Map will show cities only.")
    
    # Add Bangladesh boundary (simplified)
    print("Adding country boundary...")
    try:
        # Get Bangladesh boundary
        bangladesh = ox.geocode_to_gdf('Bangladesh')
        
        folium.GeoJson(
            bangladesh.geometry.iloc[0],
            style_function=lambda x: {
                'fillColor': 'transparent',
                'color': 'blue',
                'weight': 3,
                'opacity': 0.8
            },
            popup="Bangladesh",
            tooltip="Bangladesh Border"
        ).add_to(m)
        
    except Exception as e:
        print(f"Could not load country boundary: {e}")
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Add minimap
    minimap = plugins.MiniMap()
    m.add_child(minimap)
    
    # Add measurement tool
    plugins.MeasureControl().add_to(m)
    
    # Add fullscreen button
    plugins.Fullscreen().add_to(m)
    
    # Save map
    output_file = "simple_bangladesh_map.html"
    m.save(output_file)
    print(f"\nSimple interactive map saved to {output_file}")
    print("Open this file in your web browser to view the map.")
    
    return m

def main():
    """
    Main function to create the simple Bangladesh map
    """
    print("Simple Bangladesh Road Map Generator")
    print("====================================\n")
    
    try:
        map_obj = create_simple_bangladesh_map()
        print("\n✅ Map generation completed successfully!")
        print("\nFeatures included:")
        print("- Major cities with markers")
        print("- Major highways around Dhaka area")
        print("- Country boundary")
        print("- Multiple map layers")
        print("- Interactive tools (measurement, fullscreen)")
        print("- Mini-map for navigation")
        
    except Exception as e:
        print(f"\n❌ Error creating map: {e}")
        print("Please check your internet connection and try again.")

if __name__ == "__main__":
    main()