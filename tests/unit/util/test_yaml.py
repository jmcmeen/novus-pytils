"""Unit tests for config.yaml module."""
import pytest
from unittest.mock import patch, mock_open
import yaml

from novus_pytils.utils.yaml import (
    load_config, save_config, get_config_value, set_config_value,
    validate_config, merge_configs
)


class TestLoadConfig:
    """Test load_config function."""
    
    @patch('novus_pytils.utils.yaml.file_exists')
    @patch('builtins.open', new_callable=mock_open, read_data='key: value\nnum: 42')
    @patch('yaml.safe_load')
    def test_load_config_success(self, mock_yaml_load, mock_file, mock_file_exists):
        """Test successful config loading."""
        mock_file_exists.return_value = True
        mock_yaml_load.return_value = {'key': 'value', 'num': 42}
        
        result = load_config('config.yaml')
        
        assert result == {'key': 'value', 'num': 42}
        mock_file.assert_called_once_with('config.yaml', 'r')
        mock_yaml_load.assert_called_once()
    
    @patch('os.path.exists')
    def test_load_config_file_not_exists(self, mock_exists):
        """Test loading non-existent config file."""
        mock_exists.return_value = False
        
        with pytest.raises(FileNotFoundError):
            load_config('nonexistent.yaml')
    
    @patch('novus_pytils.utils.yaml.file_exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('yaml.safe_load')
    def test_load_config_yaml_error(self, mock_yaml_load, mock_file, mock_file_exists):
        """Test config loading with YAML error."""
        mock_file_exists.return_value = True
        mock_yaml_load.side_effect = yaml.YAMLError("Invalid YAML")
        
        with pytest.raises(yaml.YAMLError):
            load_config('config.yaml')


class TestSaveConfig:
    """Test save_config function."""
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('yaml.dump')
    def test_save_config_success(self, mock_yaml_dump, mock_file):
        """Test successful config saving."""
        config_data = {'key': 'value', 'num': 42}
        
        save_config(config_data, 'config.yaml')
        
        mock_file.assert_called_once_with('config.yaml', 'w')
        mock_yaml_dump.assert_called_once()
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('yaml.dump')
    def test_save_config_with_indent(self, mock_yaml_dump, mock_file):
        """Test config saving with custom indent."""
        config_data = {'key': 'value'}
        
        save_config(config_data, 'config.yaml', indent=4)
        
        mock_yaml_dump.assert_called_once()
        call_args = mock_yaml_dump.call_args
        assert call_args[1]['indent'] == 4


class TestConfigValues:
    """Test config value getter/setter functions."""
    
    def test_get_config_value_exists(self):
        """Test getting existing config value."""
        config = {'section': {'key': 'value', 'num': 42}}
        
        result = get_config_value(config, 'section.key')
        assert result == 'value'
        
        result = get_config_value(config, 'section.num')
        assert result == 42
    
    def test_get_config_value_not_exists(self):
        """Test getting non-existent config value."""
        config = {'section': {'key': 'value'}}
        
        result = get_config_value(config, 'section.nonexistent')
        assert result is None
        
        result = get_config_value(config, 'section.nonexistent', 'default')
        assert result == 'default'
    
    def test_get_config_value_nested(self):
        """Test getting nested config value."""
        config = {'a': {'b': {'c': 'deep_value'}}}
        
        result = get_config_value(config, 'a.b.c')
        assert result == 'deep_value'
    
    def test_set_config_value_new(self):
        """Test setting new config value."""
        config = {}
        
        set_config_value(config, 'section.key', 'value')
        
        assert config == {'section': {'key': 'value'}}
    
    def test_set_config_value_existing(self):
        """Test updating existing config value."""
        config = {'section': {'key': 'old_value'}}
        
        set_config_value(config, 'section.key', 'new_value')
        
        assert config['section']['key'] == 'new_value'
    
    def test_set_config_value_nested(self):
        """Test setting nested config value."""
        config = {}
        
        set_config_value(config, 'a.b.c', 'deep_value')
        
        assert config == {'a': {'b': {'c': 'deep_value'}}}


class TestValidateConfig:
    """Test validate_config function."""
    
    def test_validate_config_valid(self):
        """Test validating valid config."""
        config = {
            'file_operations': {
                'default_quality': 95,
                'max_file_size': 1000000
            },
            'api': {
                'host': '0.0.0.0',
                'port': 8000
            }
        }
        
        result = validate_config(config)
        assert result is True
    
    def test_validate_config_invalid_quality(self):
        """Test validating config with invalid quality."""
        config = {
            'file_operations': {
                'default_quality': 150  # Invalid: > 100
            }
        }
        
        result = validate_config(config)
        assert result is False
    
    def test_validate_config_invalid_port(self):
        """Test validating config with invalid port."""
        config = {
            'api': {
                'port': 70000  # Invalid: > 65535
            }
        }
        
        result = validate_config(config)
        assert result is False
    
    def test_validate_config_missing_required(self):
        """Test validating config with missing required fields."""
        config = {}
        
        result = validate_config(config, required_fields=['file_operations.default_quality'])
        assert result is False


class TestMergeConfigs:
    """Test merge_configs function."""
    
    def test_merge_configs_basic(self):
        """Test basic config merging."""
        base = {'a': 1, 'b': 2}
        override = {'b': 3, 'c': 4}
        
        result = merge_configs(base, override)
        
        assert result == {'a': 1, 'b': 3, 'c': 4}
    
    def test_merge_configs_nested(self):
        """Test nested config merging."""
        base = {
            'section1': {'key1': 'value1', 'key2': 'value2'},
            'section2': {'key3': 'value3'}
        }
        override = {
            'section1': {'key2': 'new_value2', 'key4': 'value4'},
            'section3': {'key5': 'value5'}
        }
        
        result = merge_configs(base, override)
        
        expected = {
            'section1': {'key1': 'value1', 'key2': 'new_value2', 'key4': 'value4'},
            'section2': {'key3': 'value3'},
            'section3': {'key5': 'value5'}
        }
        assert result == expected
    
    def test_merge_configs_preserve_base(self):
        """Test that merge doesn't modify base config."""
        base = {'a': 1}
        override = {'b': 2}
        original_base = base.copy()
        
        result = merge_configs(base, override)
        
        assert base == original_base
        assert result == {'a': 1, 'b': 2}


