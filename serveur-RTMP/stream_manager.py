#!/usr/bin/env python3
import threading
import time
import logging
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class StreamStatus(Enum):
    IDLE = "idle"
    CONNECTING = "connecting" 
    PUBLISHING = "publishing"
    ERROR = "error"

@dataclass
class VideoFrame:
    timestamp: int
    data: bytes
    is_keyframe: bool
    codec: str = "h264"

@dataclass
class AudioFrame:
    timestamp: int
    data: bytes
    codec: str = "aac"

@dataclass
class StreamMetadata:
    width: int
    height: int
    fps: int
    video_bitrate: int
    audio_bitrate: int
    video_codec: str
    audio_codec: str

class StreamPublisher:
    def __init__(self, stream_key: str, callback: Callable = None):
        self.stream_key = stream_key
        self.status = StreamStatus.IDLE
        self.metadata: Optional[StreamMetadata] = None
        self.video_frames: List[VideoFrame] = []
        self.audio_frames: List[AudioFrame] = []
        self.subscribers: List['StreamSubscriber'] = []
        self.callback = callback
        self.lock = threading.Lock()
        self.last_keyframe: Optional[VideoFrame] = None
        
    def start_publishing(self, metadata: StreamMetadata):
        with self.lock:
            self.status = StreamStatus.PUBLISHING
            self.metadata = metadata
            logger.info(f"Started publishing stream: {self.stream_key}")
            if self.callback:
                self.callback("publish_start", self.stream_key)
    
    def stop_publishing(self):
        with self.lock:
            self.status = StreamStatus.IDLE
            self.video_frames.clear()
            self.audio_frames.clear()
            logger.info(f"Stopped publishing stream: {self.stream_key}")
            if self.callback:
                self.callback("publish_stop", self.stream_key)
    
    def add_video_frame(self, frame: VideoFrame):
        with self.lock:
            if self.status != StreamStatus.PUBLISHING:
                return
                
            self.video_frames.append(frame)
            if frame.is_keyframe:
                self.last_keyframe = frame
            
            # Broadcast to subscribers
            for subscriber in self.subscribers[:]:
                try:
                    subscriber.send_video_frame(frame)
                except Exception as e:
                    logger.error(f"Error sending frame to subscriber: {e}")
                    self.subscribers.remove(subscriber)
    
    def add_audio_frame(self, frame: AudioFrame):
        with self.lock:
            if self.status != StreamStatus.PUBLISHING:
                return
                
            self.audio_frames.append(frame)
            
            # Broadcast to subscribers  
            for subscriber in self.subscribers[:]:
                try:
                    subscriber.send_audio_frame(frame)
                except Exception as e:
                    logger.error(f"Error sending audio to subscriber: {e}")
                    self.subscribers.remove(subscriber)
    
    def add_subscriber(self, subscriber: 'StreamSubscriber'):
        with self.lock:
            self.subscribers.append(subscriber)
            
            # Send metadata and last keyframe to new subscriber
            if self.metadata:
                subscriber.send_metadata(self.metadata)
            if self.last_keyframe:
                subscriber.send_video_frame(self.last_keyframe)
            
            logger.info(f"Added subscriber to stream: {self.stream_key}")

class StreamSubscriber:
    def __init__(self, client_id: str, output_callback: Callable):
        self.client_id = client_id
        self.output_callback = output_callback
        self.connected = True
    
    def send_metadata(self, metadata: StreamMetadata):
        if self.connected:
            self.output_callback("metadata", metadata)
    
    def send_video_frame(self, frame: VideoFrame):
        if self.connected:
            self.output_callback("video", frame)
    
    def send_audio_frame(self, frame: AudioFrame):
        if self.connected:
            self.output_callback("audio", frame)
    
    def disconnect(self):
        self.connected = False

class StreamManager:
    def __init__(self):
        self.publishers: Dict[str, StreamPublisher] = {}
        self.lock = threading.Lock()
        self.stats = {
            "total_streams": 0,
            "active_streams": 0,
            "total_viewers": 0
        }
    
    def create_publisher(self, stream_key: str) -> StreamPublisher:
        with self.lock:
            if stream_key not in self.publishers:
                publisher = StreamPublisher(stream_key, self._stream_callback)
                self.publishers[stream_key] = publisher
                self.stats["total_streams"] += 1
                logger.info(f"Created publisher for stream: {stream_key}")
            return self.publishers[stream_key]
    
    def get_publisher(self, stream_key: str) -> Optional[StreamPublisher]:
        return self.publishers.get(stream_key)
    
    def subscribe_to_stream(self, stream_key: str, subscriber: StreamSubscriber) -> bool:
        publisher = self.get_publisher(stream_key)
        if publisher and publisher.status == StreamStatus.PUBLISHING:
            publisher.add_subscriber(subscriber)
            with self.lock:
                self.stats["total_viewers"] += 1
            return True
        return False
    
    def remove_publisher(self, stream_key: str):
        with self.lock:
            if stream_key in self.publishers:
                publisher = self.publishers[stream_key]
                publisher.stop_publishing()
                del self.publishers[stream_key]
                if self.stats["active_streams"] > 0:
                    self.stats["active_streams"] -= 1
                logger.info(f"Removed publisher: {stream_key}")
    
    def _stream_callback(self, event: str, stream_key: str):
        with self.lock:
            if event == "publish_start":
                self.stats["active_streams"] += 1
            elif event == "publish_stop":
                if self.stats["active_streams"] > 0:
                    self.stats["active_streams"] -= 1
    
    def get_stats(self) -> Dict:
        with self.lock:
            return self.stats.copy()
    
    def get_active_streams(self) -> List[str]:
        with self.lock:
            return [
                key for key, pub in self.publishers.items() 
                if pub.status == StreamStatus.PUBLISHING
            ]
    
    def cleanup_inactive_streams(self):
        """Remove streams that haven't been active for a while"""
        with self.lock:
            to_remove = []
            for key, publisher in self.publishers.items():
                if (publisher.status == StreamStatus.IDLE and 
                    len(publisher.video_frames) == 0):
                    to_remove.append(key)
            
            for key in to_remove:
                del self.publishers[key]
                logger.info(f"Cleaned up inactive stream: {key}")

def create_test_frames():
    """Génère des frames de test pour le streaming"""
    video_frame = VideoFrame(
        timestamp=int(time.time() * 1000),
        data=b"\x00" * 1024,  # Données vidéo simulées
        is_keyframe=True
    )
    
    audio_frame = AudioFrame(
        timestamp=int(time.time() * 1000),
        data=b"\x00" * 256   # Données audio simulées
    )
    
    return video_frame, audio_frame

if __name__ == "__main__":
    # Test du StreamManager
    manager = StreamManager()
    
    # Créer un publisher
    publisher = manager.create_publisher("test_stream")
    
    # Simuler des métadonnées
    metadata = StreamMetadata(
        width=1920, height=1080, fps=30,
        video_bitrate=5000, audio_bitrate=128,
        video_codec="h264", audio_codec="aac"
    )
    
    publisher.start_publishing(metadata)
    
    # Générer quelques frames de test
    for i in range(5):
        video_frame, audio_frame = create_test_frames()
        publisher.add_video_frame(video_frame)
        publisher.add_audio_frame(audio_frame)
        time.sleep(0.033)  # ~30 FPS
    
    print(f"Stats: {manager.get_stats()}")
    print(f"Active streams: {manager.get_active_streams()}")