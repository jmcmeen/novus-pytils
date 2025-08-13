"""Pytest configuration and shared fixtures."""
import os
import tempfile
import shutil
import pytest
from pathlib import Path
import wave
import struct
import numpy as np
from PIL import Image


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_text_file(temp_dir):
    """Create a sample text file for testing."""
    file_path = temp_dir / "sample.txt"
    file_path.write_text("This is a sample text file for testing.\nSecond line.")
    return file_path


@pytest.fixture
def sample_csv_data():
    """Sample CSV data for testing."""
    return [
        ["name", "age", "city"],
        ["Alice", "25", "New York"],
        ["Bob", "30", "San Francisco"],
        ["Charlie", "35", "Chicago"]
    ]


@pytest.fixture
def sample_csv_file(temp_dir, sample_csv_data):
    """Create a sample CSV file for testing."""
    import csv
    file_path = temp_dir / "sample.csv"
    with open(file_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(sample_csv_data)
    return file_path


@pytest.fixture
def sample_wav_file(temp_dir):
    """Create a sample WAV file for testing."""
    file_path = temp_dir / "sample.wav"
    
    # Generate simple sine wave
    sample_rate = 44100
    duration = 1.0  # seconds
    frequency = 440  # Hz (A4)
    
    # Create audio data
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    audio_data = np.sin(frequency * 2 * np.pi * t) * 0.3
    audio_data = (audio_data * 32767).astype(np.int16)
    
    # Write WAV file
    with wave.open(str(file_path), 'wb') as wav_file:
        wav_file.setnchannels(1)  # mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())
    
    return file_path


@pytest.fixture
def sample_image_file(temp_dir):
    """Create a sample image file for testing."""
    file_path = temp_dir / "sample.png"
    
    # Create a simple RGB image
    image = Image.new('RGB', (100, 100), color='red')
    image.save(file_path)
    
    return file_path


@pytest.fixture
def sample_yaml_file(temp_dir):
    """Create a sample YAML file for testing."""
    file_path = temp_dir / "sample.yaml"
    yaml_content = """
database:
  host: localhost
  port: 5432
  name: test_db

settings:
  debug: true
  max_connections: 100
"""
    file_path.write_text(yaml_content)
    return file_path


@pytest.fixture
def sample_json_file(temp_dir):
    """Create a sample JSON file for testing."""
    import json
    file_path = temp_dir / "sample.json"
    data = {
        "name": "Test Data",
        "version": "1.0",
        "items": [1, 2, 3, 4, 5]
    }
    with open(file_path, 'w') as f:
        json.dump(data, f)
    return file_path


@pytest.fixture
def multiple_test_files(temp_dir):
    """Create multiple test files of different types."""
    files = {}
    
    # Text files
    for i in range(3):
        file_path = temp_dir / f"text_{i}.txt"
        file_path.write_text(f"Content of text file {i}")
        files[f"text_{i}"] = file_path
    
    # Image files (mock)
    for i in range(2):
        file_path = temp_dir / f"image_{i}.png"
        image = Image.new('RGB', (50, 50), color=['red', 'blue'][i])
        image.save(file_path)
        files[f"image_{i}"] = file_path
    
    return files


@pytest.fixture
def mock_file_structure(temp_dir):
    """Create a mock directory structure with various file types."""
    # Create subdirectories
    (temp_dir / "subdir1").mkdir()
    (temp_dir / "subdir2").mkdir()
    (temp_dir / "subdir1" / "nested").mkdir()
    
    # Create files in root
    (temp_dir / "root_file.txt").write_text("Root file content")
    (temp_dir / "config.yaml").write_text("key: value")
    
    # Create files in subdirectories
    (temp_dir / "subdir1" / "file1.txt").write_text("File 1 content")
    (temp_dir / "subdir1" / "file2.csv").write_text("col1,col2\nval1,val2")
    (temp_dir / "subdir1" / "nested" / "deep_file.txt").write_text("Deep file")
    (temp_dir / "subdir2" / "another.txt").write_text("Another file")
    
    return temp_dir


@pytest.fixture(autouse=True)
def clean_environment():
    """Clean environment variables before each test."""
    # Store original values
    original_env = {}
    env_vars_to_clean = ['NOVUS_PYTILS_CONFIG', 'NOVUS_PYTILS_DEBUG']
    
    for var in env_vars_to_clean:
        if var in os.environ:
            original_env[var] = os.environ[var]
            del os.environ[var]
    
    yield
    
    # Restore original values
    for var, value in original_env.items():
        os.environ[var] = value