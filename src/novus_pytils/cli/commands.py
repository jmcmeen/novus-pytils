"""Command-line interface for file operations.

This module provides a comprehensive CLI for all file management operations
including conversions, batch processing, and media manipulation.
"""
import os
import sys
import argparse
import json

from novus_pytils.api.functional import (
    convert_file, get_file_info, get_supported_conversions,
    batch_convert, batch_operation, resize_image, crop_image, trim_audio, trim_video,
    merge_files, split_file, create_thumbnail, apply_filter, extract_audio_from_video,
    extract_frames_from_video
)
from novus_pytils.api.web_api import run_server, FASTAPI_AVAILABLE


def print_success(message: str):
    """Print success message in green."""
    print(f"\033[92m✓ {message}\033[0m")


def print_error(message: str):
    """Print error message in red."""
    print(f"\033[91m✗ {message}\033[0m")


def print_warning(message: str):
    """Print warning message in yellow."""
    print(f"\033[93m⚠ {message}\033[0m")


def print_info(message: str):
    """Print info message in blue."""
    print(f"\033[94mℹ {message}\033[0m")


def cmd_info(args):
    """Get file information."""
    try:
        info = get_file_info(args.file)
        if args.json:
            print(json.dumps(info, indent=2, default=str))
        else:
            print(f"File: {args.file}")
            print(f"Size: {info.get('size', 'Unknown')} bytes")
            print(f"Extension: {info.get('extension', 'Unknown')}")
            if 'width' in info and 'height' in info:
                print(f"Dimensions: {info['width']}x{info['height']}")
            if 'duration' in info:
                print(f"Duration: {info['duration']} seconds")
            if 'format' in info:
                print(f"Format: {info['format']}")
        print_success(f"Retrieved information for {args.file}")
    except Exception as e:
        print_error(f"Failed to get info: {e}")
        sys.exit(1)


def cmd_convert(args):
    """Convert file to different format."""
    try:
        kwargs = {}
        if args.quality:
            kwargs['quality'] = args.quality
        if args.bitrate:
            kwargs['bitrate'] = args.bitrate
        if args.resolution:
            kwargs['resolution'] = args.resolution
        
        success = convert_file(args.input, args.output, args.format, **kwargs)
        if success:
            print_success(f"Converted {args.input} to {args.output}")
        else:
            print_error("Conversion failed")
            sys.exit(1)
    except Exception as e:
        print_error(f"Conversion failed: {e}")
        sys.exit(1)


def cmd_resize(args):
    """Resize image."""
    try:
        success = resize_image(args.input, args.output, (args.width, args.height), 
                              args.maintain_aspect, quality=args.quality or 95)
        if success:
            print_success(f"Resized {args.input} to {args.width}x{args.height}")
        else:
            print_error("Resize failed")
            sys.exit(1)
    except Exception as e:
        print_error(f"Resize failed: {e}")
        sys.exit(1)


def cmd_crop(args):
    """Crop image."""
    try:
        box = (args.left, args.top, args.right, args.bottom)
        success = crop_image(args.input, args.output, box, quality=args.quality or 95)
        if success:
            print_success(f"Cropped {args.input}")
        else:
            print_error("Crop failed")
            sys.exit(1)
    except Exception as e:
        print_error(f"Crop failed: {e}")
        sys.exit(1)


def cmd_trim(args):
    """Trim audio or video."""
    try:
        ext = os.path.splitext(args.input)[1].lower()
        
        if ext in ['.wav', '.mp3', '.ogg', '.flac', '.aac']:
            success = trim_audio(args.input, args.output, int(args.start), 
                               int(args.end) if args.end else None)
        elif ext in ['.mp4', '.avi', '.mkv', '.mov', '.webm']:
            success = trim_video(args.input, args.output, str(args.start), 
                               str(args.duration) if args.duration else None,
                               str(args.end) if args.end else None)
        else:
            print_error("File format not supported for trimming")
            sys.exit(1)
            return
        
        if success:
            print_success(f"Trimmed {args.input}")
        else:
            print_error("Trim failed")
            sys.exit(1)
    except Exception as e:
        print_error(f"Trim failed: {e}")
        sys.exit(1)


def cmd_merge(args):
    """Merge multiple files."""
    try:
        kwargs = {}
        if args.separator:
            kwargs['separator'] = args.separator
        if args.orientation:
            kwargs['orientation'] = args.orientation
        
        success = merge_files(args.inputs, args.output, **kwargs)
        if success:
            print_success(f"Merged {len(args.inputs)} files into {args.output}")
        else:
            print_error("Merge failed")
            sys.exit(1)
    except Exception as e:
        print_error(f"Merge failed: {e}")
        sys.exit(1)


def cmd_split(args):
    """Split file into parts."""
    try:
        kwargs = {}
        if args.lines_per_file:
            kwargs['lines_per_file'] = args.lines_per_file
        if args.min_silence_len:
            kwargs['min_silence_len'] = args.min_silence_len
        if args.silence_thresh:
            kwargs['silence_thresh'] = args.silence_thresh
        
        output_files = split_file(args.input, args.output_dir, **kwargs)
        print_success(f"Split {args.input} into {len(output_files)} parts")
        if args.list_outputs:
            for f in output_files:
                print(f"  - {f}")
    except Exception as e:
        print_error(f"Split failed: {e}")
        sys.exit(1)


def cmd_thumbnail(args):
    """Create thumbnail."""
    try:
        kwargs = {}
        if args.size:
            kwargs['size'] = (args.size, args.size)
        if args.time_position:
            kwargs['time_position'] = args.time_position
        
        success = create_thumbnail(args.input, args.output, **kwargs)
        if success:
            print_success(f"Created thumbnail: {args.output}")
        else:
            print_error("Thumbnail creation failed")
            sys.exit(1)
    except Exception as e:
        print_error(f"Thumbnail creation failed: {e}")
        sys.exit(1)


def cmd_filter(args):
    """Apply filter to image or video."""
    try:
        kwargs = {}
        if args.value is not None:
            kwargs['value'] = args.value
        
        success = apply_filter(args.input, args.output, args.filter_name, **kwargs)
        if success:
            print_success(f"Applied {args.filter_name} filter to {args.input}")
        else:
            print_error("Filter application failed")
            sys.exit(1)
    except Exception as e:
        print_error(f"Filter application failed: {e}")
        sys.exit(1)


def cmd_extract_audio(args):
    """Extract audio from video."""
    try:
        success = extract_audio_from_video(args.input, args.output)
        if success:
            print_success(f"Extracted audio from {args.input}")
        else:
            print_error("Audio extraction failed")
            sys.exit(1)
    except Exception as e:
        print_error(f"Audio extraction failed: {e}")
        sys.exit(1)


def cmd_extract_frames(args):
    """Extract frames from video."""
    try:
        frame_files = extract_frames_from_video(args.input, args.output_dir, args.fps)
        print_success(f"Extracted {len(frame_files)} frames from {args.input}")
        if args.list_outputs:
            for f in frame_files:
                print(f"  - {f}")
    except Exception as e:
        print_error(f"Frame extraction failed: {e}")
        sys.exit(1)


def cmd_batch(args):
    """Perform batch operations."""
    try:
        if args.operation == 'convert':
            results = batch_convert(args.files, args.target_format, args.output_dir)
        else:
            kwargs = {}
            if args.dest_dir:
                kwargs['dest_dir'] = args.dest_dir
            results = batch_operation(args.files, args.operation, **kwargs)
        
        success_count = sum(1 for success in results.values() if success)
        failure_count = len(results) - success_count
        
        print_info(f"Batch {args.operation}: {success_count} succeeded, {failure_count} failed")
        
        if args.verbose:
            for file_path, success in results.items():
                if success:
                    print_success(f"  {file_path}")
                else:
                    print_error(f"  {file_path}")
        
        if failure_count > 0:
            sys.exit(1)
    except Exception as e:
        print_error(f"Batch operation failed: {e}")
        sys.exit(1)


def cmd_server(args):
    """Run web API server."""
    if not FASTAPI_AVAILABLE:
        print_error("FastAPI is required for web server. Install with: pip install fastapi uvicorn python-multipart")
        sys.exit(1)
        return
    
    print_info(f"Starting server on {args.host}:{args.port}")
    if args.upload_dir:
        print_info(f"Upload directory: {args.upload_dir}")
    
    try:
        run_server(args.host, args.port, args.upload_dir)
    except Exception as e:
        print_error(f"Server failed: {e}")
        sys.exit(1)


def cmd_supported(args):
    """List supported conversion formats."""
    try:
        conversions = get_supported_conversions(args.file)
        print(f"Supported conversions for {args.file}:")
        for fmt in conversions:
            print(f"  - {fmt}")
    except Exception as e:
        print_error(f"Failed to get supported formats: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Novus PyTils - Comprehensive file management CLI")
    parser.add_argument('--version', action='version', version='Novus PyTils 1.0.0')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    info_parser = subparsers.add_parser('info', help='Get file information')
    info_parser.add_argument('file', help='File path')
    info_parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    convert_parser = subparsers.add_parser('convert', help='Convert file format')
    convert_parser.add_argument('input', help='Input file')
    convert_parser.add_argument('output', help='Output file')
    convert_parser.add_argument('format', help='Target format')
    convert_parser.add_argument('--quality', type=int, help='Quality (1-100)')
    convert_parser.add_argument('--bitrate', help='Bitrate (e.g., 192k)')
    convert_parser.add_argument('--resolution', help='Resolution (e.g., 1920x1080)')
    
    resize_parser = subparsers.add_parser('resize', help='Resize image')
    resize_parser.add_argument('input', help='Input image')
    resize_parser.add_argument('output', help='Output image')
    resize_parser.add_argument('width', type=int, help='Width in pixels')
    resize_parser.add_argument('height', type=int, help='Height in pixels')
    resize_parser.add_argument('--no-maintain-aspect', dest='maintain_aspect', action='store_false', help="Don't maintain aspect ratio")
    resize_parser.add_argument('--quality', type=int, help='Quality (1-100)')
    
    crop_parser = subparsers.add_parser('crop', help='Crop image')
    crop_parser.add_argument('input', help='Input image')
    crop_parser.add_argument('output', help='Output image')
    crop_parser.add_argument('left', type=int, help='Left coordinate')
    crop_parser.add_argument('top', type=int, help='Top coordinate')
    crop_parser.add_argument('right', type=int, help='Right coordinate')
    crop_parser.add_argument('bottom', type=int, help='Bottom coordinate')
    crop_parser.add_argument('--quality', type=int, help='Quality (1-100)')
    
    trim_parser = subparsers.add_parser('trim', help='Trim audio/video')
    trim_parser.add_argument('input', help='Input file')
    trim_parser.add_argument('output', help='Output file')
    trim_parser.add_argument('start', help='Start time/position')
    trim_parser.add_argument('--end', help='End time/position')
    trim_parser.add_argument('--duration', help='Duration')
    
    merge_parser = subparsers.add_parser('merge', help='Merge multiple files')
    merge_parser.add_argument('inputs', nargs='+', help='Input files')
    merge_parser.add_argument('output', help='Output file')
    merge_parser.add_argument('--separator', help='Text separator for merging')
    merge_parser.add_argument('--orientation', choices=['horizontal', 'vertical'], help='Image merge orientation')
    
    split_parser = subparsers.add_parser('split', help='Split file into parts')
    split_parser.add_argument('input', help='Input file')
    split_parser.add_argument('output_dir', help='Output directory')
    split_parser.add_argument('--lines-per-file', type=int, help='Lines per file for text')
    split_parser.add_argument('--min-silence-len', type=int, help='Minimum silence length for audio')
    split_parser.add_argument('--silence-thresh', type=int, help='Silence threshold for audio')
    split_parser.add_argument('--list-outputs', action='store_true', help='List output files')
    
    thumbnail_parser = subparsers.add_parser('thumbnail', help='Create thumbnail')
    thumbnail_parser.add_argument('input', help='Input file')
    thumbnail_parser.add_argument('output', help='Output thumbnail')
    thumbnail_parser.add_argument('--size', type=int, default=128, help='Thumbnail size')
    thumbnail_parser.add_argument('--time-position', help='Time position for video thumbnail')
    
    filter_parser = subparsers.add_parser('filter', help='Apply filter')
    filter_parser.add_argument('input', help='Input file')
    filter_parser.add_argument('output', help='Output file')
    filter_parser.add_argument('filter_name', help='Filter name')
    filter_parser.add_argument('--value', type=float, help='Filter value parameter')
    
    extract_audio_parser = subparsers.add_parser('extract-audio', help='Extract audio from video')
    extract_audio_parser.add_argument('input', help='Input video')
    extract_audio_parser.add_argument('output', help='Output audio file')
    
    extract_frames_parser = subparsers.add_parser('extract-frames', help='Extract frames from video')
    extract_frames_parser.add_argument('input', help='Input video')
    extract_frames_parser.add_argument('output_dir', help='Output directory')
    extract_frames_parser.add_argument('--fps', type=float, default=1.0, help='Frames per second')
    extract_frames_parser.add_argument('--list-outputs', action='store_true', help='List output files')
    
    batch_parser = subparsers.add_parser('batch', help='Batch operations')
    batch_parser.add_argument('operation', choices=['convert', 'copy', 'move', 'delete'], help='Operation')
    batch_parser.add_argument('files', nargs='+', help='Input files')
    batch_parser.add_argument('--target-format', help='Target format for conversion')
    batch_parser.add_argument('--output-dir', help='Output directory for conversion')
    batch_parser.add_argument('--dest-dir', help='Destination directory for copy/move')
    batch_parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    server_parser = subparsers.add_parser('server', help='Run web API server')
    server_parser.add_argument('--host', default='0.0.0.0', help='Host address')
    server_parser.add_argument('--port', type=int, default=8000, help='Port number')
    server_parser.add_argument('--upload-dir', help='Upload directory')
    
    supported_parser = subparsers.add_parser('supported', help='List supported conversions')
    supported_parser.add_argument('file', help='File path')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
        return
    
    command_map = {
        'info': cmd_info,
        'convert': cmd_convert,
        'resize': cmd_resize,
        'crop': cmd_crop,
        'trim': cmd_trim,
        'merge': cmd_merge,
        'split': cmd_split,
        'thumbnail': cmd_thumbnail,
        'filter': cmd_filter,
        'extract-audio': cmd_extract_audio,
        'extract-frames': cmd_extract_frames,
        'batch': cmd_batch,
        'server': cmd_server,
        'supported': cmd_supported
    }
    
    if args.command in command_map:
        command_map[args.command](args)
    else:
        print_error(f"Unknown command: {args.command}")
        sys.exit(1)


if __name__ == '__main__':
    main()