# Novus PyTils

A comprehensive file management library with CRUD operations, format conversion, and multi-API support for text, image, audio, and video files.

## Features

- **Multi-format support**: Text, images, audio, and video files
- **Format conversion**: Convert between compatible file formats
- **Multiple APIs**: Functional, object-oriented, web API, and CLI
- **Batch operations**: Process multiple files efficiently
- **Media processing**: Resize images, trim audio/video, apply filters
- **Web interface**: RESTful API with FastAPI
- **Command-line tools**: Full CLI for all operations
- **Security**: Input validation and path traversal protection

## Supported File Types

### Text Files
- `.txt`, `.md`, `.csv`, `.json`, `.xml`, `.yaml`, `.yml`, `.log`, `.ini`, `.cfg`
- Convert between formats (JSON ↔ YAML ↔ CSV ↔ XML)
- Merge and split operations
- Encoding conversion

### Images  
- `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`, `.webp`, `.svg`
- Resize, crop, rotate operations
- Apply filters (blur, brightness, contrast, etc.)
- Format conversion
- Thumbnail generation
- *Requires: `pip install Pillow`*

### Audio
- `.wav`, `.mp3`, `.ogg`, `.flac`, `.aac`, `.wma`, `.m4a`  
- Trim, concatenate, normalize
- Volume adjustment, fade effects
- Format conversion
- Split on silence detection
- *Requires: `pip install pydub`*

### Video
- `.mp4`, `.avi`, `.mkv`, `.mov`, `.wmv`, `.flv`, `.webm`
- Trim, concatenate, resize
- Extract audio or frames
- Apply filters and watermarks
- Thumbnail generation
- *Requires: FFmpeg installed*

## Installation

```bash
pip install novus-pytils

# With optional dependencies
pip install novus-pytils[all]  # All optional dependencies
pip install novus-pytils[web]  # Web API support
pip install novus-pytils[image]  # Image processing
```

## Quick Start

### Functional API

```python
from novus_pytils import read_file, write_file, convert_file, resize_image

# Read and write files
content = read_file("document.txt")
write_file("output.json", {"content": content})

# Convert formats
convert_file("data.json", "data.yaml", "yaml")

# Process images
resize_image("photo.jpg", "thumbnail.jpg", (200, 200))
```

### Object-Oriented API

```python
from novus_pytils import FileManager

manager = FileManager()

# Chainable operations
file = (manager.get_file("document.txt")
       .read()
       .convert_to("document.json", "json")
       .resize_to("small.json", (100, 100)))  # For images

# Context manager for editing
with manager.get_file("config.json").editing() as f:
    config = f.content
    config["debug"] = False
    f._cached_content = config

# Batch operations
batch = manager.get_batch(["file1.txt", "file2.txt", "file3.txt"])
results = batch.convert_all("json", output_dir="converted/")
```

### Web API

Start the server:
```bash
novus-pytils server --host 0.0.0.0 --port 8000
```

Or programmatically:
```python
from novus_pytils.api.web_api import run_server
run_server(host="0.0.0.0", port=8000)
```

Use the API:
```python
import requests

# Upload file
files = {'file': open('document.txt', 'rb')}
response = requests.post('http://localhost:8000/upload', files=files)

# Convert file
data = {'target_format': 'json', 'quality': 90}
response = requests.post('http://localhost:8000/convert/document.txt', json=data)

# Get file info
response = requests.get('http://localhost:8000/info/document.txt')
```

### Command Line Interface

```bash
# File operations
novus-pytils info document.txt
novus-pytils convert input.txt output.json json
novus-pytils convert photo.png photo.jpg jpg --quality 90

# Image operations  
novus-pytils resize input.jpg output.jpg 800 600
novus-pytils crop input.jpg cropped.jpg 100 100 500 400
novus-pytils thumbnail video.mp4 thumb.jpg --time-position 00:01:00

# Audio/Video operations
novus-pytils trim audio.wav output.wav 1000 --end 5000
novus-pytils extract-audio video.mp4 audio.mp3

# Batch operations
novus-pytils batch convert *.txt --target-format json --output-dir converted/
novus-pytils batch copy *.jpg --dest-dir backup/

# Start web server
novus-pytils server --port 8080 --upload-dir uploads/
```

## Examples

### Text File Processing

```python
from novus_pytils import create_file, read_file, convert_file

# Create structured data
data = [
    {"name": "Alice", "age": 30, "city": "New York"},
    {"name": "Bob", "age": 25, "city": "San Francisco"}
]

create_file("users.json", data)
convert_file("users.json", "users.csv", "csv")
convert_file("users.json", "users.yaml", "yaml")

# Read in different formats
json_data = read_file("users.json")  # Returns list of dicts
csv_data = read_file("users.csv")    # Returns list of dicts  
yaml_data = read_file("users.yaml")  # Returns list of dicts
```

### Image Processing

```python
from novus_pytils import FileManager

manager = FileManager()
image = manager.get_file("photo.jpg")

# Chain multiple operations
processed = (image
    .resize_to("resized.jpg", (1920, 1080))
    .crop_to("cropped.jpg", (100, 100, 800, 600))  
    .apply_filter_to("filtered.jpg", "blur")
    .create_thumbnail("thumb.jpg", size=200))
```

### Batch Processing

```python
from novus_pytils import batch_convert, batch_operation

# Convert all text files to JSON
text_files = ["doc1.txt", "doc2.txt", "doc3.txt"]
results = batch_convert(text_files, "json", output_dir="json_output/")

# Copy files to backup directory
image_files = ["img1.jpg", "img2.png", "img3.gif"]  
results = batch_operation(image_files, "copy", dest_dir="backup/")
```

## API Reference

### Core Functions

- `read_file(path)` - Read file contents
- `write_file(path, content)` - Write content to file  
- `convert_file(input_path, output_path, format)` - Convert file format
- `get_file_info(path)` - Get file metadata
- `batch_convert(files, format, output_dir)` - Batch convert files
- `batch_operation(files, operation, **kwargs)` - Batch file operations

### Image Functions

- `resize_image(input, output, size, maintain_aspect=True)` - Resize image
- `crop_image(input, output, box)` - Crop image  
- `create_thumbnail(input, output, size=(128,128))` - Create thumbnail
- `apply_filter(input, output, filter_name)` - Apply image filter

### Audio Functions  

- `trim_audio(input, output, start_ms, end_ms)` - Trim audio
- `normalize_audio(input, output, target_dBFS=-20.0)` - Normalize audio
- `change_audio_volume(input, output, volume_change_db)` - Adjust volume

### Video Functions

- `trim_video(input, output, start_time, duration)` - Trim video
- `extract_audio_from_video(input, output)` - Extract audio track
- `extract_frames_from_video(input, output_dir, fps=1.0)` - Extract frames

## Dependencies

### Core Dependencies
- `numpy` - Numerical operations
- `pandas` - Data manipulation  
- `pydub` - Audio processing
- `requests` - HTTP requests
- `pyyaml` - YAML processing

### Optional Dependencies
- `fastapi` - Web API framework
- `uvicorn` - ASGI server
- `python-multipart` - File upload support  
- `Pillow` - Image processing

### External Dependencies
- `FFmpeg` - Required for video processing (must be installed separately)

## Development

```bash
# Clone repository
git clone https://github.com/jmcmeen/novus-pytils.git
cd novus-pytils

# Install in development mode
pip install -e .
pip install -e .[all]  # With optional dependencies

# Run examples
python examples/functional_api_examples.py
python examples/object_oriented_examples.py

# Run CLI
novus-pytils --help
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions welcome! Please see CONTRIBUTING.md for guidelines.

## Changelog

### v1.0.0
- Initial release
- Full CRUD operations for text, image, audio, video
- Format conversion capabilities
- Functional and object-oriented APIs
- Web API with FastAPI
- Command-line interface
- Comprehensive validation and error handling