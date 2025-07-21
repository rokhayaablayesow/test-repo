#!/usr/bin/env python3
import struct
import logging
from typing import Tuple, Optional, List
from enum import Enum

logger = logging.getLogger(__name__)

class VideoCodec(Enum):
    H264 = "h264"
    H265 = "h265"
    VP8 = "vp8"
    VP9 = "vp9"

class AudioCodec(Enum):
    AAC = "aac"
    MP3 = "mp3"
    OPUS = "opus"

class NALUnitType(Enum):
    SPS = 7  # Sequence Parameter Set
    PPS = 8  # Picture Parameter Set  
    IDR = 5  # Instantaneous Decoder Refresh
    NON_IDR = 1  # Non-IDR coded slice

class H264Parser:
    def __init__(self):
        self.sps_data = None
        self.pps_data = None
        self.profile_level = None
    
    def parse_avcc_header(self, data: bytes) -> dict:
        """Parse AVCC (AVC Configuration Record) header"""
        if len(data) < 7:
            return {}
        
        config_version = data[0]
        profile = data[1] 
        compatibility = data[2]
        level = data[3]
        nal_size_length = (data[4] & 0x03) + 1
        sps_count = data[5] & 0x1F
        
        offset = 6
        sps_list = []
        
        for _ in range(sps_count):
            if offset + 2 > len(data):
                break
            sps_length = struct.unpack(">H", data[offset:offset+2])[0]
            offset += 2
            
            if offset + sps_length > len(data):
                break
            sps_data = data[offset:offset+sps_length]
            sps_list.append(sps_data)
            offset += sps_length
        
        pps_count = data[offset] if offset < len(data) else 0
        offset += 1
        pps_list = []
        
        for _ in range(pps_count):
            if offset + 2 > len(data):
                break
            pps_length = struct.unpack(">H", data[offset:offset+2])[0]
            offset += 2
            
            if offset + pps_length > len(data):
                break
            pps_data = data[offset:offset+pps_length]
            pps_list.append(pps_data)
            offset += pps_length
        
        return {
            "version": config_version,
            "profile": profile,
            "level": level,
            "nal_size_length": nal_size_length,
            "sps": sps_list,
            "pps": pps_list
        }
    
    def is_keyframe(self, data: bytes) -> bool:
        """Determine if frame is a keyframe (IDR)"""
        if len(data) < 5:
            return False
        
        # Skip AVCC length prefix if present
        offset = 0
        if len(data) > 4:
            length = struct.unpack(">I", data[:4])[0]
            if length + 4 <= len(data):
                offset = 4
        
        # Find NAL unit type
        while offset < len(data):
            # Look for start code (0x000001 or 0x00000001)
            if offset + 3 < len(data):
                if data[offset:offset+3] == b'\x00\x00\x01':
                    nal_type = data[offset+3] & 0x1F
                    return nal_type == NALUnitType.IDR.value
                elif (offset + 4 < len(data) and 
                      data[offset:offset+4] == b'\x00\x00\x00\x01'):
                    nal_type = data[offset+4] & 0x1F
                    return nal_type == NALUnitType.IDR.value
            offset += 1
        
        return False

class AACParser:
    def __init__(self):
        self.audio_config = None
    
    def parse_audio_specific_config(self, data: bytes) -> dict:
        """Parse AAC Audio Specific Config"""
        if len(data) < 2:
            return {}
        
        # Extract audio object type and sampling frequency
        audio_object_type = (data[0] >> 3) & 0x1F
        sampling_freq_index = ((data[0] & 0x07) << 1) | ((data[1] >> 7) & 0x01)
        channel_config = (data[1] >> 3) & 0x0F
        
        sampling_rates = [
            96000, 88200, 64000, 48000, 44100, 32000,
            24000, 22050, 16000, 12000, 11025, 8000, 7350
        ]
        
        sampling_rate = (sampling_rates[sampling_freq_index] 
                        if sampling_freq_index < len(sampling_rates) else 0)
        
        return {
            "audio_object_type": audio_object_type,
            "sampling_rate": sampling_rate, 
            "channel_config": channel_config
        }

class VideoProcessor:
    def __init__(self):
        self.h264_parser = H264Parser()
        self.aac_parser = AACParser()
        self.video_config = None
        self.audio_config = None
    
    def process_video_config(self, data: bytes) -> bool:
        """Process video configuration data (SPS/PPS)"""
        try:
            config = self.h264_parser.parse_avcc_header(data)
            if config:
                self.video_config = config
                logger.info(f"Video config: {config['profile']}/{config['level']}")
                return True
        except Exception as e:
            logger.error(f"Error parsing video config: {e}")
        return False
    
    def process_audio_config(self, data: bytes) -> bool:
        """Process audio configuration data"""
        try:
            config = self.aac_parser.parse_audio_specific_config(data)
            if config:
                self.audio_config = config
                logger.info(f"Audio config: {config['sampling_rate']}Hz, "
                          f"{config['channel_config']} channels")
                return True
        except Exception as e:
            logger.error(f"Error parsing audio config: {e}")
        return False
    
    def process_video_frame(self, timestamp: int, data: bytes) -> dict:
        """Process a video frame and extract metadata"""
        is_keyframe = self.h264_parser.is_keyframe(data)
        
        return {
            "timestamp": timestamp,
            "data": data,
            "size": len(data),
            "is_keyframe": is_keyframe,
            "codec": VideoCodec.H264.value
        }
    
    def process_audio_frame(self, timestamp: int, data: bytes) -> dict:
        """Process an audio frame and extract metadata"""
        return {
            "timestamp": timestamp,
            "data": data,
            "size": len(data),
            "codec": AudioCodec.AAC.value
        }
    
    def get_video_info(self) -> Optional[dict]:
        """Get video stream information"""
        if self.video_config:
            return {
                "codec": VideoCodec.H264.value,
                "profile": self.video_config.get("profile"),
                "level": self.video_config.get("level"),
                "has_config": True
            }
        return None
    
    def get_audio_info(self) -> Optional[dict]:
        """Get audio stream information"""
        if self.audio_config:
            return {
                "codec": AudioCodec.AAC.value,
                "sampling_rate": self.audio_config.get("sampling_rate"),
                "channels": self.audio_config.get("channel_config"),
                "has_config": True
            }
        return None

class StreamValidator:
    """Validates incoming stream data"""
    
    @staticmethod
    def validate_rtmp_chunk(data: bytes) -> bool:
        """Validate RTMP chunk format"""
        if len(data) < 1:
            return False
        
        # Basic header validation
        basic_header = data[0]
        fmt = (basic_header >> 6) & 0x03
        csid = basic_header & 0x3F
        
        # Check if chunk stream ID is valid
        if csid == 0:  # 2-byte chunk stream ID
            return len(data) >= 2
        elif csid == 1:  # 3-byte chunk stream ID  
            return len(data) >= 3
        
        return True
    
    @staticmethod
    def validate_flv_tag(data: bytes) -> bool:
        """Validate FLV tag format"""
        if len(data) < 11:  # FLV tag header size
            return False
        
        tag_type = data[0]
        data_size = (data[1] << 16) | (data[2] << 8) | data[3]
        
        # Check tag type (8=audio, 9=video, 18=script)
        if tag_type not in [8, 9, 18]:
            return False
        
        # Check if data size matches
        if len(data) < 11 + data_size:
            return False
        
        return True

def create_test_video_frame(timestamp: int, is_keyframe: bool = False) -> bytes:
    """Create test H.264 video frame data"""
    if is_keyframe:
        # IDR frame with SPS/PPS
        sps = b'\x00\x00\x00\x01\x67\x42\x00\x28\x8d\x8d\x40\xa0\xfd\x00\xda\x14\x26\xa0'
        pps = b'\x00\x00\x00\x01\x68\xce\x06\xe2'  
        idr = b'\x00\x00\x00\x01\x65\x88\x82\x00\x00\x03\x00\x02\x00\x00\x03\x00\x01\x08'
        return sps + pps + idr
    else:
        # Non-IDR frame
        return b'\x00\x00\x00\x01\x61\xe9\x10\x20\x00\x08\x80\x00\x01\x42\x80'

def create_test_audio_frame(timestamp: int) -> bytes:
    """Create test AAC audio frame data"""
    # AAC frame with ADTS header
    return b'\xff\xf9\x50\x80\x01\x1f\xfc\x21\x10\xd3\x20\x08\x20\x0c\x20\x08'

if __name__ == "__main__":
    # Test du processeur vidéo
    processor = VideoProcessor()
    
    # Test avec des frames simulées
    video_frame = create_test_video_frame(1000, True)
    audio_frame = create_test_audio_frame(1000)
    
    video_info = processor.process_video_frame(1000, video_frame)
    audio_info = processor.process_audio_frame(1000, audio_frame)
    
    print(f"Video frame: {video_info}")
    print(f"Audio frame: {audio_info}")
    
    # Test de validation
    validator = StreamValidator()
    print(f"Video frame valid: {validator.validate_flv_tag(b'\x09\x00\x00\x10' + b'\x00' * 16)}")
    print(f"Audio frame valid: {validator.validate_flv_tag(b'\x08\x00\x00\x08' + b'\x00' * 8)}")