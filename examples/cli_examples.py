"""Examples for using the command-line interface.

This file demonstrates various CLI commands and usage patterns.
"""


def basic_cli_examples():
    """Basic CLI command examples."""
    print("\\n=== Basic CLI Examples ===")
    
    examples = [
        # File info
        "novus-pytils info document.txt",
        "novus-pytils info --json photo.jpg",
        
        # File conversion
        "novus-pytils convert input.txt output.json json",
        "novus-pytils convert photo.png photo.jpg jpg --quality 90",
        "novus-pytils convert audio.wav audio.mp3 mp3 --bitrate 320k",
        "novus-pytils convert video.avi video.mp4 mp4 --resolution 1920x1080",
        
        # Image operations
        "novus-pytils resize input.jpg output.jpg 800 600",
        "novus-pytils resize input.jpg output.jpg 800 600 --no-maintain-aspect",
        "novus-pytils crop input.jpg cropped.jpg 100 100 500 400",
        
        # Audio/Video operations
        "novus-pytils trim audio.wav trimmed.wav 1000 --end 5000",  # milliseconds
        "novus-pytils trim video.mp4 trimmed.mp4 00:00:10 --duration 00:00:30",
        
        # Thumbnails
        "novus-pytils thumbnail photo.jpg thumb.jpg --size 256",
        "novus-pytils thumbnail video.mp4 thumb.jpg --time-position 00:01:00",
    ]
    
    print("Basic CLI commands:")
    for example in examples:
        print(f"  {example}")


def batch_operations_examples():
    """Batch operations examples."""
    print("\\n=== Batch Operations Examples ===")
    
    examples = [
        # Batch conversion
        "novus-pytils batch convert file1.txt file2.txt file3.txt --target-format json",
        "novus-pytils batch convert *.txt --target-format json --output-dir converted/",
        
        # Batch copy/move
        "novus-pytils batch copy file1.txt file2.txt --dest-dir backup/",
        "novus-pytils batch move *.log --dest-dir archive/",
        
        # Batch delete
        "novus-pytils batch delete temp*.txt --verbose",
    ]
    
    print("Batch operation commands:")
    for example in examples:
        print(f"  {example}")


def advanced_operations_examples():
    """Advanced operation examples."""
    print("\\n=== Advanced Operations Examples ===")
    
    examples = [
        # File merging
        "novus-pytils merge part1.txt part2.txt part3.txt merged.txt",
        "novus-pytils merge doc1.txt doc2.txt combined.txt --separator '\\n---\\n'",
        
        # File splitting
        "novus-pytils split large_file.txt output_dir/ --lines-per-file 1000",
        "novus-pytils split audio.wav output_dir/ --min-silence-len 1000 --silence-thresh -40",
        
        # Filters
        "novus-pytils filter input.jpg blurred.jpg blur",
        "novus-pytils filter input.jpg bright.jpg brightness --value 0.2",
        "novus-pytils filter video.mp4 gray.mp4 grayscale",
        
        # Media extraction
        "novus-pytils extract-audio video.mp4 audio.mp3",
        "novus-pytils extract-frames video.mp4 frames_dir/ --fps 1.0",
        
        # Supported formats
        "novus-pytils supported document.txt",
    ]
    
    print("Advanced operation commands:")
    for example in examples:
        print(f"  {example}")


def web_server_examples():
    """Web server examples."""
    print("\\n=== Web Server Examples ===")
    
    examples = [
        # Basic server
        "novus-pytils server",
        
        # Custom host/port
        "novus-pytils server --host 0.0.0.0 --port 8080",
        
        # Custom upload directory
        "novus-pytils server --upload-dir /path/to/uploads",
        
        # All options
        "novus-pytils server --host 127.0.0.1 --port 9000 --upload-dir ./uploads",
    ]
    
    print("Web server commands:")
    for example in examples:
        print(f"  {example}")
    
    print("\\nOnce running, the API will be available at:")
    print("  http://localhost:8000 (default)")
    print("  Interactive docs: http://localhost:8000/docs")


def scripting_examples():
    """Examples for scripting and automation."""
    print("\\n=== Scripting Examples ===")
    
    bash_script = '''#!/bin/bash
# Convert all images in a directory to JPEG
for img in *.png *.gif *.bmp; do
    if [ -f "$img" ]; then
        novus-pytils convert "$img" "${img%.*}.jpg" jpg --quality 85
    fi
done

# Create thumbnails for all videos
for video in *.mp4 *.avi *.mkv; do
    if [ -f "$video" ]; then
        novus-pytils thumbnail "$video" "thumb_${video%.*}.jpg" --size 200
    fi
done

# Batch process audio files
novus-pytils batch convert *.wav --target-format mp3 --output-dir converted/
'''
    
    powershell_script = '''# PowerShell script for batch processing
# Convert all text files to JSON
Get-ChildItem *.txt | ForEach-Object {
    novus-pytils convert $_.Name "$($_.BaseName).json" json
}

# Resize all images to web-friendly size
Get-ChildItem *.jpg | ForEach-Object {
    novus-pytils resize $_.Name "web_$($_.Name)" 1200 800 --quality 80
}
'''
    
    print("Bash script example:")
    print(bash_script)
    
    print("PowerShell script example:")
    print(powershell_script)


def help_and_documentation():
    """Help and documentation commands."""
    print("\\n=== Help and Documentation ===")
    
    help_commands = [
        "novus-pytils --help",           # Main help
        "novus-pytils convert --help",   # Command-specific help
        "novus-pytils batch --help",     # Batch operations help
        "novus-pytils server --help",    # Server help
        "novus-pytils --version",        # Version info
    ]
    
    print("Getting help:")
    for cmd in help_commands:
        print(f"  {cmd}")


def main():
    """Run all examples."""
    print("Novus PyTils CLI Examples")
    print("=========================")
    
    basic_cli_examples()
    batch_operations_examples()
    advanced_operations_examples()
    web_server_examples()
    scripting_examples()
    help_and_documentation()
    
    print("\\n=== CLI Examples completed ===")
    print("\\nInstall the package to use CLI commands:")
    print("  pip install -e .")
    print("  novus-pytils --help")


if __name__ == "__main__":
    main()