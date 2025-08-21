"""Audio file handler with format conversion capabilities.

This module provides comprehensive audio file handling including reading, writing,
and conversion between various audio formats using minimal dependencies.
"""
import os
import wave
from typing import Any, Dict, List, Union
from novus_pytils.models.models import BaseFileHandler, FileManagerMixin
from novus_pytils.exceptions import ConversionError
from novus_pytils.globals import SUPPORTED_AUDIO_EXTENSIONS, AUDIO_CONVERSION_MAP


class AudioWrapper:
    """Wrapper class to isolate audio library dependencies."""
    
    def __init__(self):
        self._pydub_available = False
        self._AudioSegment = None
        
        try:
            from pydub import AudioSegment
            self._AudioSegment = AudioSegment
            self._pydub_available = True
        except ImportError:
            pass
    
    @property
    def available(self) -> bool:
        return self._pydub_available
    
    def from_file(self, file_path: str, format: str = None):
        if not self._pydub_available:
            raise ConversionError("pydub is required for audio operations. Install with: pip install pydub")
        return self._AudioSegment.from_file(file_path, format=format)
    
    def from_wav(self, file_path: str):
        if not self._pydub_available:
            raise ConversionError("pydub is required for audio operations. Install with: pip install pydub")
        return self._AudioSegment.from_wav(file_path)
    
    def from_mp3(self, file_path: str):
        if not self._pydub_available:
            raise ConversionError("pydub is required for audio operations. Install with: pip install pydub")
        return self._AudioSegment.from_mp3(file_path)
    
    def silent(self, duration: int, frame_rate: int = 44100):
        if not self._pydub_available:
            raise ConversionError("pydub is required for audio operations. Install with: pip install pydub")
        return self._AudioSegment.silent(duration=duration, frame_rate=frame_rate)
    
    def empty(self):
        if not self._pydub_available:
            raise ConversionError("pydub is required for audio operations. Install with: pip install pydub")
        return self._AudioSegment.empty()


class AudioHandler(BaseFileHandler, FileManagerMixin):
    """Handler for audio files with conversion capabilities."""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = SUPPORTED_AUDIO_EXTENSIONS
        self.conversion_map = AUDIO_CONVERSION_MAP
        self.audio_wrapper = AudioWrapper()
    
    def read(self, file_path: str) -> Union[Any, Dict[str, Any]]:
        """Read audio file and return AudioSegment or wave data."""
        if not self.validate_file(file_path):
            raise ConversionError(f"Unsupported file format: {file_path}")
        
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.wav' and not self.audio_wrapper.available:
            return self._read_wav_native(file_path)
        elif self.audio_wrapper.available:
            return self.audio_wrapper.from_file(file_path)
        else:
            raise ConversionError("pydub is required for non-WAV audio files. Install with: pip install pydub")
    
    def write(self, file_path: str, content: Any, format: str = None, **kwargs) -> bool:
        """Write audio content to file."""
        try:
            os.makedirs(os.path.dirname(file_path) or '.', exist_ok=True)
            
            ext = os.path.splitext(file_path)[1].lower()
            output_format = format or ext[1:] if ext else 'wav'
            
            if isinstance(content, dict) and 'frames' in content:
                return self._write_wav_native(file_path, content)
            elif self.audio_wrapper.available:
                bitrate = kwargs.get('bitrate', '192k')
                parameters = []
                
                if output_format in ['mp3', 'mp4', 'aac']:
                    parameters.extend(['-b:a', bitrate])
                
                content.export(file_path, format=output_format, bitrate=bitrate, parameters=parameters)
                return True
            else:
                raise ConversionError("Cannot write audio without proper audio data or pydub")
        
        except Exception as e:
            raise ConversionError(f"Failed to write audio {file_path}: {str(e)}")
    
    def convert(self, input_path: str, output_path: str, target_format: str, **kwargs) -> bool:
        """Convert audio from one format to another."""
        if not self.validate_file(input_path):
            raise ConversionError(f"Unsupported input file format: {input_path}")
        
        input_ext = os.path.splitext(input_path)[1].lower()
        target_ext = target_format if target_format.startswith('.') else f'.{target_format}'
        
        if target_ext not in self.get_supported_conversions(input_ext):
            raise ConversionError(f"Cannot convert from {input_ext} to {target_ext}")
        
        try:
            audio_data = self.read(input_path)
            target_fmt = target_ext[1:] if target_ext.startswith('.') else target_ext
            
            return self.write(output_path, audio_data, format=target_fmt, **kwargs)
        
        except Exception as e:
            raise ConversionError(f"Conversion failed from {input_path} to {output_path}: {str(e)}")
    
    def trim(self, input_path: str, output_path: str, start_ms: int, end_ms: int, **kwargs) -> bool:
        """Trim audio file to specified time range."""
        if not self.audio_wrapper.available:
            raise ConversionError("pydub is required for audio trimming")
        
        try:
            audio = self.audio_wrapper.from_file(input_path)
            trimmed = audio[start_ms:end_ms]
            return self.write(output_path, trimmed, **kwargs)
        
        except Exception as e:
            raise ConversionError(f"Failed to trim audio: {str(e)}")
    
    def concatenate(self, input_paths: List[str], output_path: str, **kwargs) -> bool:
        """Concatenate multiple audio files."""
        if not self.audio_wrapper.available:
            raise ConversionError("pydub is required for audio concatenation")
        
        if len(input_paths) < 2:
            raise ConversionError("At least 2 audio files required for concatenation")
        
        try:
            combined = self.audio_wrapper.empty()
            
            for path in input_paths:
                audio = self.audio_wrapper.from_file(path)
                combined += audio
            
            return self.write(output_path, combined, **kwargs)
        
        except Exception as e:
            raise ConversionError(f"Failed to concatenate audio: {str(e)}")
    
    def change_volume(self, input_path: str, output_path: str, volume_change_db: float, **kwargs) -> bool:
        """Change volume of audio file by specified decibels."""
        if not self.audio_wrapper.available:
            raise ConversionError("pydub is required for volume adjustment")
        
        try:
            audio = self.audio_wrapper.from_file(input_path)
            adjusted = audio + volume_change_db
            return self.write(output_path, adjusted, **kwargs)
        
        except Exception as e:
            raise ConversionError(f"Failed to adjust volume: {str(e)}")
    
    def fade_in_out(self, input_path: str, output_path: str, 
                    fade_in_ms: int = 0, fade_out_ms: int = 0, **kwargs) -> bool:
        """Apply fade in and/or fade out effects."""
        if not self.audio_wrapper.available:
            raise ConversionError("pydub is required for fade effects")
        
        try:
            audio = self.audio_wrapper.from_file(input_path)
            
            if fade_in_ms > 0:
                audio = audio.fade_in(fade_in_ms)
            
            if fade_out_ms > 0:
                audio = audio.fade_out(fade_out_ms)
            
            return self.write(output_path, audio, **kwargs)
        
        except Exception as e:
            raise ConversionError(f"Failed to apply fade effects: {str(e)}")
    
    def get_audio_info(self, file_path: str) -> Dict[str, Any]:
        """Get audio metadata and information."""
        base_info = self.get_metadata(file_path)
        
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.wav':
            try:
                wav_info = self._get_wav_info(file_path)
                base_info.update(wav_info)
            except Exception:
                pass
        
        if self.audio_wrapper.available:
            try:
                audio = self.audio_wrapper.from_file(file_path)
                base_info.update({
                    'duration_ms': len(audio),
                    'duration_seconds': len(audio) / 1000,
                    'frame_rate': audio.frame_rate,
                    'channels': audio.channels,
                    'sample_width': audio.sample_width,
                    'frame_count': audio.frame_count(),
                    'max_possible_amplitude': audio.max_possible_amplitude,
                    'dBFS': audio.dBFS
                })
            except Exception:
                pass
        
        return base_info
    
    def _read_wav_native(self, file_path: str) -> Dict[str, Any]:
        """Read WAV file using native wave library."""
        try:
            with wave.open(file_path, 'rb') as wav_file:
                frames = wav_file.readframes(-1)
                return {
                    'frames': frames,
                    'sample_rate': wav_file.getframerate(),
                    'channels': wav_file.getnchannels(),
                    'sample_width': wav_file.getsampwidth(),
                    'frame_count': wav_file.getnframes(),
                    'duration': wav_file.getnframes() / wav_file.getframerate()
                }
        except Exception as e:
            raise ConversionError(f"Failed to read WAV file: {str(e)}")
    
    def _write_wav_native(self, file_path: str, content: Dict[str, Any]) -> bool:
        """Write WAV file using native wave library."""
        try:
            with wave.open(file_path, 'wb') as wav_file:
                wav_file.setnchannels(content['channels'])
                wav_file.setsampwidth(content['sample_width'])
                wav_file.setframerate(content['sample_rate'])
                wav_file.writeframes(content['frames'])
            return True
        except Exception as e:
            raise ConversionError(f"Failed to write WAV file: {str(e)}")
    
    def _get_wav_info(self, file_path: str) -> Dict[str, Any]:
        """Get WAV file information using native wave library."""
        try:
            with wave.open(file_path, 'rb') as wav_file:
                return {
                    'duration_seconds': wav_file.getnframes() / wav_file.getframerate(),
                    'frame_rate': wav_file.getframerate(),
                    'channels': wav_file.getnchannels(),
                    'sample_width': wav_file.getsampwidth(),
                    'frame_count': wav_file.getnframes()
                }
        except Exception:
            return {}
    
    def normalize(self, input_path: str, output_path: str, target_dBFS: float = -20.0, **kwargs) -> bool:
        """Normalize audio to target dBFS level."""
        if not self.audio_wrapper.available:
            raise ConversionError("pydub is required for audio normalization")
        
        try:
            audio = self.audio_wrapper.from_file(input_path)
            change_in_dBFS = target_dBFS - audio.dBFS
            normalized = audio.apply_gain(change_in_dBFS)
            return self.write(output_path, normalized, **kwargs)
        
        except Exception as e:
            raise ConversionError(f"Failed to normalize audio: {str(e)}")
    
    def split_on_silence(self, input_path: str, output_dir: str, 
                        min_silence_len: int = 1000, silence_thresh: int = -40, **kwargs) -> List[str]:
        """Split audio file on silence into multiple files."""
        if not self.audio_wrapper.available:
            raise ConversionError("pydub is required for silence detection")
        
        try:
            from pydub.silence import split_on_silence
            
            audio = self.audio_wrapper.from_file(input_path)
            chunks = split_on_silence(audio, 
                                    min_silence_len=min_silence_len, 
                                    silence_thresh=silence_thresh)
            
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            ext = os.path.splitext(input_path)[1]
            output_files = []
            
            for i, chunk in enumerate(chunks):
                output_file = os.path.join(output_dir, f"{base_name}_chunk_{i+1}{ext}")
                self.write(output_file, chunk, **kwargs)
                output_files.append(output_file)
            
            return output_files
        
        except Exception as e:
            raise ConversionError(f"Failed to split audio on silence: {str(e)}")
    
    def mix_audio(self, audio_paths: List[str], output_path: str, volumes: List[float] = None, **kwargs) -> bool:
        """Mix multiple audio files together."""
        if not self.audio_wrapper.available:
            raise ConversionError("pydub is required for audio mixing")
        
        if len(audio_paths) < 2:
            raise ConversionError("At least 2 audio files required for mixing")
        
        try:
            audio_segments = [self.audio_wrapper.from_file(path) for path in audio_paths]
            
            if volumes and len(volumes) == len(audio_segments):
                for i, volume in enumerate(volumes):
                    audio_segments[i] = audio_segments[i] + volume
            
            max_length = max(len(segment) for segment in audio_segments)
            
            mixed = self.audio_wrapper.silent(max_length, frame_rate=audio_segments[0].frame_rate)
            
            for segment in audio_segments:
                mixed = mixed.overlay(segment)
            
            return self.write(output_path, mixed, **kwargs)
        
        except Exception as e:
            raise ConversionError(f"Failed to mix audio: {str(e)}")