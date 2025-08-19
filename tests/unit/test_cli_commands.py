"""Unit tests for cli.commands module."""
import pytest
from unittest.mock import patch, MagicMock

from novus_pytils.cli.commands import (
    print_success, print_error, print_warning, print_info,
    cmd_info, cmd_convert, cmd_resize, cmd_crop, cmd_trim,
    cmd_merge, cmd_split, cmd_thumbnail, cmd_filter,
    cmd_extract_audio, cmd_extract_frames, cmd_batch,
    cmd_server, cmd_supported, main
)


class TestPrintFunctions:
    """Test colored print functions."""
    
    @patch('builtins.print')
    def test_print_success(self, mock_print):
        """Test print_success function."""
        print_success("Test message")
        mock_print.assert_called_once_with("\033[92m✓ Test message\033[0m")
    
    @patch('builtins.print')
    def test_print_error(self, mock_print):
        """Test print_error function."""
        print_error("Error message")
        mock_print.assert_called_once_with("\033[91m✗ Error message\033[0m")
    
    @patch('builtins.print')
    def test_print_warning(self, mock_print):
        """Test print_warning function."""
        print_warning("Warning message")
        mock_print.assert_called_once_with("\033[93m⚠ Warning message\033[0m")
    
    @patch('builtins.print')
    def test_print_info(self, mock_print):
        """Test print_info function."""
        print_info("Info message")
        mock_print.assert_called_once_with("\033[94mℹ Info message\033[0m")


class TestCommandFunctions:
    """Test command functions."""
    
    @patch('novus_pytils.cli.commands.get_file_info')
    @patch('novus_pytils.cli.commands.print_success')
    @patch('builtins.print')
    def test_cmd_info_regular_output(self, mock_print, mock_success, mock_get_info):
        """Test cmd_info with regular output."""
        mock_get_info.return_value = {
            'size': 1024,
            'extension': '.txt',
            'width': 100,
            'height': 200,
            'duration': 300,
            'format': 'text'
        }
        
        args = MagicMock()
        args.file = 'test.txt'
        args.json = False
        
        cmd_info(args)
        
        mock_get_info.assert_called_once_with('test.txt')
        mock_success.assert_called_once()
        assert mock_print.call_count >= 6  # Multiple print calls for info display
    
    @patch('novus_pytils.cli.commands.get_file_info')
    @patch('json.dumps')
    @patch('builtins.print')
    def test_cmd_info_json_output(self, mock_print, mock_json_dumps, mock_get_info):
        """Test cmd_info with JSON output."""
        mock_get_info.return_value = {'size': 1024}
        mock_json_dumps.return_value = '{"size": 1024}'
        
        args = MagicMock()
        args.file = 'test.txt'
        args.json = True
        
        cmd_info(args)
        
        mock_get_info.assert_called_once_with('test.txt')
        mock_json_dumps.assert_called_once()
        mock_print.assert_called()
    
    @patch('novus_pytils.cli.commands.get_file_info')
    @patch('novus_pytils.cli.commands.print_error')
    @patch('sys.exit')
    def test_cmd_info_exception(self, mock_exit, mock_error, mock_get_info):
        """Test cmd_info with exception."""
        mock_get_info.side_effect = Exception("Test error")
        
        args = MagicMock()
        args.file = 'test.txt'
        args.json = False
        
        cmd_info(args)
        
        mock_error.assert_called_once()
        mock_exit.assert_called_once_with(1)
    
    @patch('novus_pytils.cli.commands.convert_file')
    @patch('novus_pytils.cli.commands.print_success')
    def test_cmd_convert_success(self, mock_success, mock_convert):
        """Test cmd_convert with success."""
        mock_convert.return_value = True
        
        args = MagicMock()
        args.input = 'input.txt'
        args.output = 'output.pdf'
        args.format = 'pdf'
        args.quality = 95
        args.bitrate = '192k'
        args.resolution = '1920x1080'
        
        cmd_convert(args)
        
        mock_convert.assert_called_once_with(
            'input.txt', 'output.pdf', 'pdf',
            quality=95, bitrate='192k', resolution='1920x1080'
        )
        mock_success.assert_called_once()
    
    @patch('novus_pytils.cli.commands.convert_file')
    @patch('novus_pytils.cli.commands.print_error')
    @patch('sys.exit')
    def test_cmd_convert_failure(self, mock_exit, mock_error, mock_convert):
        """Test cmd_convert with failure."""
        mock_convert.return_value = False
        
        args = MagicMock()
        args.input = 'input.txt'
        args.output = 'output.pdf'
        args.format = 'pdf'
        args.quality = None
        args.bitrate = None
        args.resolution = None
        
        cmd_convert(args)
        
        mock_error.assert_called_once()
        mock_exit.assert_called_once_with(1)
    
    @patch('novus_pytils.cli.commands.resize_image')
    @patch('novus_pytils.cli.commands.print_success')
    def test_cmd_resize_success(self, mock_success, mock_resize):
        """Test cmd_resize with success."""
        mock_resize.return_value = True
        
        args = MagicMock()
        args.input = 'input.jpg'
        args.output = 'output.jpg'
        args.width = 800
        args.height = 600
        args.maintain_aspect = True
        args.quality = 90
        
        cmd_resize(args)
        
        mock_resize.assert_called_once_with(
            'input.jpg', 'output.jpg', (800, 600), True, quality=90
        )
        mock_success.assert_called_once()
    
    @patch('novus_pytils.cli.commands.crop_image')
    @patch('novus_pytils.cli.commands.print_success')
    def test_cmd_crop_success(self, mock_success, mock_crop):
        """Test cmd_crop with success."""
        mock_crop.return_value = True
        
        args = MagicMock()
        args.input = 'input.jpg'
        args.output = 'output.jpg'
        args.left = 10
        args.top = 20
        args.right = 100
        args.bottom = 200
        args.quality = 95
        
        cmd_crop(args)
        
        mock_crop.assert_called_once_with(
            'input.jpg', 'output.jpg', (10, 20, 100, 200), quality=95
        )
        mock_success.assert_called_once()
    
    @patch('os.path.splitext')
    @patch('novus_pytils.cli.commands.trim_audio')
    @patch('novus_pytils.cli.commands.print_success')
    def test_cmd_trim_audio_success(self, mock_success, mock_trim_audio, mock_splitext):
        """Test cmd_trim with audio file."""
        mock_splitext.return_value = ('test', '.mp3')
        mock_trim_audio.return_value = True
        
        args = MagicMock()
        args.input = 'input.mp3'
        args.output = 'output.mp3'
        args.start = '1000'
        args.end = '5000'
        args.duration = None
        
        cmd_trim(args)
        
        mock_trim_audio.assert_called_once_with('input.mp3', 'output.mp3', 1000, 5000)
        mock_success.assert_called_once()
    
    @patch('os.path.splitext')
    @patch('novus_pytils.cli.commands.trim_video')
    @patch('novus_pytils.cli.commands.print_success')
    def test_cmd_trim_video_success(self, mock_success, mock_trim_video, mock_splitext):
        """Test cmd_trim with video file."""
        mock_splitext.return_value = ('test', '.mp4')
        mock_trim_video.return_value = True
        
        args = MagicMock()
        args.input = 'input.mp4'
        args.output = 'output.mp4'
        args.start = '00:01:00'
        args.end = None
        args.duration = '00:02:00'
        
        cmd_trim(args)
        
        mock_trim_video.assert_called_once_with('input.mp4', 'output.mp4', '00:01:00', '00:02:00', None)
        mock_success.assert_called_once()
    
    @patch('os.path.splitext')
    @patch('novus_pytils.cli.commands.print_error')
    @patch('sys.exit')
    def test_cmd_trim_unsupported_format(self, mock_exit, mock_error, mock_splitext):
        """Test cmd_trim with unsupported format."""
        mock_splitext.return_value = ('test', '.unknown')
        
        args = MagicMock()
        args.input = 'input.unknown'
        args.output = 'output.unknown'
        args.start = '1000'
        args.end = '5000'
        
        cmd_trim(args)
        
        mock_error.assert_called_once()
        mock_exit.assert_called_once_with(1)
    
    @patch('novus_pytils.cli.commands.merge_files')
    @patch('novus_pytils.cli.commands.print_success')
    def test_cmd_merge_success(self, mock_success, mock_merge):
        """Test cmd_merge with success."""
        mock_merge.return_value = True
        
        args = MagicMock()
        args.inputs = ['file1.txt', 'file2.txt']
        args.output = 'merged.txt'
        args.separator = '\n'
        args.orientation = 'horizontal'
        
        cmd_merge(args)
        
        mock_merge.assert_called_once_with(
            ['file1.txt', 'file2.txt'], 'merged.txt',
            separator='\n', orientation='horizontal'
        )
        mock_success.assert_called_once()
    
    @patch('novus_pytils.cli.commands.split_file')
    @patch('novus_pytils.cli.commands.print_success')
    def test_cmd_split_success(self, mock_success, mock_split):
        """Test cmd_split with success."""
        mock_split.return_value = ['part1.txt', 'part2.txt']
        
        args = MagicMock()
        args.input = 'input.txt'
        args.output_dir = '/output'
        args.lines_per_file = 1000
        args.min_silence_len = None
        args.silence_thresh = None
        args.list_outputs = False
        
        cmd_split(args)
        
        mock_split.assert_called_once_with(
            'input.txt', '/output', lines_per_file=1000
        )
        mock_success.assert_called_once()
    
    @patch('novus_pytils.cli.commands.create_thumbnail')
    @patch('novus_pytils.cli.commands.print_success')
    def test_cmd_thumbnail_success(self, mock_success, mock_thumbnail):
        """Test cmd_thumbnail with success."""
        mock_thumbnail.return_value = True
        
        args = MagicMock()
        args.input = 'input.jpg'
        args.output = 'thumb.jpg'
        args.size = 128
        args.time_position = '00:00:01'
        
        cmd_thumbnail(args)
        
        mock_thumbnail.assert_called_once_with(
            'input.jpg', 'thumb.jpg',
            size=(128, 128), time_position='00:00:01'
        )
        mock_success.assert_called_once()
    
    @patch('novus_pytils.cli.commands.apply_filter')
    @patch('novus_pytils.cli.commands.print_success')
    def test_cmd_filter_success(self, mock_success, mock_filter):
        """Test cmd_filter with success."""
        mock_filter.return_value = True
        
        args = MagicMock()
        args.input = 'input.jpg'
        args.output = 'output.jpg'
        args.filter_name = 'blur'
        args.value = 2.5
        
        cmd_filter(args)
        
        mock_filter.assert_called_once_with(
            'input.jpg', 'output.jpg', 'blur', value=2.5
        )
        mock_success.assert_called_once()
    
    @patch('novus_pytils.cli.commands.extract_audio_from_video')
    @patch('novus_pytils.cli.commands.print_success')
    def test_cmd_extract_audio_success(self, mock_success, mock_extract):
        """Test cmd_extract_audio with success."""
        mock_extract.return_value = True
        
        args = MagicMock()
        args.input = 'input.mp4'
        args.output = 'output.mp3'
        
        cmd_extract_audio(args)
        
        mock_extract.assert_called_once_with('input.mp4', 'output.mp3')
        mock_success.assert_called_once()
    
    @patch('novus_pytils.cli.commands.extract_frames_from_video')
    @patch('novus_pytils.cli.commands.print_success')
    def test_cmd_extract_frames_success(self, mock_success, mock_extract):
        """Test cmd_extract_frames with success."""
        mock_extract.return_value = ['frame1.jpg', 'frame2.jpg']
        
        args = MagicMock()
        args.input = 'input.mp4'
        args.output_dir = '/output'
        args.fps = 2.0
        args.list_outputs = False
        
        cmd_extract_frames(args)
        
        mock_extract.assert_called_once_with('input.mp4', '/output', 2.0)
        mock_success.assert_called_once()
    
    @patch('novus_pytils.cli.commands.batch_convert')
    @patch('novus_pytils.cli.commands.print_info')
    def test_cmd_batch_convert_success(self, mock_info, mock_batch_convert):
        """Test cmd_batch with convert operation."""
        mock_batch_convert.return_value = {'file1.jpg': True, 'file2.jpg': True}
        
        args = MagicMock()
        args.operation = 'convert'
        args.files = ['file1.jpg', 'file2.jpg']
        args.target_format = '.png'
        args.output_dir = '/output'
        args.dest_dir = None
        args.verbose = False
        
        cmd_batch(args)
        
        mock_batch_convert.assert_called_once_with(['file1.jpg', 'file2.jpg'], '.png', '/output')
        mock_info.assert_called_once()
    
    @patch('novus_pytils.cli.commands.batch_operation')
    @patch('novus_pytils.cli.commands.print_info')
    @patch('novus_pytils.cli.commands.print_success')
    def test_cmd_batch_other_operation_verbose(self, mock_success, mock_info, mock_batch_operation):
        """Test cmd_batch with other operation and verbose output."""
        mock_batch_operation.return_value = {'file1.txt': True, 'file2.txt': False}
        
        args = MagicMock()
        args.operation = 'copy'
        args.files = ['file1.txt', 'file2.txt']
        args.target_format = None
        args.output_dir = None
        args.dest_dir = '/dest'
        args.verbose = True
        
        with patch('sys.exit') as mock_exit:
            cmd_batch(args)
            mock_exit.assert_called_once_with(1)  # Due to failures
        
        mock_batch_operation.assert_called_once_with(['file1.txt', 'file2.txt'], 'copy', dest_dir='/dest')
        mock_info.assert_called_once()
        assert mock_success.call_count >= 1  # For successful files
    
    @patch('novus_pytils.cli.commands.FASTAPI_AVAILABLE', True)
    @patch('novus_pytils.cli.commands.run_server')
    @patch('novus_pytils.cli.commands.print_info')
    def test_cmd_server_success(self, mock_info, mock_run_server):
        """Test cmd_server with FastAPI available."""
        args = MagicMock()
        args.host = 'localhost'
        args.port = 8080
        args.upload_dir = '/uploads'
        
        cmd_server(args)
        
        mock_run_server.assert_called_once_with('localhost', 8080, '/uploads')
        assert mock_info.call_count >= 2  # Multiple info messages
    
    @patch('novus_pytils.cli.commands.FASTAPI_AVAILABLE', False)
    @patch('novus_pytils.cli.commands.print_error')
    @patch('sys.exit')
    def test_cmd_server_no_fastapi(self, mock_exit, mock_error):
        """Test cmd_server without FastAPI."""
        args = MagicMock()
        
        cmd_server(args)
        
        mock_error.assert_called_once()
        mock_exit.assert_called_once_with(1)
    
    @patch('novus_pytils.cli.commands.get_supported_conversions')
    @patch('builtins.print')
    def test_cmd_supported_success(self, mock_print, mock_get_supported):
        """Test cmd_supported with success."""
        mock_get_supported.return_value = ['.png', '.gif', '.bmp']
        
        args = MagicMock()
        args.file = 'test.jpg'
        
        cmd_supported(args)
        
        mock_get_supported.assert_called_once_with('test.jpg')
        assert mock_print.call_count >= 4  # Header + 3 formats


class TestMainFunction:
    """Test main function."""
    
    @patch('sys.argv', ['novus-pytils'])
    @patch('argparse.ArgumentParser.print_help')
    @patch('sys.exit')
    def test_main_no_command(self, mock_exit, mock_help):
        """Test main with no command."""
        main()
        
        mock_help.assert_called_once()
        mock_exit.assert_called_once_with(1)
    
    @patch('sys.argv', ['novus-pytils', 'info', 'test.txt'])
    @patch('novus_pytils.cli.commands.cmd_info')
    def test_main_with_valid_command(self, mock_cmd_info):
        """Test main with valid command."""
        main()
        
        mock_cmd_info.assert_called_once()
    
    @patch('sys.argv', ['novus-pytils', 'invalid-command'])
    @patch('novus_pytils.cli.commands.print_error')
    @patch('sys.exit')
    def test_main_with_invalid_command(self, mock_exit, mock_error):
        """Test main with invalid command."""
        main()
        
        mock_error.assert_called_once()
        mock_exit.assert_called_once_with(1)
    
    @patch('sys.argv', ['novus-pytils', '--version'])
    def test_main_version(self):
        """Test main with version flag."""
        with pytest.raises(SystemExit):  # argparse calls sys.exit for --version
            main()