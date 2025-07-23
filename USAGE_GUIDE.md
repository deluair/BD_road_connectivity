# Bangladesh Road Connectivity Analysis - Usage Guide

## Quick Start

### First Run (Downloads and caches data)
```bash
python bangladesh_road_map.py
```

### Subsequent Runs (Uses cached data - much faster!)
```bash
python bangladesh_road_map.py
```

## Command Line Options

### Basic Usage
- `python bangladesh_road_map.py` - Run analysis using cached data when available
- `python bangladesh_road_map.py --cache-info` - Show information about cached data
- `python bangladesh_road_map.py --clear-cache` - Clear all cached data

### Force Refresh Options
- `python bangladesh_road_map.py --force-download` - Force download fresh data from OpenStreetMap
- `python bangladesh_road_map.py --force-analysis` - Force recalculation of connectivity statistics
- `python bangladesh_road_map.py --force-download --force-analysis` - Force refresh everything

### Network Type Options
- `python bangladesh_road_map.py --network-type drive` - Download driving network (default)
- `python bangladesh_road_map.py --network-type walk` - Download walking network
- `python bangladesh_road_map.py --network-type bike` - Download cycling network
- `python bangladesh_road_map.py --network-type all` - Download all network types

## Caching System

The script now uses an intelligent caching system that saves:

1. **Road Network Data** (`data_cache/bangladesh_road_graph.pkl`)
   - Complete road network from OpenStreetMap
   - Typically 50-200 MB
   - Saves 5-15 minutes on subsequent runs

2. **District Boundaries** (`data_cache/bangladesh_districts.pkl`)
   - Administrative boundary data
   - Small file (~1 MB)
   - Saves 30-60 seconds

3. **Connectivity Statistics** (`data_cache/connectivity_stats.pkl`)
   - Pre-calculated network analysis results
   - Small file (<1 MB)
   - Saves 2-5 minutes of computation

## Performance Comparison

| Run Type | Time | Description |
|----------|------|-------------|
| First Run | 10-20 minutes | Downloads data + analysis |
| Cached Run | 2-5 minutes | Uses cached data |
| Map Only | 1-2 minutes | Uses all cached data |

## Programmatic Usage

```python
from bangladesh_road_map import BangladeshRoadMap

# Create analyzer
analyzer = BangladeshRoadMap()

# Check cache status
analyzer.get_cache_info()

# Run with different options
analyzer.run_complete_analysis()  # Use cache when available
analyzer.run_complete_analysis(force_download=True)  # Force fresh download
analyzer.run_complete_analysis(force_analysis=True)  # Force fresh analysis

# Clear cache if needed
analyzer.clear_cache()

# Load specific components
analyzer.load_cached_graph()  # Load road network
analyzer.load_cached_districts()  # Load districts
stats = analyzer.load_cached_stats()  # Load statistics
```

## Troubleshooting

### Cache Issues
If you encounter errors related to cached data:
```bash
python bangladesh_road_map.py --clear-cache
python bangladesh_road_map.py --force-download --force-analysis
```

### Memory Issues
For large networks, the script automatically:
- Samples nodes for centrality calculations
- Uses efficient data structures
- Provides progress updates

### Network Issues
If download fails:
- Check internet connection
- Try again later (OpenStreetMap servers may be busy)
- Use `--force-download` to retry

## Cache Management

### View Cache Information
```bash
python bangladesh_road_map.py --cache-info
```

### Clear Specific Cache (Programmatic)
```python
import os
analyzer = BangladeshRoadMap()

# Remove specific cache files
if os.path.exists(analyzer.graph_cache_file):
    os.remove(analyzer.graph_cache_file)
```

### Cache Location
All cache files are stored in the `data_cache/` directory:
- `bangladesh_road_graph.pkl` - Road network
- `bangladesh_districts.pkl` - District boundaries  
- `connectivity_stats.pkl` - Analysis results

## Tips for Efficient Usage

1. **First time setup**: Run without any flags to download and cache everything
2. **Regular usage**: Just run `python bangladesh_road_map.py` - it's fast!
3. **Weekly refresh**: Use `--force-download` to get updated road data
4. **Development**: Use `--force-analysis` when testing analysis changes
5. **Clean slate**: Use `--clear-cache` when switching network types

## Output Files

- `bangladesh_road_map.html` - Interactive map (always generated)
- `data_cache/` - Cached data directory (auto-created)
- Console output - Analysis report and statistics