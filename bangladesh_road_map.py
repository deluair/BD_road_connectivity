#!/usr/bin/env python3
"""
Bangladesh Road Connectivity Map
A comprehensive geospatial visualization of Bangladesh's road network using OpenStreetMap data.

This script creates an interactive map showing:
- Major highways and roads
- District boundaries
- Road connectivity analysis
- Interactive features with popup information

Author: AI Assistant
Date: 2024
"""

import osmnx as ox
import folium
import geopandas as gpd
import pandas as pd
import networkx as nx
import numpy as np
from folium import plugins
import warnings
import pickle
import os
from datetime import datetime
warnings.filterwarnings('ignore')

# Configure OSMnx settings
ox.settings.use_cache = True
ox.settings.log_console = True

class BangladeshRoadMap:
    def __init__(self):
        self.country_name = "Bangladesh"
        self.road_graph = None
        self.districts_gdf = None
        self.major_cities = [
            "Dhaka", "Chittagong", "Sylhet", "Rajshahi", 
            "Khulna", "Barisal", "Rangpur", "Mymensingh"
        ]
        self.cache_dir = "data_cache"
        self.graph_cache_file = os.path.join(self.cache_dir, "bangladesh_road_graph.pkl")
        self.districts_cache_file = os.path.join(self.cache_dir, "bangladesh_districts.pkl")
        self.stats_cache_file = os.path.join(self.cache_dir, "connectivity_stats.pkl")
        
        # Create cache directory if it doesn't exist
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            print(f"Created cache directory: {self.cache_dir}")
        
    def load_cached_graph(self):
        """
        Load cached road network if available
        """
        if os.path.exists(self.graph_cache_file):
            try:
                print("Loading cached road network...")
                with open(self.graph_cache_file, 'rb') as f:
                    self.road_graph = pickle.load(f)
                print(f"Successfully loaded cached network with {len(self.road_graph.nodes)} nodes and {len(self.road_graph.edges)} edges")
                return True
            except Exception as e:
                print(f"Error loading cached graph: {e}")
                return False
        return False
    
    def save_graph_to_cache(self):
        """
        Save road network to cache
        """
        try:
            print("Saving road network to cache...")
            with open(self.graph_cache_file, 'wb') as f:
                pickle.dump(self.road_graph, f)
            print(f"Road network cached successfully at {self.graph_cache_file}")
        except Exception as e:
            print(f"Error saving graph to cache: {e}")
    
    def download_road_network(self, network_type='drive', force_download=False):
        """
        Download Bangladesh road network from OpenStreetMap
        
        Args:
            network_type (str): Type of network ('drive', 'walk', 'bike', 'all')
            force_download (bool): Force download even if cache exists
        """
        # Try to load from cache first
        if not force_download and self.load_cached_graph():
            return True
            
        print(f"Downloading {network_type} network for {self.country_name}...")
        print("This may take several minutes. Please be patient.")
        try:
            # Download the road network for Bangladesh
            self.road_graph = ox.graph_from_place(
                self.country_name, 
                network_type=network_type,
                simplify=True
            )
            print(f"Successfully downloaded road network with {len(self.road_graph.nodes)} nodes and {len(self.road_graph.edges)} edges")
            
            # Save to cache
            self.save_graph_to_cache()
            return True
        except Exception as e:
            print(f"Error downloading road network: {e}")
            return False
    
    def load_cached_districts(self):
        """
        Load cached district boundaries if available
        """
        if os.path.exists(self.districts_cache_file):
            try:
                print("Loading cached district boundaries...")
                with open(self.districts_cache_file, 'rb') as f:
                    self.districts_gdf = pickle.load(f)
                print("Successfully loaded cached district boundaries")
                return True
            except Exception as e:
                print(f"Error loading cached districts: {e}")
                return False
        return False
    
    def save_districts_to_cache(self):
        """
        Save district boundaries to cache
        """
        try:
            print("Saving district boundaries to cache...")
            with open(self.districts_cache_file, 'wb') as f:
                pickle.dump(self.districts_gdf, f)
            print(f"District boundaries cached successfully at {self.districts_cache_file}")
        except Exception as e:
            print(f"Error saving districts to cache: {e}")
    
    def download_districts(self, force_download=False):
        """
        Download Bangladesh district boundaries
        
        Args:
            force_download (bool): Force download even if cache exists
        """
        # Try to load from cache first
        if not force_download and self.load_cached_districts():
            return True
            
        print("Downloading district boundaries...")
        try:
            # Try to get administrative boundaries
            self.districts_gdf = ox.geocode_to_gdf(
                "Bangladesh", 
                which_result=None
            )
            print("Successfully downloaded district boundaries")
            
            # Save to cache
            self.save_districts_to_cache()
            return True
        except Exception as e:
            print(f"Error downloading districts: {e}")
            return False
    
    def load_cached_stats(self):
        """
        Load cached connectivity statistics if available
        """
        if os.path.exists(self.stats_cache_file):
            try:
                print("Loading cached connectivity statistics...")
                with open(self.stats_cache_file, 'rb') as f:
                    stats = pickle.load(f)
                print("Successfully loaded cached connectivity statistics")
                return stats
            except Exception as e:
                print(f"Error loading cached stats: {e}")
                return None
        return None
    
    def save_stats_to_cache(self, stats):
        """
        Save connectivity statistics to cache
        """
        try:
            print("Saving connectivity statistics to cache...")
            with open(self.stats_cache_file, 'wb') as f:
                pickle.dump(stats, f)
            print(f"Statistics cached successfully at {self.stats_cache_file}")
        except Exception as e:
            print(f"Error saving stats to cache: {e}")
    
    def analyze_connectivity(self, force_analysis=False):
        """
        Analyze road network connectivity metrics
        
        Args:
            force_analysis (bool): Force analysis even if cache exists
        """
        if self.road_graph is None:
            print("No road network available for analysis")
            return None
        
        # Try to load from cache first
        if not force_analysis:
            cached_stats = self.load_cached_stats()
            if cached_stats is not None:
                return cached_stats
            
        print("Analyzing road network connectivity...")
        print("This may take a few minutes for large networks...")
        
        # Basic network statistics
        stats = {
            'total_nodes': len(self.road_graph.nodes),
            'total_edges': len(self.road_graph.edges),
            'is_connected': nx.is_connected(self.road_graph.to_undirected()),
            'number_of_components': nx.number_connected_components(self.road_graph.to_undirected()),
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Calculate centrality measures for major nodes
        try:
            # Convert to undirected for centrality calculations
            G_undirected = self.road_graph.to_undirected()
            
            # Calculate degree centrality
            degree_centrality = nx.degree_centrality(G_undirected)
            
            # Calculate betweenness centrality (sample for large networks)
            if len(G_undirected.nodes) > 5000:
                sample_nodes = list(G_undirected.nodes)[:1000]
                betweenness_centrality = nx.betweenness_centrality(
                    G_undirected.subgraph(sample_nodes)
                )
            else:
                betweenness_centrality = nx.betweenness_centrality(G_undirected)
            
            stats['avg_degree_centrality'] = np.mean(list(degree_centrality.values()))
            stats['avg_betweenness_centrality'] = np.mean(list(betweenness_centrality.values()))
            
        except Exception as e:
            print(f"Error calculating centrality measures: {e}")
        
        # Save to cache
        self.save_stats_to_cache(stats)
        
        return stats
    
    def create_interactive_map(self, save_path="bangladesh_road_map.html"):
        """
        Create an interactive Folium map of Bangladesh roads
        
        Args:
            save_path (str): Path to save the HTML map
        """
        if self.road_graph is None:
            print("No road network available for mapping")
            return None
            
        print("Creating interactive map...")
        
        # Convert graph to GeoDataFrames
        nodes_gdf, edges_gdf = ox.graph_to_gdfs(self.road_graph)
        
        # Calculate map center
        center_lat = nodes_gdf.geometry.y.mean()
        center_lon = nodes_gdf.geometry.x.mean()
        
        # Create base map
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=7,
            tiles='OpenStreetMap'
        )
        
        # Add different tile layers
        folium.TileLayer('Stamen Terrain', attr='Map tiles by <a href="http://stamen.com">Stamen Design</a>, under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. Data by <a href="http://openstreetmap.org">OpenStreetMap</a>, under <a href="http://www.openstreetmap.org/copyright">ODbL</a>.').add_to(m)
        folium.TileLayer('CartoDB positron', attr='Map tiles by <a href="https://carto.com/attributions">CARTO</a>, under <a href="https://creativecommons.org/licenses/by/3.0/">CC BY 3.0</a>. Data by <a href="http://openstreetmap.org">OpenStreetMap</a>, under <a href="http://www.openstreetmap.org/copyright">ODbL</a>.').add_to(m)
        
        # Style roads by type
        def get_road_style(highway_type):
            styles = {
                'motorway': {'color': '#FF0000', 'weight': 4, 'opacity': 0.8},
                'trunk': {'color': '#FF4500', 'weight': 3, 'opacity': 0.8},
                'primary': {'color': '#FFA500', 'weight': 2.5, 'opacity': 0.7},
                'secondary': {'color': '#FFFF00', 'weight': 2, 'opacity': 0.6},
                'tertiary': {'color': '#90EE90', 'weight': 1.5, 'opacity': 0.5},
                'residential': {'color': '#87CEEB', 'weight': 1, 'opacity': 0.4},
                'default': {'color': '#808080', 'weight': 1, 'opacity': 0.3}
            }
            
            if isinstance(highway_type, list):
                highway_type = highway_type[0] if highway_type else 'default'
            
            return styles.get(highway_type, styles['default'])
        
        # Add roads to map
        print("Adding roads to map...")
        road_groups = {}
        
        for idx, row in edges_gdf.iterrows():
            highway_type = row.get('highway', 'default')
            if isinstance(highway_type, list):
                highway_type = highway_type[0] if highway_type else 'default'
            
            if highway_type not in road_groups:
                road_groups[highway_type] = folium.FeatureGroup(name=f"{highway_type.title()} Roads")
            
            style = get_road_style(highway_type)
            
            # Create popup with road information
            popup_text = f"""
            <b>Road Information</b><br>
            Type: {highway_type}<br>
            Length: {row.get('length', 'N/A'):.0f}m<br>
            Name: {row.get('name', 'Unnamed')}
            """
            
            folium.GeoJson(
                row.geometry,
                style_function=lambda x, style=style: style,
                popup=folium.Popup(popup_text, max_width=200),
                tooltip=f"{highway_type.title()} Road"
            ).add_to(road_groups[highway_type])
        
        # Add road groups to map
        for group in road_groups.values():
            group.add_to(m)
        
        # Add major cities
        print("Adding major cities...")
        cities_group = folium.FeatureGroup(name="Major Cities")
        
        for city in self.major_cities:
            try:
                city_location = ox.geocode(f"{city}, Bangladesh")
                folium.Marker(
                    location=[city_location[0], city_location[1]],
                    popup=f"<b>{city}</b><br>Major City",
                    tooltip=city,
                    icon=folium.Icon(color='red', icon='info-sign')
                ).add_to(cities_group)
            except Exception as e:
                print(f"Could not geocode {city}: {e}")
        
        cities_group.add_to(m)
        
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
        m.save(save_path)
        print(f"Interactive map saved to {save_path}")
        
        return m
    
    def generate_report(self, force_analysis=False):
        """
        Generate a connectivity analysis report
        
        Args:
            force_analysis (bool): Force analysis even if cache exists
        """
        stats = self.analyze_connectivity(force_analysis=force_analysis)
        if stats is None:
            return
            
        print("\n" + "="*50)
        print("BANGLADESH ROAD CONNECTIVITY REPORT")
        print("="*50)
        print(f"Total Road Nodes: {stats['total_nodes']:,}")
        print(f"Total Road Segments: {stats['total_edges']:,}")
        print(f"Network Connected: {'Yes' if stats['is_connected'] else 'No'}")
        print(f"Number of Components: {stats['number_of_components']}")
        
        if 'avg_degree_centrality' in stats:
            print(f"Average Degree Centrality: {stats['avg_degree_centrality']:.4f}")
        if 'avg_betweenness_centrality' in stats:
            print(f"Average Betweenness Centrality: {stats['avg_betweenness_centrality']:.4f}")
        
        if 'analysis_date' in stats:
            print(f"Analysis Date: {stats['analysis_date']}")
        
        print("="*50)
    
    def clear_cache(self):
        """
        Clear all cached data
        """
        cache_files = [self.graph_cache_file, self.districts_cache_file, self.stats_cache_file]
        for cache_file in cache_files:
            if os.path.exists(cache_file):
                try:
                    os.remove(cache_file)
                    print(f"Removed cache file: {cache_file}")
                except Exception as e:
                    print(f"Error removing cache file {cache_file}: {e}")
        print("Cache cleared successfully!")
    
    def get_cache_info(self):
        """
        Get information about cached data
        """
        print("\n=== CACHE INFORMATION ===")
        cache_files = {
            'Road Network': self.graph_cache_file,
            'District Boundaries': self.districts_cache_file,
            'Connectivity Stats': self.stats_cache_file
        }
        
        for name, file_path in cache_files.items():
            if os.path.exists(file_path):
                size_mb = os.path.getsize(file_path) / (1024 * 1024)
                mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                print(f"{name}: Cached ({size_mb:.1f} MB, {mod_time.strftime('%Y-%m-%d %H:%M:%S')})")
            else:
                print(f"{name}: Not cached")
        print("========================\n")
    
    def run_complete_analysis(self, force_download=False, force_analysis=False):
        """
        Run the complete road connectivity analysis
        
        Args:
            force_download (bool): Force download even if cache exists
            force_analysis (bool): Force analysis even if cache exists
        """
        print("Starting Bangladesh Road Connectivity Analysis...")
        
        # Show cache information
        self.get_cache_info()
        
        if not force_download:
            print("Using cached data when available. Use force_download=True to refresh data.\n")
        
        # Download road network
        if not self.download_road_network(force_download=force_download):
            print("Failed to download road network. Exiting.")
            return
        
        # Download districts (optional)
        self.download_districts(force_download=force_download)
        
        # Generate analysis report
        self.generate_report(force_analysis=force_analysis)
        
        # Create interactive map
        map_obj = self.create_interactive_map()
        
        print("\nAnalysis complete!")
        print("Check 'bangladesh_road_map.html' for the interactive map.")
        print("\nTo force refresh data next time, use:")
        print("analyzer.run_complete_analysis(force_download=True, force_analysis=True)")
        
        return map_obj

def main():
    """
    Main function to run the Bangladesh road connectivity analysis
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Bangladesh Road Connectivity Analysis')
    parser.add_argument('--force-download', action='store_true', 
                       help='Force download data even if cache exists')
    parser.add_argument('--force-analysis', action='store_true', 
                       help='Force analysis even if cache exists')
    parser.add_argument('--clear-cache', action='store_true', 
                       help='Clear all cached data and exit')
    parser.add_argument('--cache-info', action='store_true', 
                       help='Show cache information and exit')
    parser.add_argument('--network-type', default='drive', 
                       choices=['drive', 'walk', 'bike', 'all'],
                       help='Type of network to download (default: drive)')
    
    args = parser.parse_args()
    
    # Create analyzer instance
    analyzer = BangladeshRoadMap()
    
    # Handle special commands
    if args.clear_cache:
        analyzer.clear_cache()
        return
    
    if args.cache_info:
        analyzer.get_cache_info()
        return
    
    # Run complete analysis
    analyzer.run_complete_analysis(
        force_download=args.force_download,
        force_analysis=args.force_analysis
    )

if __name__ == "__main__":
    main()