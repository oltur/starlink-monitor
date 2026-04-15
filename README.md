# Starlink Metrics Dashboard

A real-time web dashboard for monitoring Starlink performance metrics including download/upload speeds, latency, and connection quality.

## Features

- **Real-time graphs** with 8 different metrics:
  - Download speed (Mbps)
  - Upload speed (Mbps)
  - Latency (ms)
  - Packet loss / ping drop rate (%)
  - Obstruction percentage over time
  - GPS satellite count
  - Dish azimuth (pointing direction)
  - Dish elevation angle
- **Live statistics dashboard** with current values
- **Time range controls** - filter data by:
  - All data (up to 500 data points)
  - Last 5 minutes
  - Last 15 minutes
  - Last 30 minutes
  - Last 1 hour
- **Speedtest mode** - test maximum bandwidth capacity:
  - Generates maximum download and upload traffic
  - Uses 4 parallel connections for accurate testing
  - 10-second test duration for each direction
  - Displays max achieved speeds
- Auto-refreshing every 2 seconds
- Responsive design for mobile and desktop
- Optimized for Starlink Mini

## Requirements

- Python 3.7+
- Starlink dish connected to local network at 192.168.100.1
- Virtual environment (recommended)

## Installation

1. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Make sure your Starlink dish is connected to your local network at 192.168.100.1

2. Start the dashboard:
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
python app.py
```

3. Open your browser to:
```
http://localhost:5001
```

## Usage

### Real-time Monitoring
The dashboard automatically updates every 2 seconds showing current metrics from your Starlink dish.

### Time Range Selection
Use the time range buttons at the top to focus on specific intervals:
- **All Data**: Shows all collected data (up to 500 points)
- **Last 5/15/30 Min**: Zoom into recent data
- **Last 1 Hour**: View the past hour

### Speedtest
Click the **⚡ Run Speedtest** button to test your maximum bandwidth:
- The test runs for ~20 seconds (10 seconds download + 10 seconds upload)
- Uses 4 parallel connections to saturate your connection
- Shows maximum achieved speeds (not averages)
- Normal monitoring continues during the test

## Troubleshooting

- **Connection Error**: Ensure your Starlink dish is accessible at 192.168.100.1
- **gRPC Error**: Make sure the gRPC port (9200) is accessible
- **No Data**: Wait a few seconds for the first metrics to be collected

## Technology Stack

- **Backend**: Flask, starlink-grpc-core
- **Frontend**: HTML5, Chart.js
- **API**: Starlink gRPC API

## References

- [starlink-grpc-core on PyPI](https://pypi.org/project/starlink-grpc-core/)
