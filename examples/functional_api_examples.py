"""Examples using the functional API.

This file demonstrates how to use the functional API for various file operations.
"""
import os
import tempfile
from novus_pytils import (
    create_file, read_file, write_file, convert_file, resize_image, 
    crop_image, trim_audio, merge_files, batch_convert, get_file_info
)


def text_operations_example():
    """Example of text file operations."""
    print("\\n=== Text Operations Example ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create text files
        txt_file = os.path.join(temp_dir, "sample.txt")
        json_file = os.path.join(temp_dir, "data.json")
        csv_file = os.path.join(temp_dir, "data.csv")
        
        # Create and write text file
        create_file(txt_file, "Hello, World!\\nThis is a sample text file.")
        print(f"Created: {txt_file}")
        
        # Create JSON data
        json_data = {"name": "John", "age": 30, "city": "New York"}
        create_file(json_file, json_data)
        print(f"Created: {json_file}")
        
        # Create CSV data
        csv_data = [
            {"name": "Alice", "age": 25},
            {"name": "Bob", "age": 30}
        ]
        create_file(csv_file, csv_data)
        print(f"Created: {csv_file}")
        
        # Read files
        txt_content = read_file(txt_file)
        json_content = read_file(json_file)
        csv_content = read_file(csv_file)
        
        print(f"\\nText content: {txt_content[:50]}...")
        print(f"JSON content: {json_content}")
        print(f"CSV content: {len(csv_content)} rows")
        
        # Convert JSON to YAML
        yaml_file = os.path.join(temp_dir, "data.yaml")
        convert_file(json_file, yaml_file, "yaml")
        print(f"\\nConverted JSON to YAML: {yaml_file}")
        
        # Get file info
        info = get_file_info(json_file)
        print(f"JSON file size: {info['size']} bytes")


def image_operations_example():
    """Example of image operations (requires PIL)."""
    print("\\n=== Image Operations Example ===")
    
    # Note: This example would work with actual image files
    # For demonstration, we'll show the function calls
    
    print("Example image operations (requires actual image files):")
    print("resize_image('input.jpg', 'output.jpg', (800, 600))")
    print("crop_image('input.jpg', 'cropped.jpg', (100, 100, 400, 400))")
    print("convert_file('input.png', 'output.jpg', 'jpg')")


def audio_operations_example():
    """Example of audio operations (requires pydub)."""
    print("\\n=== Audio Operations Example ===")
    
    # Note: This example would work with actual audio files
    print("Example audio operations (requires actual audio files):")
    print("trim_audio('input.wav', 'output.wav', 1000, 5000)  # 1-5 seconds")
    print("convert_file('input.wav', 'output.mp3', 'mp3')")


def batch_operations_example():
    """Example of batch operations."""
    print("\\n=== Batch Operations Example ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create multiple text files
        files = []
        for i in range(3):
            file_path = os.path.join(temp_dir, f"file_{i}.txt")
            create_file(file_path, f"Content of file {i}")
            files.append(file_path)
        
        print(f"Created {len(files)} files")
        
        # Batch convert to JSON (text files will be wrapped in JSON structure)
        results = batch_convert(files, "json", temp_dir)
        
        success_count = sum(1 for success in results.values() if success)
        print(f"\\nBatch conversion results: {success_count}/{len(files)} successful")
        
        for file_path, success in results.items():
            status = "✓" if success else "✗"
            print(f"  {status} {os.path.basename(file_path)}")


def merge_files_example():
    """Example of merging files."""
    print("\\n=== Merge Files Example ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create multiple text files
        files = []
        for i in range(3):
            file_path = os.path.join(temp_dir, f"part_{i}.txt")
            create_file(file_path, f"This is part {i+1} of the document.")
            files.append(file_path)
        
        # Merge files
        merged_file = os.path.join(temp_dir, "merged.txt")
        merge_files(files, merged_file, separator="\\n\\n---\\n\\n")
        
        # Read merged content
        merged_content = read_file(merged_file)
        print(f"Merged file content:\\n{merged_content}")


def main():
    """Run all examples."""
    print("Novus PyTils Functional API Examples")
    print("====================================")
    
    text_operations_example()
    image_operations_example() 
    audio_operations_example()
    batch_operations_example()
    merge_files_example()
    
    print("\\n=== Examples completed ===")


if __name__ == "__main__":
    main()