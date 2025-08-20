"""Web API for file operations using FastAPI.

This module provides a RESTful web API for file management operations
with support for upload, download, and conversion operations.
"""
import os
import tempfile
from typing import List, Optional, Dict, Any, Union

try:
    from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Query
    from fastapi.responses import FileResponse, JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    
    class BaseModel:
        pass

from novus_pytils.api.functional import (
    delete_file,
    convert_file, get_file_info, get_supported_conversions,
    batch_convert, batch_operation, resize_image, crop_image, trim_audio, trim_video,
    create_thumbnail, apply_filter, extract_audio_from_video,
    extract_frames_from_video
)


class ConversionRequest(BaseModel):
    target_format: str
    quality: Optional[int] = 95
    bitrate: Optional[str] = None
    resolution: Optional[str] = None


class ResizeRequest(BaseModel):
    width: int
    height: int
    maintain_aspect: bool = True
    quality: Optional[int] = 95


class CropRequest(BaseModel):
    left: int
    top: int
    right: int
    bottom: int
    quality: Optional[int] = 95


class TrimRequest(BaseModel):
    start: Union[int, str]
    end: Optional[Union[int, str]] = None
    duration: Optional[Union[int, str]] = None


class FilterRequest(BaseModel):
    filter_name: str
    value: Optional[float] = None


class FileOperationResponse(BaseModel):
    success: bool
    message: str
    file_path: Optional[str] = None
    file_info: Optional[Dict[str, Any]] = None


class BatchOperationResponse(BaseModel):
    results: Dict[str, bool]
    success_count: int
    failure_count: int


def create_web_api(upload_dir: str = None, max_file_size: int = 100 * 1024 * 1024) -> FastAPI:
    """Create and configure FastAPI application."""
    if not FASTAPI_AVAILABLE:
        raise ImportError("FastAPI is required for web API. Install with: pip install fastapi uvicorn python-multipart")
    
    app = FastAPI(
        title="Novus PyTils File Management API",
        description="Comprehensive file management API with support for text, image, audio, and video operations",
        version="1.0.0"
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    upload_directory = upload_dir or tempfile.gettempdir()
    os.makedirs(upload_directory, exist_ok=True)
    
    @app.get("/")
    async def root():
        return {"message": "Novus PyTils File Management API", "version": "1.0.0"}
    
    @app.post("/upload", response_model=FileOperationResponse)
    async def upload_file(file: UploadFile = File(...)):
        """Upload a file to the server."""
        try:
            content = await file.read()
            if len(content) > max_file_size:
                raise HTTPException(status_code=413, detail="File too large")
            
            file_path = os.path.join(upload_directory, file.filename)
            
            with open(file_path, "wb") as buffer:
                buffer.write(content)
            
            file_info = get_file_info(file_path)
            
            return FileOperationResponse(
                success=True,
                message="File uploaded successfully",
                file_path=file_path,
                file_info=file_info
            )
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/download/{file_path:path}")
    async def download_file(file_path: str):
        """Download a file from the server."""
        try:
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail="File not found")
            
            filename = os.path.basename(file_path)
            return FileResponse(file_path, filename=filename)
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/info/{file_path:path}")
    async def file_info(file_path: str):
        """Get file information and metadata."""
        try:
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail="File not found")
            
            info = get_file_info(file_path)
            return JSONResponse(content=info)
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.delete("/file/{file_path:path}")
    async def delete_file_endpoint(file_path: str):
        """Delete a file."""
        try:
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail="File not found")
            
            success = delete_file(file_path)
            
            return FileOperationResponse(
                success=success,
                message="File deleted successfully" if success else "Failed to delete file"
            )
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/convert/{file_path:path}")
    async def convert_file_endpoint(file_path: str, request: ConversionRequest):
        """Convert a file to a different format."""
        try:
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail="File not found")
            
            base_name = os.path.splitext(file_path)[0]
            target_ext = request.target_format if request.target_format.startswith('.') else f'.{request.target_format}'
            output_path = f"{base_name}_converted{target_ext}"
            
            kwargs = {}
            if request.quality:
                kwargs['quality'] = request.quality
            if request.bitrate:
                kwargs['bitrate'] = request.bitrate
            if request.resolution:
                kwargs['resolution'] = request.resolution
            
            success = convert_file(file_path, output_path, request.target_format, **kwargs)
            
            return FileOperationResponse(
                success=success,
                message="File converted successfully" if success else "Conversion failed",
                file_path=output_path if success else None
            )
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/resize/{file_path:path}")
    async def resize_image_endpoint(file_path: str, request: ResizeRequest):
        """Resize an image file."""
        try:
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail="File not found")
            
            base_name = os.path.splitext(file_path)[0]
            ext = os.path.splitext(file_path)[1]
            output_path = f"{base_name}_resized{ext}"
            
            success = resize_image(
                file_path, output_path, 
                (request.width, request.height), 
                request.maintain_aspect,
                quality=request.quality
            )
            
            return FileOperationResponse(
                success=success,
                message="Image resized successfully" if success else "Resize failed",
                file_path=output_path if success else None
            )
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/crop/{file_path:path}")
    async def crop_image_endpoint(file_path: str, request: CropRequest):
        """Crop an image file."""
        try:
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail="File not found")
            
            base_name = os.path.splitext(file_path)[0]
            ext = os.path.splitext(file_path)[1]
            output_path = f"{base_name}_cropped{ext}"
            
            box = (request.left, request.top, request.right, request.bottom)
            success = crop_image(file_path, output_path, box, quality=request.quality)
            
            return FileOperationResponse(
                success=success,
                message="Image cropped successfully" if success else "Crop failed",
                file_path=output_path if success else None
            )
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/trim/{file_path:path}")
    async def trim_file_endpoint(file_path: str, request: TrimRequest):
        """Trim audio or video file."""
        try:
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail="File not found")
            
            base_name = os.path.splitext(file_path)[0]
            ext = os.path.splitext(file_path)[1]
            output_path = f"{base_name}_trimmed{ext}"
            
            get_file_info(file_path)
            
            if ext.lower() in ['.wav', '.mp3', '.ogg', '.flac', '.aac']:
                success = trim_audio(file_path, output_path, int(request.start), int(request.end) if request.end else None)
            elif ext.lower() in ['.mp4', '.avi', '.mkv', '.mov', '.webm']:
                success = trim_video(file_path, output_path, str(request.start), 
                                   str(request.duration) if request.duration else None,
                                   str(request.end) if request.end else None)
            else:
                raise HTTPException(status_code=400, detail="File format not supported for trimming")
            
            return FileOperationResponse(
                success=success,
                message="File trimmed successfully" if success else "Trim failed",
                file_path=output_path if success else None
            )
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/filter/{file_path:path}")
    async def apply_filter_endpoint(file_path: str, request: FilterRequest):
        """Apply filter to image or video."""
        try:
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail="File not found")
            
            base_name = os.path.splitext(file_path)[0]
            ext = os.path.splitext(file_path)[1]
            output_path = f"{base_name}_filtered{ext}"
            
            kwargs = {}
            if request.value is not None:
                kwargs['value'] = request.value
            
            success = apply_filter(file_path, output_path, request.filter_name, **kwargs)
            
            return FileOperationResponse(
                success=success,
                message="Filter applied successfully" if success else "Filter application failed",
                file_path=output_path if success else None
            )
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/thumbnail/{file_path:path}")
    async def create_thumbnail_endpoint(file_path: str, size: int = Query(128)):
        """Create thumbnail from image or video."""
        try:
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail="File not found")
            
            base_name = os.path.splitext(file_path)[0]
            output_path = f"{base_name}_thumbnail.jpg"
            
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']:
                success = create_thumbnail(file_path, output_path, size=(size, size))
            elif ext in ['.mp4', '.avi', '.mkv', '.mov', '.webm']:
                success = create_thumbnail(file_path, output_path, time_position='00:00:01')
            else:
                raise HTTPException(status_code=400, detail="File format not supported for thumbnail")
            
            return FileOperationResponse(
                success=success,
                message="Thumbnail created successfully" if success else "Thumbnail creation failed",
                file_path=output_path if success else None
            )
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/batch/convert")
    async def batch_convert_endpoint(
        files: List[str] = Form(...),
        target_format: str = Form(...),
        output_dir: Optional[str] = Form(None)
    ):
        """Convert multiple files to target format."""
        try:
            results = batch_convert(files, target_format, output_dir)
            success_count = sum(1 for success in results.values() if success)
            failure_count = len(results) - success_count
            
            return BatchOperationResponse(
                results=results,
                success_count=success_count,
                failure_count=failure_count
            )
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/batch/{operation}")
    async def batch_operation_endpoint(
        operation: str,
        files: List[str] = Form(...),
        dest_dir: Optional[str] = Form(None)
    ):
        """Perform batch operations on multiple files."""
        try:
            kwargs = {}
            if dest_dir:
                kwargs['dest_dir'] = dest_dir
            
            results = batch_operation(files, operation, **kwargs)
            success_count = sum(1 for success in results.values() if success)
            failure_count = len(results) - success_count
            
            return BatchOperationResponse(
                results=results,
                success_count=success_count,
                failure_count=failure_count
            )
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/supported-conversions/{file_path:path}")
    async def supported_conversions_endpoint(file_path: str):
        """Get supported conversion formats for a file."""
        try:
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail="File not found")
            
            conversions = get_supported_conversions(file_path)
            return JSONResponse(content={"supported_formats": conversions})
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/extract-audio/{file_path:path}")
    async def extract_audio_endpoint(file_path: str):
        """Extract audio from video file."""
        try:
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail="File not found")
            
            base_name = os.path.splitext(file_path)[0]
            output_path = f"{base_name}_audio.mp3"
            
            success = extract_audio_from_video(file_path, output_path)
            
            return FileOperationResponse(
                success=success,
                message="Audio extracted successfully" if success else "Audio extraction failed",
                file_path=output_path if success else None
            )
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/extract-frames/{file_path:path}")
    async def extract_frames_endpoint(file_path: str, fps: float = Query(1.0)):
        """Extract frames from video as images."""
        try:
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail="File not found")
            
            output_dir = os.path.join(upload_directory, f"frames_{os.path.basename(file_path)}")
            os.makedirs(output_dir, exist_ok=True)
            
            frame_files = extract_frames_from_video(file_path, output_dir, fps)
            
            return JSONResponse(content={
                "success": len(frame_files) > 0,
                "message": f"Extracted {len(frame_files)} frames",
                "frame_files": frame_files,
                "output_directory": output_dir
            })
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    return app


def run_server(host: str = "0.0.0.0", port: int = 8000, upload_dir: str = None):
    """Run the web API server."""
    if not FASTAPI_AVAILABLE:
        raise ImportError("FastAPI and uvicorn are required. Install with: pip install fastapi uvicorn python-multipart")
    
    try:
        import uvicorn
    except ImportError:
        raise ImportError("uvicorn is required to run the server. Install with: pip install uvicorn")
    
    app = create_web_api(upload_dir)
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()