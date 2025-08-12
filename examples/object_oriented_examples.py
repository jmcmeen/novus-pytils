"""Examples using the object-oriented API.

This file demonstrates how to use the object-oriented API for various file operations.
"""
import os
import tempfile
from novus_pytils import FileManager, File


def basic_file_operations():
    """Basic file operations using File objects."""
    print("\\n=== Basic File Operations ===")
    
    manager = FileManager()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a file
        txt_file = os.path.join(temp_dir, "sample.txt")
        file_obj = manager.get_file(txt_file)
        
        # Chain operations
        file_obj.create("Hello, World!").write("Updated content!").read()
        
        print(f"File created: {file_obj.path}")
        print(f"File type: {file_obj.file_type}")
        print(f"File exists: {file_obj.exists}")
        print(f"Content: {file_obj.content}")
        
        # Get file info
        info = file_obj.get_info()
        print(f"File size: {info['size']} bytes")


def chaining_operations():
    """Demonstrate method chaining."""
    print("\\n=== Chaining Operations ===")
    
    manager = FileManager()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create JSON file with chaining
        json_file = os.path.join(temp_dir, "data.json")
        yaml_file = os.path.join(temp_dir, "data.yaml")
        
        data = {"name": "Alice", "age": 30, "skills": ["Python", "JavaScript"]}
        
        # Chain: create → write → convert → get info
        file_obj = (manager.get_file(json_file)
                   .create(data)
                   .convert_to(yaml_file, "yaml"))
        
        print(f"Created and converted: {json_file} → {yaml_file}")
        print(f"YAML file exists: {os.path.exists(yaml_file)}")


def context_manager_example():
    """Using context manager for file editing."""
    print("\\n=== Context Manager Example ===")
    
    manager = FileManager()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        json_file = os.path.join(temp_dir, "config.json")
        file_obj = manager.get_file(json_file)
        
        # Initial data
        config = {"debug": True, "port": 8080}
        file_obj.create(config)
        
        print(f"Initial config: {file_obj.content}")
        
        # Edit using context manager
        with file_obj.editing() as f:
            current_config = f.content
            current_config["debug"] = False
            current_config["host"] = "0.0.0.0"
            f._cached_content = current_config
        
        # Read updated content
        file_obj.read()
        print(f"Updated config: {file_obj.content}")


def batch_operations():
    """Batch operations using FileBatch."""
    print("\\n=== Batch Operations ===")
    
    manager = FileManager()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create multiple files
        files = []
        for i in range(3):
            file_path = os.path.join(temp_dir, f"document_{i}.txt")
            content = f"This is document number {i+1}\\nWith some sample content."
            manager.get_file(file_path).create(content)
            files.append(file_path)
        
        # Get batch object
        batch = manager.get_batch(files)
        
        print(f"Batch contains {len(batch)} files")
        print(f"File types: {set(f.file_type for f in batch.files)}")
        
        # Batch convert to JSON
        output_dir = os.path.join(temp_dir, "converted")
        os.makedirs(output_dir, exist_ok=True)
        
        results = batch.convert_all("json", output_dir)
        success_count = sum(1 for success in results.values() if success)
        
        print(f"\\nBatch conversion: {success_count}/{len(files)} successful")
        
        # Get info for all files
        all_info = batch.get_all_info()
        for file_path, info in all_info.items():
            print(f"  {os.path.basename(file_path)}: {info.get('size', 0)} bytes")


def media_collection_example():
    """Using MediaCollection for type-specific operations."""
    print("\\n=== Media Collection Example ===")
    
    manager = FileManager()
    media = manager.MediaCollection(manager)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create different file types
        txt_file = os.path.join(temp_dir, "document.txt")
        json_file = os.path.join(temp_dir, "data.json")
        
        manager.get_file(txt_file).create("Sample text content")
        manager.get_file(json_file).create({"key": "value"})
        
        # Use media collection for text files
        text_files = [txt_file, json_file]
        text_batch = media.text(text_files)
        
        print(f"Text batch contains {len(text_batch)} files")
        
        # Individual text file
        single_text = media.text(txt_file)
        print(f"Single text file: {single_text.basename}")
        print(f"Content: {single_text.content}")


def image_operations_example():
    """Image-specific operations (would work with actual images)."""
    print("\\n=== Image Operations Example ===")
    
    # Note: These operations would work with actual image files
    print("Example image operations (requires actual image files and PIL):")
    
    code_example = '''
    manager = FileManager()
    
    # Single image operations
    image = manager.get_file("photo.jpg")
    
    # Chain image operations
    thumbnail = (image
                .resize_to("thumbnail.jpg", (200, 200))
                .apply_filter_to("filtered.jpg", "blur"))
    
    # Crop and convert
    cropped = image.crop_to("cropped.png", (100, 100, 400, 400))
    '''
    
    print(code_example)


def main():
    """Run all examples."""
    print("Novus PyTils Object-Oriented API Examples")
    print("=========================================")
    
    basic_file_operations()
    chaining_operations() 
    context_manager_example()
    batch_operations()
    media_collection_example()
    image_operations_example()
    
    print("\\n=== Examples completed ===")


if __name__ == "__main__":
    main()