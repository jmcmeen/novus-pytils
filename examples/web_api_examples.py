"""Examples for using the web API.

This file shows how to interact with the Novus PyTils web API.
"""
import requests
import os
from typing import Dict, Any


class FileManagerClient:
    """Client for interacting with Novus PyTils web API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def upload_file(self, file_path: str) -> Dict[str, Any]:
        """Upload a file to the server."""
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f)}
            response = self.session.post(f"{self.base_url}/upload", files=files)
            return response.json()
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get file information."""
        response = self.session.get(f"{self.base_url}/info/{file_path}")
        return response.json()
    
    def convert_file(self, file_path: str, target_format: str, quality: int = None) -> Dict[str, Any]:
        """Convert a file to different format."""
        data = {"target_format": target_format}
        if quality:
            data["quality"] = quality
        
        response = self.session.post(f"{self.base_url}/convert/{file_path}", json=data)
        return response.json()
    
    def resize_image(self, file_path: str, width: int, height: int, maintain_aspect: bool = True) -> Dict[str, Any]:
        """Resize an image."""
        data = {
            "width": width,
            "height": height,
            "maintain_aspect": maintain_aspect
        }
        response = self.session.post(f"{self.base_url}/resize/{file_path}", json=data)
        return response.json()
    
    def crop_image(self, file_path: str, left: int, top: int, right: int, bottom: int) -> Dict[str, Any]:
        """Crop an image."""
        data = {
            "left": left,
            "top": top,
            "right": right,
            "bottom": bottom
        }
        response = self.session.post(f"{self.base_url}/crop/{file_path}", json=data)
        return response.json()
    
    def apply_filter(self, file_path: str, filter_name: str, value: float = None) -> Dict[str, Any]:
        """Apply filter to image or video."""
        data = {"filter_name": filter_name}
        if value is not None:
            data["value"] = value
        
        response = self.session.post(f"{self.base_url}/filter/{file_path}", json=data)
        return response.json()
    
    def create_thumbnail(self, file_path: str, size: int = 128) -> Dict[str, Any]:
        """Create thumbnail from image or video."""
        response = self.session.post(f"{self.base_url}/thumbnail/{file_path}?size={size}")
        return response.json()
    
    def batch_convert(self, files: list, target_format: str, output_dir: str = None) -> Dict[str, Any]:
        """Convert multiple files."""
        data = {
            "files": files,
            "target_format": target_format
        }
        if output_dir:
            data["output_dir"] = output_dir
        
        response = self.session.post(f"{self.base_url}/batch/convert", data=data)
        return response.json()
    
    def delete_file(self, file_path: str) -> Dict[str, Any]:
        """Delete a file."""
        response = self.session.delete(f"{self.base_url}/file/{file_path}")
        return response.json()
    
    def download_file(self, file_path: str, save_path: str):
        """Download a file from the server."""
        response = self.session.get(f"{self.base_url}/download/{file_path}")
        
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return True
        return False


def basic_api_example():
    """Basic API usage example."""
    print("\\n=== Basic API Example ===")
    
    FileManagerClient()
    
    # Note: This assumes the server is running
    print("Example API calls (requires running server):")
    
    example_calls = [
        "client.upload_file('document.txt')",
        "client.get_file_info('uploaded_file.txt')",
        "client.convert_file('document.txt', 'json')",
        "client.resize_image('photo.jpg', 800, 600)",
        "client.create_thumbnail('video.mp4')"
    ]
    
    for call in example_calls:
        print(f"  {call}")


def batch_operations_example():
    """Batch operations via API."""
    print("\\n=== Batch Operations Example ===")
    
    FileManagerClient()
    
    print("Example batch operations:")
    print("  # Convert multiple files")
    print("  files = ['doc1.txt', 'doc2.txt', 'doc3.txt']")
    print("  result = client.batch_convert(files, 'json')")
    print("  print(f'Converted {result[\\\"success_count\\\"]} files')")


def image_processing_example():
    """Image processing via API."""
    print("\\n=== Image Processing Example ===")
    
    example_workflow = '''
    client = FileManagerClient()
    
    # Upload image
    upload_result = client.upload_file("original.jpg")
    image_path = upload_result["file_path"]
    
    # Resize image
    resize_result = client.resize_image(image_path, 1920, 1080)
    resized_path = resize_result["file_path"]
    
    # Apply filter
    filter_result = client.apply_filter(resized_path, "blur")
    filtered_path = filter_result["file_path"]
    
    # Create thumbnail
    thumb_result = client.create_thumbnail(filtered_path, size=256)
    thumbnail_path = thumb_result["file_path"]
    
    # Download processed image
    client.download_file(filtered_path, "processed.jpg")
    '''
    
    print("Example image processing workflow:")
    print(example_workflow)


def server_startup_example():
    """Example of starting the web server."""
    print("\\n=== Server Startup Example ===")
    
    startup_code = '''
    from novus_pytils.api.web_api import run_server
    
    # Start server with custom settings
    run_server(
        host="0.0.0.0",      # Accept connections from any IP
        port=8080,           # Custom port
        upload_dir="/tmp"    # Custom upload directory
    )
    '''
    
    print("Starting the web server:")
    print(startup_code)
    
    print("\\nOr via command line:")
    print("  novus-pytils server --host 0.0.0.0 --port 8080")


def main():
    """Run all examples."""
    print("Novus PyTils Web API Examples")
    print("=============================")
    
    basic_api_example()
    batch_operations_example()
    image_processing_example()
    server_startup_example()
    
    print("\\n=== Examples completed ===")
    print("\\nTo run the server: novus-pytils server")
    print("Then visit: http://localhost:8000 for API documentation")


if __name__ == "__main__":
    main()