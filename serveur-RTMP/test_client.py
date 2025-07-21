#!/usr/bin/env python3
import socket
import struct
import time
import threading
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RTMPTestClient:
    """Simple RTMP test client for testing the server"""
    
    def __init__(self, host: str = "localhost", port: int = 1935):
        self.host = host
        self.port = port
        self.socket: Optional[socket.socket] = None
        self.connected = False
        self.stream_key = "test_stream"
    
    def connect(self) -> bool:
        """Connect to RTMP server and perform handshake"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            
            # Send C0 + C1
            c0 = struct.pack("B", 3)  # RTMP version 3
            c1_timestamp = int(time.time())
            c1 = struct.pack(">I", c1_timestamp) + b"\x00" * 4 + b"\x01" * 1528
            
            self.socket.send(c0 + c1)
            logger.info("Sent C0+C1 handshake")
            
            # Receive S0 + S1
            s0s1 = self.socket.recv(1537)
            if len(s0s1) >= 1537 and s0s1[0] == 3:
                logger.info("Received S0+S1 handshake")
                
                # Send C2 (echo of S1)
                c2 = s0s1[1:1537]
                self.socket.send(c2)
                logger.info("Sent C2 handshake")
                
                # Receive S2
                s2 = self.socket.recv(1536)
                if len(s2) == 1536:
                    logger.info("Received S2 handshake - Connection established")
                    self.connected = True
                    return True
            
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            
        return False
    
    def send_connect_message(self):
        """Send RTMP connect message"""
        # This is a simplified version - real RTMP connect involves AMF encoding
        connect_data = b"connect_message_placeholder"
        self._send_rtmp_message(20, 3, connect_data)  # Command message
    
    def send_publish_message(self):
        """Send RTMP publish message"""
        publish_data = f"publish_{self.stream_key}".encode()
        self._send_rtmp_message(20, 4, publish_data)  # Command message
    
    def send_video_data(self, data: bytes, timestamp: int):
        """Send video data"""
        self._send_rtmp_message(9, 4, data, timestamp)  # Video message
    
    def send_audio_data(self, data: bytes, timestamp: int):
        """Send audio data"""
        self._send_rtmp_message(8, 4, data, timestamp)  # Audio message
    
    def _send_rtmp_message(self, msg_type: int, stream_id: int, 
                          payload: bytes, timestamp: int = 0):
        """Send RTMP message (simplified)"""
        if not self.connected or not self.socket:
            return
        
        try:
            # Basic header (fmt=0, csid=3)
            basic_header = 0x03
            
            # Message header
            msg_header = struct.pack(">IBHIB", 
                                   timestamp & 0xFFFFFF,    # timestamp (3 bytes)
                                   len(payload),            # message length  
                                   msg_type,               # message type
                                   stream_id)              # message stream ID
            
            # Send chunk
            chunk_data = struct.pack("B", basic_header) + msg_header + payload
            self.socket.send(chunk_data)
            
        except Exception as e:
            logger.error(f"Error sending message: {e}")
    
    def simulate_stream(self, duration: int = 30):
        """Simulate streaming for testing"""
        if not self.connected:
            logger.error("Not connected to server")
            return
        
        logger.info(f"Starting stream simulation for {duration} seconds")
        
        # Send connect and publish messages
        self.send_connect_message()
        time.sleep(0.1)
        self.send_publish_message()
        time.sleep(0.1)
        
        start_time = time.time()
        frame_count = 0
        
        try:
            while time.time() - start_time < duration:
                timestamp = int((time.time() - start_time) * 1000)
                
                # Send video frame every ~33ms (30 FPS)
                if frame_count % 30 == 0:  # Keyframe every 30 frames
                    video_data = self._create_test_keyframe()
                else:
                    video_data = self._create_test_frame()
                
                self.send_video_data(video_data, timestamp)
                
                # Send audio frame
                audio_data = self._create_test_audio()
                self.send_audio_data(audio_data, timestamp)
                
                frame_count += 1
                time.sleep(1/30)  # 30 FPS
                
                if frame_count % 300 == 0:  # Log every 10 seconds
                    logger.info(f"Sent {frame_count} frames")
        
        except KeyboardInterrupt:
            logger.info("Stream interrupted by user")
        except Exception as e:
            logger.error(f"Streaming error: {e}")
        
        logger.info(f"Stream completed. Total frames: {frame_count}")
    
    def _create_test_keyframe(self) -> bytes:
        """Create test keyframe data"""
        return b"\x17\x00\x00\x00\x00" + b"\x01" * 100  # FLV video keyframe header + data
    
    def _create_test_frame(self) -> bytes:
        """Create test frame data"""
        return b"\x27\x01\x00\x00\x00" + b"\x01" * 50   # FLV video frame header + data
    
    def _create_test_audio(self) -> bytes:
        """Create test audio data"""
        return b"\xaf\x01" + b"\x01" * 20  # FLV audio header + data
    
    def disconnect(self):
        """Disconnect from server"""
        self.connected = False
        if self.socket:
            self.socket.close()
            self.socket = None
        logger.info("Disconnected from server")

def main():
    """Test client main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='RTMP Test Client')
    parser.add_argument('--host', default='localhost',
                       help='RTMP server host (default: localhost)')
    parser.add_argument('--port', type=int, default=1935,
                       help='RTMP server port (default: 1935)')
    parser.add_argument('--duration', type=int, default=30,
                       help='Stream duration in seconds (default: 30)')
    parser.add_argument('--stream-key', default='test_stream',
                       help='Stream key (default: test_stream)')
    
    args = parser.parse_args()
    
    client = RTMPTestClient(args.host, args.port)
    client.stream_key = args.stream_key
    
    try:
        if client.connect():
            logger.info(f"Connected to RTMP server at {args.host}:{args.port}")
            client.simulate_stream(args.duration)
        else:
            logger.error("Failed to connect to RTMP server")
            return 1
            
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
    finally:
        client.disconnect()
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())