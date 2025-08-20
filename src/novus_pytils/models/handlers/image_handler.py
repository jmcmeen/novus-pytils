"""Image file handler with format conversion capabilities.

This module provides comprehensive image file handling including reading, writing,
and conversion between various image formats using minimal dependencies.
"""
import os
import base64
from typing import Any, Dict, List, Tuple
from novus_pytils.models.base import BaseFileHandler, FileManagerMixin, ConversionError
from novus_pytils.globals import SUPPORTED_IMAGE_EXTENSIONS, IMAGE_CONVERSION_MAP


class ImageWrapper:
    """Wrapper class to isolate PIL dependency."""
    
    def __init__(self):
        self._pil_available = False
        self._Image = None
        self._ImageOps = None
        self._ImageFilter = None
        
        try:
            from PIL import Image, ImageOps, ImageFilter
            self._Image = Image
            self._ImageOps = ImageOps
            self._ImageFilter = ImageFilter
            self._pil_available = True
        except ImportError:
            pass
    
    @property
    def available(self) -> bool:
        return self._pil_available
    
    def open(self, file_path: str):
        if not self._pil_available:
            raise ConversionError("PIL/Pillow is required for image operations. Install with: pip install Pillow")
        return self._Image.open(file_path)
    
    def new(self, mode: str, size: Tuple[int, int], color=0):
        if not self._pil_available:
            raise ConversionError("PIL/Pillow is required for image operations. Install with: pip install Pillow")
        return self._Image.new(mode, size, color)
    
    def blend(self, img1, img2, alpha: float):
        if not self._pil_available:
            raise ConversionError("PIL/Pillow is required for image operations. Install with: pip install Pillow")
        return self._Image.blend(img1, img2, alpha)
    
    @property
    def ImageOps(self):
        if not self._pil_available:
            raise ConversionError("PIL/Pillow is required for image operations. Install with: pip install Pillow")
        return self._ImageOps
    
    @property
    def ImageFilter(self):
        if not self._pil_available:
            raise ConversionError("PIL/Pillow is required for image operations. Install with: pip install Pillow")
        return self._ImageFilter


class ImageHandler(BaseFileHandler, FileManagerMixin):
    """Handler for image files with conversion capabilities."""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = SUPPORTED_IMAGE_EXTENSIONS
        self.conversion_map = IMAGE_CONVERSION_MAP
        self.image_wrapper = ImageWrapper()
    
    def read(self, file_path: str) -> Any:
        """Read image file and return PIL Image object or base64 data."""
        if not self.validate_file(file_path):
            raise ConversionError(f"Unsupported file format: {file_path}")
        
        if self.image_wrapper.available:
            return self.image_wrapper.open(file_path)
        else:
            with open(file_path, 'rb') as file:
                return base64.b64encode(file.read()).decode('utf-8')
    
    def write(self, file_path: str, content: Any, quality: int = 95, **kwargs) -> bool:
        """Write image content to file."""
        try:
            os.makedirs(os.path.dirname(file_path) or '.', exist_ok=True)
            
            if isinstance(content, str) and content.startswith('data:image'):
                header, data = content.split(',', 1)
                image_data = base64.b64decode(data)
                with open(file_path, 'wb') as file:
                    file.write(image_data)
                return True
            elif isinstance(content, str):
                image_data = base64.b64decode(content)
                with open(file_path, 'wb') as file:
                    file.write(image_data)
                return True
            elif self.image_wrapper.available:
                ext = os.path.splitext(file_path)[1].lower()
                save_format = self._get_pil_format(ext)
                
                if save_format == 'JPEG':
                    content.save(file_path, format=save_format, quality=quality, optimize=True)
                elif save_format == 'PNG':
                    content.save(file_path, format=save_format, optimize=True)
                else:
                    content.save(file_path, format=save_format)
                return True
            else:
                raise ConversionError("Cannot write image without PIL/Pillow installed")
        
        except Exception as e:
            raise ConversionError(f"Failed to write image {file_path}: {str(e)}")
    
    def convert(self, input_path: str, output_path: str, target_format: str, **kwargs) -> bool:
        """Convert image from one format to another."""
        if not self.validate_file(input_path):
            raise ConversionError(f"Unsupported input file format: {input_path}")
        
        input_ext = os.path.splitext(input_path)[1].lower()
        target_ext = target_format if target_format.startswith('.') else f'.{target_format}'
        
        if target_ext not in self.get_supported_conversions(input_ext):
            raise ConversionError(f"Cannot convert from {input_ext} to {target_ext}")
        
        if not self.image_wrapper.available:
            raise ConversionError("PIL/Pillow is required for image conversion. Install with: pip install Pillow")
        
        try:
            with self.image_wrapper.open(input_path) as image:
                if image.mode == 'RGBA' and target_ext in ['.jpg', '.jpeg']:
                    background = self.image_wrapper.new('RGB', image.size, (255, 255, 255))
                    background.paste(image, mask=image.split()[-1])
                    image = background
                elif image.mode == 'P':
                    image = image.convert('RGB')
                
                quality = kwargs.get('quality', 95)
                return self.write(output_path, image, quality=quality)
        
        except Exception as e:
            raise ConversionError(f"Conversion failed from {input_path} to {output_path}: {str(e)}")
    
    def resize(self, input_path: str, output_path: str, size: Tuple[int, int], 
               maintain_aspect: bool = True, **kwargs) -> bool:
        """Resize an image."""
        if not self.image_wrapper.available:
            raise ConversionError("PIL/Pillow is required for image resizing")
        
        try:
            with self.image_wrapper.open(input_path) as image:
                if maintain_aspect:
                    image = self.image_wrapper.ImageOps.fit(image, size, method=0, bleed=0.0, centering=(0.5, 0.5))
                else:
                    image = image.resize(size)
                
                quality = kwargs.get('quality', 95)
                return self.write(output_path, image, quality=quality)
        
        except Exception as e:
            raise ConversionError(f"Failed to resize image: {str(e)}")
    
    def crop(self, input_path: str, output_path: str, box: Tuple[int, int, int, int], **kwargs) -> bool:
        """Crop an image to specified box (left, top, right, bottom)."""
        if not self.image_wrapper.available:
            raise ConversionError("PIL/Pillow is required for image cropping")
        
        try:
            with self.image_wrapper.open(input_path) as image:
                cropped = image.crop(box)
                quality = kwargs.get('quality', 95)
                return self.write(output_path, cropped, quality=quality)
        
        except Exception as e:
            raise ConversionError(f"Failed to crop image: {str(e)}")
    
    def rotate(self, input_path: str, output_path: str, angle: float, **kwargs) -> bool:
        """Rotate an image by specified angle."""
        if not self.image_wrapper.available:
            raise ConversionError("PIL/Pillow is required for image rotation")
        
        try:
            with self.image_wrapper.open(input_path) as image:
                rotated = image.rotate(angle, expand=kwargs.get('expand', True))
                quality = kwargs.get('quality', 95)
                return self.write(output_path, rotated, quality=quality)
        
        except Exception as e:
            raise ConversionError(f"Failed to rotate image: {str(e)}")
    
    def apply_filter(self, input_path: str, output_path: str, filter_name: str, **kwargs) -> bool:
        """Apply filter to image."""
        if not self.image_wrapper.available:
            raise ConversionError("PIL/Pillow is required for image filtering")
        
        filter_map = {
            'blur': self.image_wrapper.ImageFilter.BLUR,
            'contour': self.image_wrapper.ImageFilter.CONTOUR,
            'detail': self.image_wrapper.ImageFilter.DETAIL,
            'edge_enhance': self.image_wrapper.ImageFilter.EDGE_ENHANCE,
            'emboss': self.image_wrapper.ImageFilter.EMBOSS,
            'sharpen': self.image_wrapper.ImageFilter.SHARPEN,
            'smooth': self.image_wrapper.ImageFilter.SMOOTH
        }
        
        if filter_name not in filter_map:
            raise ConversionError(f"Unsupported filter: {filter_name}")
        
        try:
            with self.image_wrapper.open(input_path) as image:
                filtered = image.filter(filter_map[filter_name])
                quality = kwargs.get('quality', 95)
                return self.write(output_path, filtered, quality=quality)
        
        except Exception as e:
            raise ConversionError(f"Failed to apply filter: {str(e)}")
    
    def get_image_info(self, file_path: str) -> Dict[str, Any]:
        """Get image metadata and information."""
        base_info = self.get_metadata(file_path)
        
        if not self.image_wrapper.available:
            return base_info
        
        try:
            with self.image_wrapper.open(file_path) as image:
                base_info.update({
                    'width': image.width,
                    'height': image.height,
                    'mode': image.mode,
                    'format': image.format,
                    'has_transparency': image.mode in ('RGBA', 'LA') or 'transparency' in image.info
                })
        except Exception:
            pass
        
        return base_info
    
    def _get_pil_format(self, extension: str) -> str:
        """Map file extension to PIL format."""
        format_map = {
            '.jpg': 'JPEG',
            '.jpeg': 'JPEG',
            '.png': 'PNG',
            '.gif': 'GIF',
            '.bmp': 'BMP',
            '.tiff': 'TIFF',
            '.tif': 'TIFF',
            '.webp': 'WEBP'
        }
        return format_map.get(extension.lower(), 'PNG')
    
    def create_thumbnail(self, input_path: str, output_path: str, size: Tuple[int, int] = (128, 128), **kwargs) -> bool:
        """Create thumbnail of image."""
        if not self.image_wrapper.available:
            raise ConversionError("PIL/Pillow is required for thumbnail creation")
        
        try:
            with self.image_wrapper.open(input_path) as image:
                image.thumbnail(size)
                quality = kwargs.get('quality', 85)
                return self.write(output_path, image, quality=quality)
        
        except Exception as e:
            raise ConversionError(f"Failed to create thumbnail: {str(e)}")
    
    def merge_images(self, image_paths: List[str], output_path: str, orientation: str = 'horizontal', **kwargs) -> bool:
        """Merge multiple images into one."""
        if not self.image_wrapper.available:
            raise ConversionError("PIL/Pillow is required for image merging")
        
        if len(image_paths) < 2:
            raise ConversionError("At least 2 images required for merging")
        
        try:
            images = [self.image_wrapper.open(path) for path in image_paths]
            
            if orientation == 'horizontal':
                total_width = sum(img.width for img in images)
                max_height = max(img.height for img in images)
                merged = self.image_wrapper.new('RGB', (total_width, max_height))
                
                x_offset = 0
                for img in images:
                    merged.paste(img, (x_offset, 0))
                    x_offset += img.width
            else:
                max_width = max(img.width for img in images)
                total_height = sum(img.height for img in images)
                merged = self.image_wrapper.new('RGB', (max_width, total_height))
                
                y_offset = 0
                for img in images:
                    merged.paste(img, (0, y_offset))
                    y_offset += img.height
            
            for img in images:
                img.close()
            
            quality = kwargs.get('quality', 95)
            return self.write(output_path, merged, quality=quality)
        
        except Exception as e:
            raise ConversionError(f"Failed to merge images: {str(e)}")