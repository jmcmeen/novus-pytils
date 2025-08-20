"""Unit tests for api.web_api module."""
import pytest
from unittest.mock import patch, MagicMock, mock_open

from novus_pytils.api.app import (
    ConversionRequest, ResizeRequest, CropRequest, TrimRequest, FilterRequest,
    FileOperationResponse, BatchOperationResponse, create_web_api, run_server,
    FASTAPI_AVAILABLE
)


class TestModels:
    """Test Pydantic models."""
    
    def test_conversion_request(self):
        """Test ConversionRequest model."""
        request = ConversionRequest(target_format="mp4", quality=90)
        assert request.target_format == "mp4"
        assert request.quality == 90
        assert request.bitrate is None
        assert request.resolution is None
    
    def test_resize_request(self):
        """Test ResizeRequest model."""
        request = ResizeRequest(width=800, height=600, maintain_aspect=False)
        assert request.width == 800
        assert request.height == 600
        assert request.maintain_aspect is False
        assert request.quality == 95
    
    def test_crop_request(self):
        """Test CropRequest model."""
        request = CropRequest(left=10, top=20, right=100, bottom=200)
        assert request.left == 10
        assert request.top == 20
        assert request.right == 100
        assert request.bottom == 200
        assert request.quality == 95
    
    def test_trim_request(self):
        """Test TrimRequest model."""
        request = TrimRequest(start=1000, end=5000)
        assert request.start == 1000
        assert request.end == 5000
        assert request.duration is None
    
    def test_filter_request(self):
        """Test FilterRequest model."""
        request = FilterRequest(filter_name="blur", value=2.5)
        assert request.filter_name == "blur"
        assert request.value == 2.5
    
    def test_file_operation_response(self):
        """Test FileOperationResponse model."""
        response = FileOperationResponse(
            success=True,
            message="Success",
            file_path="/path/to/file.txt"
        )
        assert response.success is True
        assert response.message == "Success"
        assert response.file_path == "/path/to/file.txt"
        assert response.file_info is None
    
    def test_batch_operation_response(self):
        """Test BatchOperationResponse model."""
        response = BatchOperationResponse(
            results={"file1.txt": True, "file2.txt": False},
            success_count=1,
            failure_count=1
        )
        assert response.results == {"file1.txt": True, "file2.txt": False}
        assert response.success_count == 1
        assert response.failure_count == 1


class TestCreateWebAPI:
    """Test create_web_api function."""
    
    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
    @patch('tempfile.gettempdir')
    @patch('os.makedirs')
    def test_create_web_api_default_upload_dir(self, mock_makedirs, mock_gettempdir):
        """Test creating web API with default upload directory."""
        mock_gettempdir.return_value = "/tmp"
        
        app = create_web_api()
        
        assert app.title == "Novus PyTils File Management API"
        assert app.version == "1.0.0"
        mock_makedirs.assert_called_once_with("/tmp", exist_ok=True)
    
    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
    @patch('os.makedirs')
    def test_create_web_api_custom_upload_dir(self, mock_makedirs):
        """Test creating web API with custom upload directory."""
        app = create_web_api(upload_dir="/custom/upload")
        
        assert app.title == "Novus PyTils File Management API"
        mock_makedirs.assert_called_once_with("/custom/upload", exist_ok=True)
    
    @pytest.mark.skipif(FASTAPI_AVAILABLE, reason="FastAPI is available")
    def test_create_web_api_no_fastapi(self):
        """Test creating web API without FastAPI raises ImportError."""
        with pytest.raises(ImportError, match="FastAPI is required"):
            create_web_api()


@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
class TestWebAPIEndpoints:
    """Test web API endpoints."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.app = create_web_api(upload_dir="/tmp")
        from fastapi.testclient import TestClient
        self.client = TestClient(self.app)
    
    def test_root_endpoint(self):
        """Test root endpoint."""
        response = self.client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Novus PyTils File Management API"
        assert data["version"] == "1.0.0"
    
    @patch('novus_pytils.api.app.get_file_info')
    @patch('builtins.open', new_callable=mock_open)
    def test_upload_file_success(self, mock_file, mock_get_info):
        """Test successful file upload."""
        mock_get_info.return_value = {"size": 1024, "type": "text"}
        
        files = {"file": ("test.txt", b"test content", "text/plain")}
        response = self.client.post("/upload", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "File uploaded successfully"
        assert "file_path" in data
        assert "file_info" in data
    
    def test_upload_file_too_large(self):
        """Test file upload that's too large."""
        large_content = b"x" * (101 * 1024 * 1024)  # 101MB
        files = {"file": ("large.txt", large_content, "text/plain")}
        
        response = self.client.post("/upload", files=files)
        
        assert response.status_code == 413
    
    @patch('os.path.exists')
    @patch('novus_pytils.api.app.FileResponse')
    def test_download_file_success(self, mock_response, mock_exists):
        """Test successful file download."""
        mock_exists.return_value = True
        
        self.client.get("/download/test.txt")
        mock_response.assert_called_once()
    
    @patch('os.path.exists')
    def test_download_file_not_found(self, mock_exists):
        """Test downloading non-existent file."""
        mock_exists.return_value = False
        
        response = self.client.get("/download/nonexistent.txt")
        
        assert response.status_code == 404
    
    @patch('os.path.exists')
    @patch('novus_pytils.api.app.get_file_info')
    def test_file_info_success(self, mock_get_info, mock_exists):
        """Test getting file info."""
        mock_exists.return_value = True
        mock_get_info.return_value = {"size": 1024, "type": "text"}
        
        response = self.client.get("/info/test.txt")
        
        assert response.status_code == 200
        data = response.json()
        assert data == {"size": 1024, "type": "text"}
    
    @patch('os.path.exists')
    def test_file_info_not_found(self, mock_exists):
        """Test getting info for non-existent file."""
        mock_exists.return_value = False
        
        response = self.client.get("/info/nonexistent.txt")
        
        assert response.status_code == 404
    
    @patch('os.path.exists')
    @patch('novus_pytils.api.app.delete_file')
    def test_delete_file_success(self, mock_delete, mock_exists):
        """Test successful file deletion."""
        mock_exists.return_value = True
        mock_delete.return_value = True
        
        response = self.client.delete("/file/test.txt")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "File deleted successfully"
    
    @patch('os.path.exists')
    def test_delete_file_not_found(self, mock_exists):
        """Test deleting non-existent file."""
        mock_exists.return_value = False
        
        response = self.client.delete("/file/nonexistent.txt")
        
        assert response.status_code == 404
    
    @patch('os.path.exists')
    @patch('novus_pytils.api.app.convert_file')
    @patch('os.path.splitext')
    def test_convert_file_success(self, mock_splitext, mock_convert, mock_exists):
        """Test successful file conversion."""
        mock_exists.return_value = True
        mock_convert.return_value = True
        mock_splitext.return_value = ('test', '.txt')
        
        request_data = {
            "target_format": "pdf",
            "quality": 90
        }
        
        response = self.client.post("/convert/test.txt", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "File converted successfully"
        assert "file_path" in data
    
    @patch('os.path.exists')
    @patch('novus_pytils.api.app.resize_image')
    @patch('os.path.splitext')
    def test_resize_image_success(self, mock_splitext, mock_resize, mock_exists):
        """Test successful image resize."""
        mock_exists.return_value = True
        mock_resize.return_value = True
        mock_splitext.return_value = ('test', '.jpg')
        
        request_data = {
            "width": 800,
            "height": 600,
            "maintain_aspect": True,
            "quality": 95
        }
        
        response = self.client.post("/resize/test.jpg", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Image resized successfully"
    
    @patch('os.path.exists')
    @patch('novus_pytils.api.app.crop_image')
    @patch('os.path.splitext')
    def test_crop_image_success(self, mock_splitext, mock_crop, mock_exists):
        """Test successful image crop."""
        mock_exists.return_value = True
        mock_crop.return_value = True
        mock_splitext.return_value = ('test', '.jpg')
        
        request_data = {
            "left": 10,
            "top": 20,
            "right": 100,
            "bottom": 200,
            "quality": 95
        }
        
        response = self.client.post("/crop/test.jpg", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Image cropped successfully"
    
    @patch('os.path.exists')
    @patch('novus_pytils.api.app.trim_audio')
    @patch('novus_pytils.api.app.get_file_info')
    @patch('os.path.splitext')
    def test_trim_audio_success(self, mock_splitext, mock_get_info, mock_trim, mock_exists):
        """Test successful audio trim."""
        mock_exists.return_value = True
        mock_trim.return_value = True
        mock_get_info.return_value = {"duration": 300}
        mock_splitext.return_value = ('test', '.mp3')
        
        request_data = {
            "start": 1000,
            "end": 5000
        }
        
        response = self.client.post("/trim/test.mp3", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "File trimmed successfully"
    
    @patch('os.path.exists')
    @patch('novus_pytils.api.app.apply_filter')
    @patch('os.path.splitext')
    def test_apply_filter_success(self, mock_splitext, mock_filter, mock_exists):
        """Test successful filter application."""
        mock_exists.return_value = True
        mock_filter.return_value = True
        mock_splitext.return_value = ('test', '.jpg')
        
        request_data = {
            "filter_name": "blur",
            "value": 2.5
        }
        
        response = self.client.post("/filter/test.jpg", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Filter applied successfully"
    
    @patch('os.path.exists')
    @patch('novus_pytils.api.app.create_thumbnail')
    @patch('os.path.splitext')
    def test_create_thumbnail_image_success(self, mock_splitext, mock_thumbnail, mock_exists):
        """Test successful thumbnail creation from image."""
        mock_exists.return_value = True
        mock_thumbnail.return_value = True
        mock_splitext.return_value = ('test', '.jpg')
        
        response = self.client.post("/thumbnail/test.jpg?size=128")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Thumbnail created successfully"
    
    @patch('os.path.exists')
    @patch('novus_pytils.api.app.create_thumbnail')
    @patch('os.path.splitext')
    def test_create_thumbnail_video_success(self, mock_splitext, mock_thumbnail, mock_exists):
        """Test successful thumbnail creation from video."""
        mock_exists.return_value = True
        mock_thumbnail.return_value = True
        mock_splitext.return_value = ('test', '.mp4')
        
        response = self.client.post("/thumbnail/test.mp4?size=128")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Thumbnail created successfully"
    
    @patch('novus_pytils.api.app.batch_convert')
    def test_batch_convert_success(self, mock_batch_convert):
        """Test successful batch conversion."""
        mock_batch_convert.return_value = {"file1.jpg": True, "file2.jpg": True}
        
        form_data = {
            "files": ["file1.jpg", "file2.jpg"],
            "target_format": "png"
        }
        
        response = self.client.post("/batch/convert", data=form_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success_count"] == 2
        assert data["failure_count"] == 0
        assert data["results"] == {"file1.jpg": True, "file2.jpg": True}
    
    @patch('novus_pytils.api.app.batch_operation')
    def test_batch_operation_success(self, mock_batch_operation):
        """Test successful batch operation."""
        mock_batch_operation.return_value = {"file1.txt": True, "file2.txt": False}
        
        form_data = {
            "files": ["file1.txt", "file2.txt"],
            "dest_dir": "/dest"
        }
        
        response = self.client.post("/batch/copy", data=form_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success_count"] == 1
        assert data["failure_count"] == 1
        assert data["results"] == {"file1.txt": True, "file2.txt": False}
    
    @patch('os.path.exists')
    @patch('novus_pytils.api.app.get_supported_conversions')
    def test_supported_conversions_success(self, mock_conversions, mock_exists):
        """Test getting supported conversions."""
        mock_exists.return_value = True
        mock_conversions.return_value = [".png", ".gif", ".bmp"]
        
        response = self.client.get("/supported-conversions/test.jpg")
        
        assert response.status_code == 200
        data = response.json()
        assert data["supported_formats"] == [".png", ".gif", ".bmp"]
    
    @patch('os.path.exists')
    @patch('novus_pytils.api.app.extract_audio_from_video')
    @patch('os.path.splitext')
    def test_extract_audio_success(self, mock_splitext, mock_extract, mock_exists):
        """Test successful audio extraction from video."""
        mock_exists.return_value = True
        mock_extract.return_value = True
        mock_splitext.return_value = ('test', '.mp4')
        
        response = self.client.post("/extract-audio/test.mp4")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Audio extracted successfully"
    
    @patch('os.path.exists')
    @patch('novus_pytils.api.app.extract_frames_from_video')
    @patch('os.makedirs')
    @patch('os.path.basename')
    def test_extract_frames_success(self, mock_basename, mock_makedirs, mock_extract, mock_exists):
        """Test successful frame extraction from video."""
        mock_exists.return_value = True
        mock_extract.return_value = ["frame1.jpg", "frame2.jpg"]
        mock_basename.return_value = "test.mp4"
        
        response = self.client.post("/extract-frames/test.mp4?fps=2.0")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Extracted 2 frames"
        assert data["frame_files"] == ["frame1.jpg", "frame2.jpg"]


class TestRunServer:
    """Test run_server function."""
    
    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
    @patch('builtins.__import__')
    @patch('novus_pytils.api.app.create_web_api')
    def test_run_server_success(self, mock_create_app, mock_import):
        """Test successful server run."""
        mock_app = MagicMock()
        mock_create_app.return_value = mock_app
        
        mock_uvicorn = MagicMock()
        def side_effect(name, *args, **kwargs):
            if name == 'uvicorn':
                return mock_uvicorn
            return __import__(name, *args, **kwargs)
        mock_import.side_effect = side_effect
        
        run_server(host="localhost", port=8080, upload_dir="/custom")
        
        mock_create_app.assert_called_once_with("/custom")
        mock_uvicorn.run.assert_called_once_with(mock_app, host="localhost", port=8080)
    
    @pytest.mark.skipif(FASTAPI_AVAILABLE, reason="FastAPI is available")
    def test_run_server_no_fastapi(self):
        """Test running server without FastAPI."""
        with pytest.raises(ImportError, match="FastAPI and uvicorn are required"):
            run_server()
    
    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
    @patch('novus_pytils.api.app.create_web_api')
    def test_run_server_no_uvicorn(self, mock_create_app):
        """Test running server without uvicorn."""
        with patch.dict('sys.modules', {'uvicorn': None}):
            with pytest.raises(ImportError, match="uvicorn is required"):
                run_server()