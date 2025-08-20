"""Unit tests for utils.console module."""
from unittest.mock import patch

from novus_pytils.console import (
    print_color, print_success, print_error, print_warning, print_info,
    print_table, print_progress_bar, confirm_action, get_user_input,
    clear_screen, move_cursor, ColorCode
)


class TestColorCode:
    """Test ColorCode enum."""
    
    def test_color_codes_exist(self):
        """Test that all expected color codes exist."""
        assert hasattr(ColorCode, 'RED')
        assert hasattr(ColorCode, 'GREEN')
        assert hasattr(ColorCode, 'YELLOW')
        assert hasattr(ColorCode, 'BLUE')
        assert hasattr(ColorCode, 'MAGENTA')
        assert hasattr(ColorCode, 'CYAN')
        assert hasattr(ColorCode, 'WHITE')
        assert hasattr(ColorCode, 'RESET')
    
    def test_color_code_values(self):
        """Test color code values are strings."""
        assert isinstance(ColorCode.RED.value, str)
        assert isinstance(ColorCode.GREEN.value, str)
        assert isinstance(ColorCode.RESET.value, str)


class TestPrintColored:
    """Test print_colored function."""
    
    @patch('builtins.print')
    def test_print_colored_basic(self, mock_print):
        """Test basic colored printing."""
        print_color("Test message", ColorCode.RED)
        
        expected = f"{ColorCode.RED.value}Test message{ColorCode.RESET.value}"
        mock_print.assert_called_once_with(expected)
    
    @patch('builtins.print')
    def test_print_colored_with_background(self, mock_print):
        """Test colored printing with background color."""
        print_color("Test message", ColorCode.RED, ColorCode.YELLOW)
        
        expected = f"{ColorCode.RED.value}{ColorCode.YELLOW.value}Test message{ColorCode.RESET.value}"
        mock_print.assert_called_once_with(expected)
    
    @patch('builtins.print')
    def test_print_colored_no_color(self, mock_print):
        """Test printing without color when disabled."""
        with patch('novus_pytils.utils.console.COLORS_ENABLED', False):
            print_color("Test message", ColorCode.RED)
        
        mock_print.assert_called_once_with("Test message")
    
    @patch('builtins.print')
    def test_print_colored_with_kwargs(self, mock_print):
        """Test colored printing with additional print kwargs."""
        print_color("Test message", ColorCode.GREEN, end="", flush=True)
        
        expected = f"{ColorCode.GREEN.value}Test message{ColorCode.RESET.value}"
        mock_print.assert_called_once_with(expected, end="", flush=True)


class TestConveniencePrintFunctions:
    """Test convenience print functions."""
    
    @patch('novus_pytils.utils.console.print_colored')
    def test_print_success(self, mock_print_colored):
        """Test print_success function."""
        print_success("Success message")
        
        mock_print_colored.assert_called_once_with("✓ Success message", ColorCode.GREEN)
    
    @patch('novus_pytils.utils.console.print_colored')
    def test_print_error(self, mock_print_colored):
        """Test print_error function."""
        print_error("Error message")
        
        mock_print_colored.assert_called_once_with("✗ Error message", ColorCode.RED)
    
    @patch('novus_pytils.utils.console.print_colored')
    def test_print_warning(self, mock_print_colored):
        """Test print_warning function."""
        print_warning("Warning message")
        
        mock_print_colored.assert_called_once_with("⚠ Warning message", ColorCode.YELLOW)
    
    @patch('novus_pytils.utils.console.print_colored')
    def test_print_info(self, mock_print_colored):
        """Test print_info function."""
        print_info("Info message")
        
        mock_print_colored.assert_called_once_with("ℹ Info message", ColorCode.BLUE)


class TestPrintTable:
    """Test print_table function."""
    
    @patch('builtins.print')
    def test_print_table_basic(self, mock_print):
        """Test basic table printing."""
        headers = ["Name", "Age", "City"]
        rows = [
            ["Alice", "30", "New York"],
            ["Bob", "25", "London"],
            ["Charlie", "35", "Paris"]
        ]
        
        print_table(headers, rows)
        
        # Check that print was called multiple times (header, separator, rows)
        assert mock_print.call_count >= 5
    
    @patch('builtins.print')
    def test_print_table_with_alignment(self, mock_print):
        """Test table printing with custom alignment."""
        headers = ["Name", "Age", "Score"]
        rows = [["Alice", "30", "95.5"]]
        alignments = ["left", "center", "right"]
        
        print_table(headers, rows, alignments=alignments)
        
        mock_print.assert_called()
    
    @patch('builtins.print')
    def test_print_table_empty_rows(self, mock_print):
        """Test table printing with empty rows."""
        headers = ["Column1", "Column2"]
        rows = []
        
        print_table(headers, rows)
        
        # Should still print headers
        mock_print.assert_called()
    
    @patch('builtins.print')
    def test_print_table_with_colors(self, mock_print):
        """Test table printing with colors."""
        headers = ["Status", "Message"]
        rows = [["Success", "Operation completed"]]
        
        print_table(headers, rows, header_color=ColorCode.BLUE)
        
        mock_print.assert_called()


class TestPrintProgressBar:
    """Test print_progress_bar function."""
    
    @patch('builtins.print')
    def test_print_progress_bar_basic(self, mock_print):
        """Test basic progress bar printing."""
        print_progress_bar(50, 100, "Processing")
        
        mock_print.assert_called()
        call_args = mock_print.call_args[0][0]
        assert "Processing" in call_args
        assert "50%" in call_args
    
    @patch('builtins.print')
    def test_print_progress_bar_complete(self, mock_print):
        """Test progress bar at 100%."""
        print_progress_bar(100, 100, "Complete")
        
        mock_print.assert_called()
        call_args = mock_print.call_args[0][0]
        assert "100%" in call_args
    
    @patch('builtins.print')
    def test_print_progress_bar_zero_total(self, mock_print):
        """Test progress bar with zero total."""
        print_progress_bar(0, 0, "Empty")
        
        mock_print.assert_called()
        call_args = mock_print.call_args[0][0]
        assert "0%" in call_args
    
    @patch('builtins.print')
    def test_print_progress_bar_custom_width(self, mock_print):
        """Test progress bar with custom width."""
        print_progress_bar(25, 100, "Loading", width=20)
        
        mock_print.assert_called()
        call_args = mock_print.call_args[0][0]
        assert "25%" in call_args


class TestUserInteraction:
    """Test user interaction functions."""
    
    @patch('builtins.input')
    def test_confirm_action_yes(self, mock_input):
        """Test confirm_action with yes response."""
        mock_input.return_value = 'y'
        
        result = confirm_action("Are you sure?")
        
        assert result is True
        mock_input.assert_called_once()
    
    @patch('builtins.input')
    def test_confirm_action_no(self, mock_input):
        """Test confirm_action with no response."""
        mock_input.return_value = 'n'
        
        result = confirm_action("Are you sure?")
        
        assert result is False
        mock_input.assert_called_once()
    
    @patch('builtins.input')
    def test_confirm_action_default_yes(self, mock_input):
        """Test confirm_action with empty input and default yes."""
        mock_input.return_value = ''
        
        result = confirm_action("Continue?", default=True)
        
        assert result is True
    
    @patch('builtins.input')
    def test_confirm_action_default_no(self, mock_input):
        """Test confirm_action with empty input and default no."""
        mock_input.return_value = ''
        
        result = confirm_action("Continue?", default=False)
        
        assert result is False
    
    @patch('builtins.input')
    def test_confirm_action_invalid_then_valid(self, mock_input):
        """Test confirm_action with invalid input followed by valid."""
        mock_input.side_effect = ['maybe', 'invalid', 'y']
        
        result = confirm_action("Are you sure?")
        
        assert result is True
        assert mock_input.call_count == 3
    
    @patch('builtins.input')
    def test_get_user_input_basic(self, mock_input):
        """Test get_user_input basic functionality."""
        mock_input.return_value = 'user response'
        
        result = get_user_input("Enter something: ")
        
        assert result == 'user response'
        mock_input.assert_called_once_with("Enter something: ")
    
    @patch('builtins.input')
    def test_get_user_input_with_default(self, mock_input):
        """Test get_user_input with default value."""
        mock_input.return_value = ''
        
        result = get_user_input("Enter name: ", default="Anonymous")
        
        assert result == "Anonymous"
    
    @patch('builtins.input')
    def test_get_user_input_with_validation(self, mock_input):
        """Test get_user_input with validation function."""
        mock_input.side_effect = ['invalid', '42']
        
        def validate_number(value):
            try:
                int(value)
                return True
            except ValueError:
                return False
        
        result = get_user_input("Enter number: ", validator=validate_number)
        
        assert result == '42'
        assert mock_input.call_count == 2
    
    @patch('builtins.input')
    def test_get_user_input_required(self, mock_input):
        """Test get_user_input with required input."""
        mock_input.side_effect = ['', '  ', 'valid input']
        
        result = get_user_input("Required field: ", required=True)
        
        assert result == 'valid input'
        assert mock_input.call_count == 3


class TestScreenControl:
    """Test screen control functions."""
    
    @patch('builtins.print')
    def test_clear_screen_ansi(self, mock_print):
        """Test clear_screen with ANSI escape codes."""
        clear_screen(method='ansi')
        
        mock_print.assert_called_once_with('\\033[2J\\033[H', end='')
    
    @patch('os.system')
    def test_clear_screen_system_windows(self, mock_system):
        """Test clear_screen with system command on Windows."""
        with patch('platform.system', return_value='Windows'):
            clear_screen(method='system')
        
        mock_system.assert_called_once_with('cls')
    
    @patch('os.system')
    def test_clear_screen_system_unix(self, mock_system):
        """Test clear_screen with system command on Unix."""
        with patch('platform.system', return_value='Linux'):
            clear_screen(method='system')
        
        mock_system.assert_called_once_with('clear')
    
    @patch('builtins.print')
    def test_move_cursor(self, mock_print):
        """Test move_cursor function."""
        move_cursor(10, 20)
        
        mock_print.assert_called_once_with('\\033[20;10H', end='')
    
    @patch('builtins.print')
    def test_move_cursor_home(self, mock_print):
        """Test move_cursor to home position."""
        move_cursor(1, 1)
        
        mock_print.assert_called_once_with('\\033[1;1H', end='')


class TestEnvironmentDetection:
    """Test environment detection functionality."""
    
    def test_colors_enabled_detection(self):
        """Test color support detection."""
        # This test might vary based on environment
        # Just check that the detection doesn't crash
        with patch('novus_pytils.utils.console._detect_color_support') as mock_detect:
            mock_detect.return_value = True
            from novus_pytils.console import COLORS_ENABLED
            assert isinstance(COLORS_ENABLED, bool)
    
    @patch('sys.stdout.isatty')
    @patch('os.environ.get')
    def test_color_support_detection_tty_colorterm(self, mock_env_get, mock_isatty):
        """Test color support detection with TTY and COLORTERM."""
        mock_isatty.return_value = True
        mock_env_get.side_effect = lambda key, default=None: 'truecolor' if key == 'COLORTERM' else default
        
        from novus_pytils.console import _detect_color_support
        assert _detect_color_support() is True
    
    @patch('sys.stdout.isatty')
    def test_color_support_detection_no_tty(self, mock_isatty):
        """Test color support detection without TTY."""
        mock_isatty.return_value = False
        
        from novus_pytils.console import _detect_color_support
        assert _detect_color_support() is False