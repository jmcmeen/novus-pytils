"""Unit tests for file_operations.text module."""
import pytest
import pandas as pd

from novus_pytils.file_operations.text import to_frame, write_csv


class TestDataFrameOperations:
    """Test DataFrame operations."""
    
    def test_to_frame_from_list_of_lists(self, sample_csv_data):
        """Test creating DataFrame from list of lists."""
        df = to_frame(sample_csv_data)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == len(sample_csv_data)
        assert len(df.columns) == len(sample_csv_data[0])
    
    def test_to_frame_from_dict(self):
        """Test creating DataFrame from dictionary."""
        data = {
            'name': ['Alice', 'Bob', 'Charlie'],
            'age': [25, 30, 35],
            'city': ['New York', 'San Francisco', 'Chicago']
        }
        
        df = to_frame(data)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert list(df.columns) == ['name', 'age', 'city']
        assert df['name'].tolist() == ['Alice', 'Bob', 'Charlie']
    
    def test_to_frame_from_list_of_dicts(self):
        """Test creating DataFrame from list of dictionaries."""
        data = [
            {'name': 'Alice', 'age': 25, 'city': 'New York'},
            {'name': 'Bob', 'age': 30, 'city': 'San Francisco'},
            {'name': 'Charlie', 'age': 35, 'city': 'Chicago'}
        ]
        
        df = to_frame(data)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert 'name' in df.columns
        assert 'age' in df.columns
        assert 'city' in df.columns
    
    def test_to_frame_empty_data(self):
        """Test creating DataFrame from empty data."""
        df = to_frame([])
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0
    
    def test_to_frame_single_row(self):
        """Test creating DataFrame from single row."""
        data = [['Alice', 25, 'New York']]
        
        df = to_frame(data)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1
        assert len(df.columns) == 3


class TestCSVOperations:
    """Test CSV file operations."""
    
    def test_write_csv_basic(self, temp_dir, sample_csv_data):
        """Test basic CSV writing."""
        df = pd.DataFrame(sample_csv_data[1:], columns=sample_csv_data[0])
        output_path = temp_dir / "output.csv"
        
        write_csv(df, str(output_path))
        
        assert output_path.exists()
        
        # Read back and verify
        read_df = pd.read_csv(output_path)
        assert len(read_df) == len(df)
        assert list(read_df.columns) == list(df.columns)
    
    def test_write_csv_with_index(self, temp_dir):
        """Test CSV writing behavior with index."""
        data = {
            'col1': [1, 2, 3],
            'col2': ['a', 'b', 'c']
        }
        df = pd.DataFrame(data)
        output_path = temp_dir / "with_index.csv"
        
        write_csv(df, str(output_path))
        
        # Read back and check that index was not included
        content = output_path.read_text()
        lines = content.strip().split('\n')
        
        # First line should be header
        assert lines[0] == 'col1,col2'
        # Data lines should not start with index numbers
        assert lines[1] == '1,a'
        assert lines[2] == '2,b'
        assert lines[3] == '3,c'
    
    def test_write_csv_empty_dataframe(self, temp_dir):
        """Test writing empty DataFrame to CSV."""
        df = pd.DataFrame()
        output_path = temp_dir / "empty.csv"
        
        write_csv(df, str(output_path))
        
        assert output_path.exists()
        content = output_path.read_text().strip()
        assert content == ""  # Empty DataFrame should create empty file
    
    def test_write_csv_single_column(self, temp_dir):
        """Test writing single-column DataFrame."""
        df = pd.DataFrame({'single_col': [1, 2, 3, 4, 5]})
        output_path = temp_dir / "single_column.csv"
        
        write_csv(df, str(output_path))
        
        assert output_path.exists()
        
        # Verify content
        read_df = pd.read_csv(output_path)
        assert len(read_df.columns) == 1
        assert read_df.columns[0] == 'single_col'
        assert read_df['single_col'].tolist() == [1, 2, 3, 4, 5]
    
    def test_write_csv_special_characters(self, temp_dir):
        """Test writing CSV with special characters."""
        data = {
            'name': ['Alice, Jr.', 'Bob "Bobby"', 'Charlie\nNewline'],
            'description': ['Has comma', 'Has "quotes"', 'Has\nnewline']
        }
        df = pd.DataFrame(data)
        output_path = temp_dir / "special_chars.csv"
        
        write_csv(df, str(output_path))
        
        assert output_path.exists()
        
        # Read back and verify data integrity
        read_df = pd.read_csv(output_path)
        assert len(read_df) == 3
        assert 'Alice, Jr.' in read_df['name'].values
        assert 'Bob "Bobby"' in read_df['name'].values
    
    def test_write_csv_numeric_data(self, temp_dir):
        """Test writing CSV with various numeric data types."""
        data = {
            'integers': [1, 2, 3],
            'floats': [1.1, 2.2, 3.3],
            'mixed': [1, 2.5, 3]
        }
        df = pd.DataFrame(data)
        output_path = temp_dir / "numeric.csv"
        
        write_csv(df, str(output_path))
        
        assert output_path.exists()
        
        # Read back and verify
        read_df = pd.read_csv(output_path)
        assert len(read_df) == 3
        assert read_df['integers'].tolist() == [1, 2, 3]
        assert abs(read_df['floats'].iloc[0] - 1.1) < 0.001
    
    def test_write_csv_with_nulls(self, temp_dir):
        """Test writing CSV with null values."""
        import numpy as np
        
        data = {
            'col1': [1, 2, np.nan, 4],
            'col2': ['a', None, 'c', 'd']
        }
        df = pd.DataFrame(data)
        output_path = temp_dir / "with_nulls.csv"
        
        write_csv(df, str(output_path))
        
        assert output_path.exists()
        
        # Read back and verify null handling
        read_df = pd.read_csv(output_path)
        assert len(read_df) == 4
        assert pd.isna(read_df['col1'].iloc[2])
    
    def test_write_csv_large_dataset(self, temp_dir):
        """Test writing larger CSV dataset."""
        import numpy as np
        
        # Create larger dataset
        size = 1000
        data = {
            'id': range(size),
            'value': np.random.rand(size),
            'category': [f'cat_{i % 5}' for i in range(size)]
        }
        df = pd.DataFrame(data)
        output_path = temp_dir / "large.csv"
        
        write_csv(df, str(output_path))
        
        assert output_path.exists()
        
        # Verify file size is reasonable
        file_size = output_path.stat().st_size
        assert file_size > 1000  # Should be at least 1KB for 1000 rows
        
        # Read back and verify
        read_df = pd.read_csv(output_path)
        assert len(read_df) == size


class TestIntegrationWithToFrame:
    """Test integration between to_frame and write_csv."""
    
    def test_list_to_frame_to_csv(self, temp_dir):
        """Test full pipeline: list -> DataFrame -> CSV."""
        raw_data = [
            ['Product', 'Price', 'Quantity'],
            ['Apple', 1.50, 100],
            ['Banana', 0.75, 150],
            ['Orange', 2.00, 75]
        ]
        
        # Convert to DataFrame
        df = to_frame(raw_data[1:])  # Skip header row
        df.columns = raw_data[0]     # Set header as columns
        
        # Write to CSV
        output_path = temp_dir / "pipeline_test.csv"
        write_csv(df, str(output_path))
        
        assert output_path.exists()
        
        # Verify final result
        final_df = pd.read_csv(output_path)
        assert list(final_df.columns) == ['Product', 'Price', 'Quantity']
        assert len(final_df) == 3
        assert final_df['Product'].iloc[0] == 'Apple'
    
    def test_dict_to_frame_to_csv(self, temp_dir):
        """Test pipeline: dict -> DataFrame -> CSV."""
        raw_data = {
            'student': ['Alice', 'Bob', 'Charlie'],
            'grade': [85, 92, 78],
            'subject': ['Math', 'Science', 'English']
        }
        
        # Convert to DataFrame and write
        df = to_frame(raw_data)
        output_path = temp_dir / "dict_pipeline.csv"
        write_csv(df, str(output_path))
        
        assert output_path.exists()
        
        # Verify
        final_df = pd.read_csv(output_path)
        assert set(final_df.columns) == set(raw_data.keys())
        assert len(final_df) == 3


class TestErrorHandling:
    """Test error handling in text operations."""
    
    def test_write_csv_invalid_path(self, temp_dir):
        """Test error handling for invalid file path."""
        df = pd.DataFrame({'col': [1, 2, 3]})
        
        # Try to write to a directory that doesn't exist
        invalid_path = temp_dir / "nonexistent" / "subdir" / "file.csv"
        
        with pytest.raises(FileNotFoundError):
            write_csv(df, str(invalid_path))
    
    def test_to_frame_invalid_data(self):
        """Test error handling for invalid data in to_frame."""
        # This should not raise an error but might create an empty or unexpected DataFrame
        try:
            df = to_frame(None)
            # pandas might handle this differently in different versions
            assert isinstance(df, pd.DataFrame)
        except (ValueError, TypeError):
            # This is also acceptable behavior
            pass
    
    def test_write_csv_permission_error(self, temp_dir):
        """Test handling of permission errors (simulated)."""
        df = pd.DataFrame({'col': [1, 2, 3]})
        
        # Create a file and make it read-only (on systems that support it)
        output_path = temp_dir / "readonly.csv"
        output_path.touch()
        
        try:
            # Make file read-only
            output_path.chmod(0o444)
            
            # This might raise a PermissionError on some systems
            write_csv(df, str(output_path))
            
        except PermissionError:
            # Expected on systems with strict file permissions
            pass
        finally:
            # Clean up - restore write permissions
            try:
                output_path.chmod(0o644)
            except (OSError, AttributeError):
                pass