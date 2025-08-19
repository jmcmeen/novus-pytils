"""Unit tests for file_operations.audio module."""
import pytest
import wave
import struct
import numpy as np
from unittest.mock import patch

from novus_pytils.file_operations.audio import (
    count_audio_files, get_audio_files, get_wav_files, read_wav_file,
    get_wav_metadata, analyze_wav_file, write_wav_file, parse_wav,
    validate_wav, WAVParser, WAVError, InvalidWAVFormatError, CorruptedFileError
)


class TestAudioFileQueries:
    """Test audio file query functions."""
    
    @patch('novus_pytils.file_operations.audio.get_files_by_extension')
    def test_count_audio_files(self, mock_get_files):
        """Test counting audio files."""
        mock_get_files.return_value = ['file1.mp3', 'file2.wav', 'file3.ogg']
        
        count = count_audio_files('/test/path')
        assert count == 3
        mock_get_files.assert_called_once()
    
    @patch('novus_pytils.file_operations.audio.get_files_by_extension')
    def test_get_audio_files(self, mock_get_files):
        """Test getting audio files."""
        expected_files = ['file1.mp3', 'file2.wav']
        mock_get_files.return_value = expected_files
        
        files = get_audio_files('/test/path')
        assert files == expected_files
        mock_get_files.assert_called_once()
    
    @patch('novus_pytils.file_operations.audio.get_files_by_extension')
    def test_get_wav_files(self, mock_get_files):
        """Test getting WAV files specifically."""
        expected_files = ['file1.wav', 'file2.wav']
        mock_get_files.return_value = expected_files
        
        files = get_wav_files('/test/path')
        assert files == expected_files
        mock_get_files.assert_called_with('/test/path', ['.wav'])


class TestWAVFileOperations:
    """Test WAV file operations."""
    
    def test_read_wav_file(self, sample_wav_file):
        """Test reading WAV file."""
        audio_data, num_channels, sample_width, frame_rate, num_frames, duration = read_wav_file(str(sample_wav_file))
        
        assert isinstance(audio_data, np.ndarray)
        assert num_channels == 1
        assert sample_width == 2
        assert frame_rate == 44100
        assert num_frames > 0
        assert duration > 0
    
    def test_get_wav_metadata(self, sample_wav_file):
        """Test getting WAV metadata."""
        metadata = get_wav_metadata(str(sample_wav_file))
        
        assert 'filepath' in metadata
        assert 'file_size' in metadata
        assert 'num_channels' in metadata
        assert 'sample_width' in metadata
        assert 'frame_rate' in metadata
        assert 'num_frames' in metadata
        assert 'duration' in metadata
        
        assert metadata['filepath'] == str(sample_wav_file)
        assert metadata['num_channels'] == 1
        assert metadata['frame_rate'] == 44100
    
    def test_analyze_wav_file(self, sample_wav_file, temp_dir):
        """Test analyzing WAV file."""
        analysis = analyze_wav_file(sample_wav_file, temp_dir)
        
        assert analysis['status'] == 'Success'
        assert analysis['filename'] == sample_wav_file.name
        assert analysis['num_channels'] == 1
        assert analysis['sample_rate'] == 44100
        assert analysis['length_seconds'] > 0
        assert 'md5_hash' in analysis
    
    def test_write_wav_file(self, temp_dir):
        """Test writing WAV file."""
        output_path = temp_dir / "output.wav"
        
        # Create test audio data
        sample_rate = 22050
        duration = 0.5
        frequency = 440
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        audio_data = np.sin(frequency * 2 * np.pi * t) * 0.3
        audio_data = (audio_data * 32767).astype(np.int16)
        
        write_wav_file(str(output_path), audio_data, 1, 2, sample_rate)
        
        assert output_path.exists()
        
        # Verify written file
        with wave.open(str(output_path), 'rb') as wav_file:
            assert wav_file.getnchannels() == 1
            assert wav_file.getsampwidth() == 2
            assert wav_file.getframerate() == sample_rate


class TestWAVParser:
    """Test WAV parser functionality."""
    
    def test_parse_wav_success(self, sample_wav_file):
        """Test successful WAV parsing."""
        info = parse_wav(sample_wav_file)
        
        assert 'file_path' in info
        assert 'file_size' in info
        assert 'format' in info
        assert 'duration_seconds' in info
        
        format_info = info['format']
        assert format_info['channels'] == 1
        assert format_info['sample_rate'] == 44100
        assert format_info['is_pcm'] is True
    
    def test_validate_wav_success(self, sample_wav_file):
        """Test WAV validation with valid file."""
        assert validate_wav(sample_wav_file) is True
    
    def test_validate_wav_failure(self, temp_dir):
        """Test WAV validation with invalid file."""
        invalid_file = temp_dir / "invalid.wav"
        invalid_file.write_text("This is not a WAV file")
        
        assert validate_wav(invalid_file) is False
    
    def test_wav_parser_class(self, sample_wav_file):
        """Test WAVParser class directly."""
        parser = WAVParser(sample_wav_file)
        parser.parse()
        
        assert parser.format_info is not None
        assert parser.audio_data is not None
        assert len(parser.chunks) > 0
        
        # Test getting info
        detailed_info = parser.get_info()
        assert 'file_path' in detailed_info
        assert 'sample_count' in detailed_info
    
    def test_wav_parser_invalid_file(self, temp_dir):
        """Test WAVParser with invalid file."""
        invalid_file = temp_dir / "invalid.wav"
        invalid_file.write_bytes(b"RIFF\x00\x00\x00\x00INVALID")
        
        parser = WAVParser(invalid_file)
        with pytest.raises(InvalidWAVFormatError):
            parser.parse()
    
    def test_wav_parser_corrupted_file(self, temp_dir):
        """Test WAVParser with corrupted file."""
        corrupted_file = temp_dir / "corrupted.wav"
        corrupted_file.write_bytes(b"RIFF\x00\x00\x00\x00WAVE")  # Too short
        
        parser = WAVParser(corrupted_file)
        with pytest.raises((CorruptedFileError, InvalidWAVFormatError)):
            parser.parse()
    
    def test_wav_parser_nonexistent_file(self, temp_dir):
        """Test WAVParser with non-existent file."""
        nonexistent_file = temp_dir / "nonexistent.wav"
        
        parser = WAVParser(nonexistent_file)
        with pytest.raises(FileNotFoundError):
            parser.parse()


class TestWAVParserEdgeCases:
    """Test WAV parser edge cases."""
    
    def test_wav_parser_not_parsed_error(self, sample_wav_file):
        """Test error when getting info before parsing."""
        parser = WAVParser(sample_wav_file)
        
        with pytest.raises(WAVError):
            parser.get_info()
    
    def test_wav_format_properties(self, sample_wav_file):
        """Test WAV format properties."""
        parser = WAVParser(sample_wav_file)
        parser.parse()
        
        format_info = parser.format_info
        assert format_info.is_pcm is True
        assert format_info.duration_seconds > 0
    
    def create_custom_wav_file(self, temp_dir, channels=2, sample_rate=48000, bits_per_sample=24):
        """Helper to create custom WAV files for testing."""
        file_path = temp_dir / f"custom_{channels}ch_{sample_rate}hz_{bits_per_sample}bit.wav"
        
        # Create a simple WAV file structure
        duration = 0.1  # 100ms
        num_samples = int(sample_rate * duration)
        
        # Create RIFF header
        riff_header = b'RIFF'
        file_size = 36 + num_samples * channels * (bits_per_sample // 8)
        riff_header += struct.pack('<I', file_size)
        riff_header += b'WAVE'
        
        # Create fmt chunk
        fmt_chunk = b'fmt '
        fmt_chunk += struct.pack('<I', 16)  # Chunk size
        fmt_chunk += struct.pack('<H', 1)   # PCM format
        fmt_chunk += struct.pack('<H', channels)
        fmt_chunk += struct.pack('<I', sample_rate)
        byte_rate = sample_rate * channels * (bits_per_sample // 8)
        fmt_chunk += struct.pack('<I', byte_rate)
        block_align = channels * (bits_per_sample // 8)
        fmt_chunk += struct.pack('<H', block_align)
        fmt_chunk += struct.pack('<H', bits_per_sample)
        
        # Create data chunk
        data_chunk = b'data'
        data_size = num_samples * channels * (bits_per_sample // 8)
        data_chunk += struct.pack('<I', data_size)
        
        # Generate audio data (simple sine wave)
        audio_data = b''
        for i in range(num_samples):
            for ch in range(channels):
                # Simple sine wave
                value = int(32767 * 0.1 * np.sin(2 * np.pi * 440 * i / sample_rate))
                if bits_per_sample == 16:
                    audio_data += struct.pack('<h', value)
                elif bits_per_sample == 24:
                    # 24-bit is tricky, use 3 bytes
                    value_24 = value << 8  # Scale to 24-bit range
                    audio_data += struct.pack('<i', value_24)[:3]
                else:
                    audio_data += struct.pack('<h', value)  # Default to 16-bit
        
        # Write file
        with open(file_path, 'wb') as f:
            f.write(riff_header)
            f.write(fmt_chunk)
            f.write(data_chunk)
            f.write(audio_data)
        
        return file_path
    
    def test_parse_stereo_wav(self, temp_dir):
        """Test parsing stereo WAV file."""
        stereo_file = self.create_custom_wav_file(temp_dir, channels=2)
        
        parser = WAVParser(stereo_file)
        info = parser.parse()
        
        assert info['format']['channels'] == 2
        assert info['format']['is_pcm'] is True
    
    def test_parse_high_sample_rate_wav(self, temp_dir):
        """Test parsing high sample rate WAV file."""
        high_sr_file = self.create_custom_wav_file(temp_dir, sample_rate=96000)
        
        parser = WAVParser(high_sr_file)
        info = parser.parse()
        
        assert info['format']['sample_rate'] == 96000


class TestAudioFileAnalysisErrors:
    """Test error handling in audio file analysis."""
    
    def test_analyze_wav_file_error(self, temp_dir):
        """Test error handling in WAV file analysis."""
        invalid_file = temp_dir / "invalid.wav"
        invalid_file.write_text("Not a WAV file")
        
        analysis = analyze_wav_file(invalid_file, temp_dir)
        assert analysis['status'] != 'Success'
        assert 'error_message' in analysis
        assert analysis['error_message'] != ''
    
    @patch('novus_pytils.file_operations.audio.get_file_md5_hash')
    def test_analyze_wav_file_hash_error(self, mock_hash, sample_wav_file, temp_dir):
        """Test error handling when hash calculation fails."""
        mock_hash.side_effect = Exception("Hash calculation failed")
        
        analysis = analyze_wav_file(sample_wav_file, temp_dir)
        # Should still work but without hash
        assert 'md5_hash' in analysis


@pytest.mark.slow
class TestAudioFilePerformance:
    """Performance tests for audio file operations."""
    
    def test_parse_large_wav_file(self, temp_dir):
        """Test parsing larger WAV files for performance."""
        # Create a larger WAV file (1 second at 44.1kHz)
        large_file = temp_dir / "large.wav"
        
        sample_rate = 44100
        duration = 1.0
        frequency = 440
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        audio_data = np.sin(frequency * 2 * np.pi * t) * 0.3
        audio_data = (audio_data * 32767).astype(np.int16)
        
        with wave.open(str(large_file), 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data.tobytes())
        
        # Test parsing performance
        import time
        start_time = time.time()
        
        parser = WAVParser(large_file)
        info = parser.parse()
        
        end_time = time.time()
        parse_time = end_time - start_time
        
        # Should parse reasonably quickly (less than 1 second for 1-second file)
        assert parse_time < 1.0
        assert info['duration_seconds'] > 0.9  # Should be close to 1 second