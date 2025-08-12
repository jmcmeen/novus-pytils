"""Audio file operations and utilities.

This module consolidates all audio-related file operations including counting,
retrieving, parsing WAV files, and comprehensive audio analysis.
"""
import wave
import struct
import numpy as np
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from pathlib import Path

from novus_pytils.file_operations.general import get_files_by_extension
from novus_pytils.globals import SUPPORTED_AUDIO_EXTENSIONS
from novus_pytils.utils.hash import get_file_md5_hash


def count_audio_files(audio_folder_path):
    """Count the number of audio files in a folder.

    Args:
        audio_folder_path (str): The path to the folder containing the audio files.

    Returns:
        int: The number of audio files in the folder.
    """
    files = get_files_by_extension(audio_folder_path, SUPPORTED_AUDIO_EXTENSIONS)
    return len(files)


def get_audio_files(audio_folder_path, file_extensions=SUPPORTED_AUDIO_EXTENSIONS):
    """Get a list of audio files in a folder.

    Args:
        audio_folder_path (str): The path to the folder containing the audio files.
        file_extensions (list, optional): A list of file extensions to consider as audio files.

    Returns:
        list: A list of audio file paths.
    """
    files = get_files_by_extension(audio_folder_path, file_extensions, relative=True)
    return files


def get_wav_files(dir):
    """Get all WAV files in a directory.

    Args:
        dir (str): The directory to search for WAV files.

    Returns:
        list: A list of paths to WAV files in the directory.
    """
    return get_files_by_extension(dir, ['.wav'])


# WAV Parser Classes and Functions
class WAVError(Exception):
    """Base exception for WAV parsing errors."""
    pass


class InvalidWAVFormatError(WAVError):
    """Raised when WAV file format is invalid or unsupported."""
    pass


class CorruptedFileError(WAVError):
    """Raised when WAV file appears to be corrupted."""
    pass


@dataclass
class WAVFormat:
    """WAV format information."""
    audio_format: int
    channels: int
    sample_rate: int
    byte_rate: int
    block_align: int
    bits_per_sample: int
    
    @property
    def is_pcm(self) -> bool:
        """Check if format is PCM (uncompressed)."""
        return self.audio_format == 1
    
    @property
    def duration_seconds(self) -> float:
        """Calculate duration based on byte rate (requires data size)."""
        return getattr(self, '_duration', 0.0)


@dataclass
class WAVChunk:
    """Represents a RIFF chunk in the WAV file."""
    id: str
    size: int
    data: bytes
    offset: int


class WAVParser:
    """Pure Python WAV file parser."""
    
    def __init__(self, file_path: Union[str, Path]):
        """Initialize parser with file path."""
        self.file_path = Path(file_path)
        self.format_info: Optional[WAVFormat] = None
        self.chunks: Dict[str, WAVChunk] = {}
        self.audio_data: Optional[bytes] = None
        self._file_size = 0
        
    def parse(self) -> Dict:
        """Parse the WAV file and return comprehensive information."""
        if not self.file_path.exists():
            raise FileNotFoundError(f"WAV file not found: {self.file_path}")
        
        self._file_size = self.file_path.stat().st_size
        
        with open(self.file_path, 'rb') as f:
            self._parse_riff_header(f)
            self._parse_chunks(f)
            self._validate_format()
        
        return self.get_info()
    
    def _parse_riff_header(self, f) -> None:
        """Parse the RIFF header."""
        riff_header = f.read(12)
        if len(riff_header) != 12:
            raise CorruptedFileError("File too small to be a valid WAV file")
        
        riff_id, file_size, wave_id = struct.unpack('<4sI4s', riff_header)
        
        if riff_id != b'RIFF':
            raise InvalidWAVFormatError("Not a valid RIFF file")
        
        if wave_id != b'WAVE':
            raise InvalidWAVFormatError("Not a valid WAV file")
    
    def _parse_chunks(self, f) -> None:
        """Parse all chunks in the WAV file."""
        while True:
            chunk_header = f.read(8)
            if len(chunk_header) < 8:
                break
            
            chunk_id, chunk_size = struct.unpack('<4sI', chunk_header)
            chunk_id = chunk_id.decode('ascii', errors='ignore')
            
            chunk_offset = f.tell()
            chunk_data = f.read(chunk_size)
            if len(chunk_data) != chunk_size:
                raise CorruptedFileError(f"Incomplete chunk: {chunk_id}")
            
            self.chunks[chunk_id] = WAVChunk(
                id=chunk_id,
                size=chunk_size,
                data=chunk_data,
                offset=chunk_offset
            )
            
            if chunk_id == 'fmt ':
                self._parse_format_chunk(chunk_data)
            elif chunk_id == 'data':
                self.audio_data = chunk_data
            
            if chunk_size % 2:
                f.read(1)
    
    def _parse_format_chunk(self, data: bytes) -> None:
        """Parse the format chunk."""
        if len(data) < 16:
            raise InvalidWAVFormatError("Format chunk too small")
        
        fmt_data = struct.unpack('<HHIIHH', data[:16])
        
        self.format_info = WAVFormat(
            audio_format=fmt_data[0],
            channels=fmt_data[1],
            sample_rate=fmt_data[2],
            byte_rate=fmt_data[3],
            block_align=fmt_data[4],
            bits_per_sample=fmt_data[5]
        )
        
        if self.audio_data and self.format_info.byte_rate > 0:
            duration = len(self.audio_data) / self.format_info.byte_rate
            self.format_info._duration = duration
    
    def _validate_format(self) -> None:
        """Validate the parsed format."""
        if not self.format_info:
            raise InvalidWAVFormatError("No format chunk found")
        
        if not self.format_info.is_pcm:
            raise InvalidWAVFormatError(
                f"Unsupported audio format: {self.format_info.audio_format} "
                "(only PCM is supported)"
            )
        
        if self.format_info.channels == 0:
            raise InvalidWAVFormatError("Invalid number of channels")
        
        if self.format_info.sample_rate == 0:
            raise InvalidWAVFormatError("Invalid sample rate")
        
        if self.audio_data is None:
            raise InvalidWAVFormatError("No audio data found")
    
    def get_info(self) -> Dict:
        """Get comprehensive information about the WAV file."""
        if not self.format_info:
            raise WAVError("File not parsed yet. Call parse() first.")
        
        info = {
            'file_path': str(self.file_path),
            'file_size': self._file_size,
            'format': {
                'audio_format': self.format_info.audio_format,
                'channels': self.format_info.channels,
                'sample_rate': self.format_info.sample_rate,
                'byte_rate': self.format_info.byte_rate,
                'block_align': self.format_info.block_align,
                'bits_per_sample': self.format_info.bits_per_sample,
                'is_pcm': self.format_info.is_pcm
            },
            'duration_seconds': self.format_info.duration_seconds,
            'audio_data_size': len(self.audio_data) if self.audio_data else 0,
            'sample_count': self._calculate_sample_count(),
            'chunks': {chunk_id: chunk.size for chunk_id, chunk in self.chunks.items()}
        }
        
        return info
    
    def _calculate_sample_count(self) -> int:
        """Calculate total number of samples."""
        if not self.audio_data or not self.format_info:
            return 0
        
        bytes_per_sample = self.format_info.bits_per_sample // 8
        return len(self.audio_data) // (bytes_per_sample * self.format_info.channels)


# Standard wave library functions
def read_wav_file(filename):
    """Reads a WAV file and returns the audio data and file metadata."""
    with wave.open(filename, 'rb') as wav_file:
        num_channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        frame_rate = wav_file.getframerate()
        num_frames = wav_file.getnframes()
        duration = num_frames / frame_rate

        audio_data = np.frombuffer(wav_file.readframes(num_frames), dtype=np.int16)

        return audio_data, num_channels, sample_width, frame_rate, num_frames, duration


def get_wav_metadata(wav_filepath: str) -> dict:
    """Get metadata information from a WAV file."""
    with wave.open(wav_filepath, 'rb') as wav_file:
        return {
            "filepath": wav_filepath,
            "file_size": wav_file.getnframes() * wav_file.getnchannels() * wav_file.getsampwidth(),
            "num_channels": wav_file.getnchannels(),
            "sample_width": wav_file.getsampwidth(),
            "frame_rate": wav_file.getframerate(),
            "num_frames": wav_file.getnframes(),
            "duration": wav_file.getnframes() / wav_file.getframerate()
        }


def analyze_wav_file(wav_path, input_dir):
    """Analyze a WAV file and extract comprehensive information."""
    wav_path = Path(wav_path)
    file_info = {
        'filename': wav_path.name,
        'relative_path': str(wav_path.relative_to(input_dir)),
        'full_path': str(wav_path),
        'file_size_bytes': 0,
        'file_size_mb': 0.0,
        'sample_rate': 0,
        'num_channels': 0,
        'num_frames': 0,
        'sample_width_bytes': 0,
        'sample_width_bits': 0,
        'length_seconds': 0.0,
        'length_milliseconds': 0,
        'length_formatted': '00:00:00.000',
        'md5_hash': '',
        'compression_type': '',
        'compression_name': '',
        'status': 'Success',
        'error_message': ''
    }
    
    try:
        file_info['file_size_bytes'] = wav_path.stat().st_size
        file_info['file_size_mb'] = file_info['file_size_bytes'] / (1024 * 1024)
        
        with wave.open(str(wav_path), 'rb') as wav_file:
            file_info['num_channels'] = wav_file.getnchannels()
            file_info['sample_rate'] = wav_file.getframerate()
            file_info['num_frames'] = wav_file.getnframes()
            file_info['sample_width_bytes'] = wav_file.getsampwidth()
            file_info['sample_width_bits'] = file_info['sample_width_bytes'] * 8
            file_info['compression_type'] = wav_file.getcomptype()
            file_info['compression_name'] = wav_file.getcompname()
            
            if file_info['sample_rate'] > 0:
                file_info['length_seconds'] = file_info['num_frames'] / file_info['sample_rate']
                file_info['length_milliseconds'] = int(file_info['length_seconds'] * 1000)
                
                hours = int(file_info['length_seconds'] // 3600)
                minutes = int((file_info['length_seconds'] % 3600) // 60)
                seconds = file_info['length_seconds'] % 60
                file_info['length_formatted'] = f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"
        
        file_info['md5_hash'] = get_file_md5_hash(wav_path)
        
    except wave.Error as e:
        file_info['status'] = 'WAV Error'
        file_info['error_message'] = str(e)
    except Exception as e:
        file_info['status'] = 'Error'
        file_info['error_message'] = str(e)
    
    return file_info


def write_wav_file(filename, audio_data, num_channels, sample_width, frame_rate):
    """Writes audio data to a WAV file with specified parameters."""
    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(num_channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(frame_rate)
        wav_file.writeframes(audio_data.tobytes())


# Convenience functions
def parse_wav(file_path: Union[str, Path]) -> Dict:
    """Quick function to parse a WAV file and return information."""
    parser = WAVParser(file_path)
    return parser.parse()


def validate_wav(file_path: Union[str, Path]) -> bool:
    """Check if a file is a valid WAV file."""
    try:
        parse_wav(file_path)
        return True
    except (WAVError, FileNotFoundError, struct.error):
        return False