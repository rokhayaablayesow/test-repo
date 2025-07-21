#!/usr/bin/env python3
import sys
import signal
import argparse
import logging
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from rtmp_server import RTMPServer
from stream_manager import StreamManager
from video_processor import VideoProcessor

def setup_logging(level=logging.INFO):
    """Configure logging for the application"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('rtmp_server.log')
        ]
    )

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    print("\nReceived shutdown signal. Stopping server...")
    global server
    if server:
        server.stop()
    sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description='RTMP Streaming Server')
    parser.add_argument('--host', default='0.0.0.0', 
                       help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=1935,
                       help='Port to bind to (default: 1935)')
    parser.add_argument('--log-level', default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level (default: INFO)')
    parser.add_argument('--max-streams', type=int, default=100,
                       help='Maximum concurrent streams (default: 100)')
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = getattr(logging, args.log_level.upper())
    setup_logging(log_level)
    
    logger = logging.getLogger(__name__)
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and start server
    global server
    server = RTMPServer(host=args.host, port=args.port)
    
    try:
        logger.info(f"Starting RTMP server on {args.host}:{args.port}")
        logger.info(f"Maximum concurrent streams: {args.max_streams}")
        logger.info("Press Ctrl+C to stop the server")
        
        server.start()
        
    except Exception as e:
        logger.error(f"Server error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())