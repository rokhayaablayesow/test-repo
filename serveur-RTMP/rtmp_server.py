#!/usr/bin/env python3
import socket
import threading
import struct
import time
import logging
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RTMPHandshake:
    def __init__(self):
        self.c0c1_received = False
        self.s0s1_sent = False
        self.c2_received = False
        self.s2_sent = False
    
    def process_c0c1(self, data: bytes) -> bytes:
        if len(data) < 1537:
            return b""
        
        version = data[0]
        if version != 3:
            logger.error(f"Unsupported RTMP version: {version}")
            return b""
        
        c1 = data[1:1537]
        timestamp = struct.unpack(">I", c1[:4])[0]
        
        s0 = struct.pack("B", 3)
        s1_timestamp = int(time.time())
        s1 = struct.pack(">I", s1_timestamp) + b"\x00" * 4 + b"\x01" * 1528
        
        self.c0c1_received = True
        self.s0s1_sent = True
        
        return s0 + s1
    
    def process_c2(self, data: bytes) -> bytes:
        if len(data) < 1536:
            return b""
        
        c2 = data[:1536]
        s2 = c2
        
        self.c2_received = True
        self.s2_sent = True
        
        return s2

class RTMPMessage:
    def __init__(self, fmt: int, csid: int, timestamp: int, length: int, 
                 type_id: int, stream_id: int, payload: bytes):
        self.fmt = fmt
        self.csid = csid
        self.timestamp = timestamp
        self.length = length
        self.type_id = type_id
        self.stream_id = stream_id
        self.payload = payload

class RTMPStream:
    def __init__(self, stream_key: str):
        self.stream_key = stream_key
        self.is_publishing = False
        self.subscribers: List[socket.socket] = []
        self.metadata = {}
        self.video_config = None
        self.audio_config = None

class RTMPConnection:
    def __init__(self, client_socket: socket.socket, address, server):
        self.socket = client_socket
        self.address = address
        self.server = server
        self.handshake = RTMPHandshake()
        self.stream: Optional[RTMPStream] = None
        self.chunk_size = 128
        self.is_publisher = False
        
    def handle(self):
        try:
            while True:
                data = self.socket.recv(4096)
                if not data:
                    break
                
                if not self.handshake.s2_sent:
                    self._handle_handshake(data)
                else:
                    self._handle_rtmp_messages(data)
                    
        except Exception as e:
            logger.error(f"Connection error: {e}")
        finally:
            self._cleanup()
    
    def _handle_handshake(self, data: bytes):
        if not self.handshake.c0c1_received:
            response = self.handshake.process_c0c1(data)
            if response:
                self.socket.send(response)
        elif not self.handshake.c2_received:
            response = self.handshake.process_c2(data)
            if response:
                self.socket.send(response)
                logger.info(f"RTMP handshake completed with {self.address}")
    
    def _handle_rtmp_messages(self, data: bytes):
        # Traitement basique des messages RTMP
        # Dans une implémentation complète, il faudrait parser les chunks RTMP
        pass
    
    def _cleanup(self):
        if self.stream and self.is_publisher:
            self.stream.is_publishing = False
        self.socket.close()
        logger.info(f"Connection closed: {self.address}")

class RTMPServer:
    def __init__(self, host: str = "0.0.0.0", port: int = 1935):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.streams: Dict[str, RTMPStream] = {}
        self.connections: List[RTMPConnection] = []
        self.running = False
    
    def start(self):
        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            self.running = True
            
            logger.info(f"RTMP Server started on {self.host}:{self.port}")
            
            while self.running:
                client_socket, address = self.socket.accept()
                logger.info(f"New connection from {address}")
                
                connection = RTMPConnection(client_socket, address, self)
                self.connections.append(connection)
                
                thread = threading.Thread(target=connection.handle)
                thread.daemon = True
                thread.start()
                
        except KeyboardInterrupt:
            logger.info("Server shutdown requested")
        finally:
            self.stop()
    
    def stop(self):
        self.running = False
        for conn in self.connections:
            conn.socket.close()
        self.socket.close()
        logger.info("RTMP Server stopped")
    
    def create_stream(self, stream_key: str) -> RTMPStream:
        if stream_key not in self.streams:
            self.streams[stream_key] = RTMPStream(stream_key)
        return self.streams[stream_key]
    
    def publish_to_stream(self, stream_key: str, data: bytes):
        if stream_key in self.streams:
            stream = self.streams[stream_key]
            for subscriber in stream.subscribers:
                try:
                    subscriber.send(data)
                except:
                    stream.subscribers.remove(subscriber)

if __name__ == "__main__":
    server = RTMPServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.stop()