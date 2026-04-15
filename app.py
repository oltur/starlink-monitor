#!/usr/bin/env python3
"""
Starlink Metrics Dashboard
A Flask web server that displays real-time Starlink metrics
"""

from datetime import datetime
from flask import Flask, render_template, jsonify, request, Response
from collections import deque
import starlink_grpc
import speedtest
import threading

app = Flask(__name__)

# Store recent metrics (keep last 500 data points for better time range selection)
metrics_history = {
    'timestamps': deque(maxlen=500),
    'download_speed': deque(maxlen=500),
    'upload_speed': deque(maxlen=500),
    'latency': deque(maxlen=500),
    'ping_drop_rate': deque(maxlen=500),
    'uptime': deque(maxlen=500),
    'obstructed': deque(maxlen=500),
    'fraction_obstructed': deque(maxlen=500),
    'azimuth': deque(maxlen=500),
    'elevation': deque(maxlen=500),
    'gps_sats': deque(maxlen=500),
    'snr_above_noise': deque(maxlen=500)
}

STARLINK_ADDRESS = '192.168.100.1:9200'

# Create a persistent context for efficiency
context = starlink_grpc.ChannelContext(target=STARLINK_ADDRESS)

def get_starlink_status():
    """Fetch status from Starlink dish via gRPC"""
    try:
        status = starlink_grpc.get_status(context=context)

        # Extract uptime from device_state
        uptime = 0
        if hasattr(status, 'device_state') and status.device_state:
            uptime = status.device_state.uptime_s if hasattr(status.device_state, 'uptime_s') else 0

        # Obstruction statistics
        obstructed = False
        fraction_obstructed = 0
        if hasattr(status, 'obstruction_stats') and status.obstruction_stats:
            obs = status.obstruction_stats
            obstructed = obs.currently_obstructed if hasattr(obs, 'currently_obstructed') else False
            fraction_obstructed = obs.fraction_obstructed if hasattr(obs, 'fraction_obstructed') else 0

        # GPS stats
        gps_sats = 0
        gps_valid = False
        if hasattr(status, 'gps_stats') and status.gps_stats:
            gps = status.gps_stats
            gps_sats = gps.gps_sats if hasattr(gps, 'gps_sats') else 0
            gps_valid = gps.gps_valid if hasattr(gps, 'gps_valid') else False

        # Device info
        device_info_str = ""
        if hasattr(status, 'device_info') and status.device_info:
            info = status.device_info
            hw = info.hardware_version if hasattr(info, 'hardware_version') else 'N/A'
            sw = info.software_version if hasattr(info, 'software_version') else 'N/A'
            device_info_str = f"{hw} | {sw}"

        print(f"✓ DL: {status.downlink_throughput_bps / 1_000_000:.2f} Mbps, UL: {status.uplink_throughput_bps / 1_000_000:.2f} Mbps, Latency: {status.pop_ping_latency_ms:.1f}ms, Drop: {status.pop_ping_drop_rate*100:.2f}%")

        return {
            'success': True,
            'downlink_throughput': status.downlink_throughput_bps / 1_000_000,
            'uplink_throughput': status.uplink_throughput_bps / 1_000_000,
            'pop_ping_latency': status.pop_ping_latency_ms,
            'pop_ping_drop_rate': status.pop_ping_drop_rate * 100,  # Convert to percentage
            'uptime': uptime,
            'obstructed': obstructed,
            'fraction_obstructed': fraction_obstructed * 100,  # Convert to percentage
            'azimuth': status.boresight_azimuth_deg if hasattr(status, 'boresight_azimuth_deg') else 0,
            'elevation': status.boresight_elevation_deg if hasattr(status, 'boresight_elevation_deg') else 0,
            'gps_sats': gps_sats,
            'gps_valid': gps_valid,
            'snr_above_noise': 1 if status.is_snr_above_noise_floor else 0,
            'device_info': device_info_str
        }

    except starlink_grpc.GrpcError as e:
        print(f"gRPC Error: {str(e)}")
        return {'success': False, 'error': f'gRPC error: {str(e)}'}
    except Exception as e:
        print(f"Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': f'Error: {str(e)}'}

def update_metrics():
    """Update metrics history with latest data"""
    data = get_starlink_status()

    if data['success']:
        timestamp = datetime.now().strftime('%H:%M:%S')
        metrics_history['timestamps'].append(timestamp)
        metrics_history['download_speed'].append(data.get('downlink_throughput', 0))
        metrics_history['upload_speed'].append(data.get('uplink_throughput', 0))
        metrics_history['latency'].append(data.get('pop_ping_latency', 0))
        metrics_history['ping_drop_rate'].append(data.get('pop_ping_drop_rate', 0))
        metrics_history['uptime'].append(data.get('uptime', 0))
        metrics_history['obstructed'].append(1 if data.get('obstructed', False) else 0)
        metrics_history['fraction_obstructed'].append(data.get('fraction_obstructed', 0))
        metrics_history['azimuth'].append(data.get('azimuth', 0))
        metrics_history['elevation'].append(data.get('elevation', 0))
        metrics_history['gps_sats'].append(data.get('gps_sats', 0))
        metrics_history['snr_above_noise'].append(data.get('snr_above_noise', 0))

@app.route('/')
def index():
    """Serve the main dashboard page"""
    return render_template('index.html')

@app.route('/api/metrics')
def api_metrics():
    """API endpoint to get current metrics"""
    update_metrics()

    return jsonify({
        'timestamps': list(metrics_history['timestamps']),
        'download_speed': list(metrics_history['download_speed']),
        'upload_speed': list(metrics_history['upload_speed']),
        'latency': list(metrics_history['latency']),
        'ping_drop_rate': list(metrics_history['ping_drop_rate']),
        'uptime': list(metrics_history['uptime']),
        'obstructed': list(metrics_history['obstructed']),
        'fraction_obstructed': list(metrics_history['fraction_obstructed']),
        'azimuth': list(metrics_history['azimuth']),
        'elevation': list(metrics_history['elevation']),
        'gps_sats': list(metrics_history['gps_sats']),
        'snr_above_noise': list(metrics_history['snr_above_noise'])
    })

@app.route('/api/status')
def api_status():
    """API endpoint to get current status"""
    data = get_starlink_status()
    return jsonify(data)

speedtest_status = {
    'running': False,
    'progress': '',
    'download': 0,
    'upload': 0,
    'ping': 0,
    'server': '',
    'error': None
}

def run_speedtest_thread():
    """Run speedtest in background thread"""
    global speedtest_status

    try:
        speedtest_status['running'] = True
        speedtest_status['progress'] = 'Initializing speedtest...'
        speedtest_status['error'] = None

        # Create speedtest instance
        st = speedtest.Speedtest()

        speedtest_status['progress'] = 'Finding best server...'
        st.get_best_server()
        speedtest_status['server'] = f"{st.best['sponsor']} ({st.best['name']})"

        speedtest_status['progress'] = 'Testing download speed...'
        download_speed = st.download() / 1_000_000  # Convert to Mbps
        speedtest_status['download'] = round(download_speed, 2)

        speedtest_status['progress'] = 'Testing upload speed...'
        upload_speed = st.upload() / 1_000_000  # Convert to Mbps
        speedtest_status['upload'] = round(upload_speed, 2)

        speedtest_status['ping'] = round(st.results.ping, 1)
        speedtest_status['progress'] = 'Complete!'

    except Exception as e:
        speedtest_status['error'] = str(e)
        speedtest_status['progress'] = f'Error: {str(e)}'
        print(f"Speedtest error: {e}")
    finally:
        speedtest_status['running'] = False

@app.route('/api/speedtest/start', methods=['POST'])
def start_speedtest():
    """Start a speedtest in background"""
    global speedtest_status

    if speedtest_status['running']:
        return jsonify({'error': 'Speedtest already running'}), 400

    # Reset status
    speedtest_status = {
        'running': True,
        'progress': 'Starting...',
        'download': 0,
        'upload': 0,
        'ping': 0,
        'server': '',
        'error': None
    }

    # Run in background thread
    thread = threading.Thread(target=run_speedtest_thread)
    thread.daemon = True
    thread.start()

    return jsonify({'status': 'started'})

@app.route('/api/speedtest/status')
def get_speedtest_status():
    """Get current speedtest status"""
    return jsonify(speedtest_status)

if __name__ == '__main__':
    print("Starting Starlink Metrics Dashboard...")
    print(f"Connecting to Starlink at {STARLINK_ADDRESS}")
    print("Dashboard will be available at http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)
