"""Unit tests for utils.lists module."""
import pytest

from novus_pytils.utils.lists import (
    flatten_list, remove_duplicates, chunk_list, filter_list,
    sort_list_of_dicts, group_by_key, find_in_list, list_intersection,
    list_union, list_difference, rotate_list, partition_list,
    merge_sorted_lists, get_list_statistics
)


class TestFlattenList:
    """Test flatten_list function."""
    
    def test_flatten_simple_nested_list(self):
        """Test flattening simple nested lists."""
        nested = [[1, 2], [3, 4], [5, 6]]
        result = flatten_list(nested)
        assert result == [1, 2, 3, 4, 5, 6]
    
    def test_flatten_deeply_nested_list(self):
        """Test flattening deeply nested lists."""
        nested = [1, [2, [3, [4, 5]], 6], 7]
        result = flatten_list(nested)
        assert result == [1, 2, 3, 4, 5, 6, 7]
    
    def test_flatten_empty_list(self):
        """Test flattening empty list."""
        result = flatten_list([])
        assert result == []
    
    def test_flatten_already_flat_list(self):
        """Test flattening already flat list."""
        flat = [1, 2, 3, 4, 5]
        result = flatten_list(flat)
        assert result == [1, 2, 3, 4, 5]
    
    def test_flatten_mixed_types(self):
        """Test flattening list with mixed types."""
        nested = [1, ['a', 'b'], [True, False], [3.14]]
        result = flatten_list(nested)
        assert result == [1, 'a', 'b', True, False, 3.14]
    
    def test_flatten_with_empty_sublists(self):
        """Test flattening list containing empty sublists."""
        nested = [1, [], [2, 3], [], [4]]
        result = flatten_list(nested)
        assert result == [1, 2, 3, 4]


class TestRemoveDuplicates:
    """Test remove_duplicates function."""
    
    def test_remove_duplicates_basic(self):
        """Test basic duplicate removal."""
        input_list = [1, 2, 2, 3, 3, 3, 4]
        result = remove_duplicates(input_list)
        assert result == [1, 2, 3, 4]
    
    def test_remove_duplicates_preserve_order(self):
        """Test that order is preserved when removing duplicates."""
        input_list = [3, 1, 2, 1, 3, 2]
        result = remove_duplicates(input_list)
        assert result == [3, 1, 2]
    
    def test_remove_duplicates_empty_list(self):
        """Test removing duplicates from empty list."""
        result = remove_duplicates([])
        assert result == []
    
    def test_remove_duplicates_no_duplicates(self):
        """Test removing duplicates when there are none."""
        input_list = [1, 2, 3, 4, 5]
        result = remove_duplicates(input_list)
        assert result == [1, 2, 3, 4, 5]
    
    def test_remove_duplicates_strings(self):
        """Test removing duplicates from string list."""
        input_list = ['apple', 'banana', 'apple', 'cherry', 'banana']
        result = remove_duplicates(input_list)
        assert result == ['apple', 'banana', 'cherry']
    
    def test_remove_duplicates_mixed_types(self):
        """Test removing duplicates with mixed types."""
        input_list = [1, '1', 1, 2, '2', 2]
        result = remove_duplicates(input_list)
        assert result == [1, '1', 2, '2']


class TestChunkList:
    """Test chunk_list function."""
    
    def test_chunk_list_basic(self):
        """Test basic list chunking."""
        input_list = [1, 2, 3, 4, 5, 6]
        result = chunk_list(input_list, 2)
        assert result == [[1, 2], [3, 4], [5, 6]]
    
    def test_chunk_list_uneven(self):
        """Test chunking list with uneven division."""
        input_list = [1, 2, 3, 4, 5]
        result = chunk_list(input_list, 2)
        assert result == [[1, 2], [3, 4], [5]]
    
    def test_chunk_list_larger_chunk_size(self):
        """Test chunking with chunk size larger than list."""
        input_list = [1, 2, 3]
        result = chunk_list(input_list, 5)
        assert result == [[1, 2, 3]]
    
    def test_chunk_list_empty(self):
        """Test chunking empty list."""
        result = chunk_list([], 3)
        assert result == []
    
    def test_chunk_list_chunk_size_one(self):
        """Test chunking with chunk size of 1."""
        input_list = [1, 2, 3]
        result = chunk_list(input_list, 1)
        assert result == [[1], [2], [3]]
    
    def test_chunk_list_invalid_chunk_size(self):
        """Test chunking with invalid chunk size."""
        input_list = [1, 2, 3]
        with pytest.raises(ValueError):
            chunk_list(input_list, 0)
        with pytest.raises(ValueError):
            chunk_list(input_list, -1)


class TestFilterList:
    """Test filter_list function."""
    
    def test_filter_list_basic(self):
        """Test basic list filtering."""
        input_list = [1, 2, 3, 4, 5, 6]
        result = filter_list(input_list, lambda x: x % 2 == 0)
        assert result == [2, 4, 6]
    
    def test_filter_list_strings(self):
        """Test filtering string list."""
        input_list = ['apple', 'banana', 'cherry', 'apricot']
        result = filter_list(input_list, lambda x: x.startswith('a'))
        assert result == ['apple', 'apricot']
    
    def test_filter_list_empty(self):
        """Test filtering empty list."""
        result = filter_list([], lambda x: True)
        assert result == []
    
    def test_filter_list_no_matches(self):
        """Test filtering with no matches."""
        input_list = [1, 3, 5, 7, 9]
        result = filter_list(input_list, lambda x: x % 2 == 0)
        assert result == []
    
    def test_filter_list_all_matches(self):
        """Test filtering where all items match."""
        input_list = [2, 4, 6, 8]
        result = filter_list(input_list, lambda x: x % 2 == 0)
        assert result == [2, 4, 6, 8]


class TestSortListOfDicts:
    """Test sort_list_of_dicts function."""
    
    def test_sort_by_key_ascending(self):
        """Test sorting list of dicts by key in ascending order."""
        input_list = [
            {'name': 'Alice', 'age': 30},
            {'name': 'Bob', 'age': 25},
            {'name': 'Charlie', 'age': 35}
        ]
        result = sort_list_of_dicts(input_list, 'age')
        expected = [
            {'name': 'Bob', 'age': 25},
            {'name': 'Alice', 'age': 30},
            {'name': 'Charlie', 'age': 35}
        ]
        assert result == expected
    
    def test_sort_by_key_descending(self):
        """Test sorting list of dicts by key in descending order."""
        input_list = [
            {'name': 'Alice', 'age': 30},
            {'name': 'Bob', 'age': 25},
            {'name': 'Charlie', 'age': 35}
        ]
        result = sort_list_of_dicts(input_list, 'age', reverse=True)
        expected = [
            {'name': 'Charlie', 'age': 35},
            {'name': 'Alice', 'age': 30},
            {'name': 'Bob', 'age': 25}
        ]
        assert result == expected
    
    def test_sort_by_string_key(self):
        """Test sorting by string key."""
        input_list = [
            {'name': 'Charlie', 'age': 35},
            {'name': 'Alice', 'age': 30},
            {'name': 'Bob', 'age': 25}
        ]
        result = sort_list_of_dicts(input_list, 'name')
        expected = [
            {'name': 'Alice', 'age': 30},
            {'name': 'Bob', 'age': 25},
            {'name': 'Charlie', 'age': 35}
        ]
        assert result == expected
    
    def test_sort_missing_key(self):
        """Test sorting when some dicts are missing the key."""
        input_list = [
            {'name': 'Alice', 'age': 30},
            {'name': 'Bob'},  # Missing age
            {'name': 'Charlie', 'age': 25}
        ]
        with pytest.raises(KeyError):
            sort_list_of_dicts(input_list, 'age')
    
    def test_sort_empty_list(self):
        """Test sorting empty list."""
        result = sort_list_of_dicts([], 'any_key')
        assert result == []


class TestGroupByKey:
    """Test group_by_key function."""
    
    def test_group_by_key_basic(self):
        """Test basic grouping by key."""
        input_list = [
            {'category': 'fruit', 'name': 'apple'},
            {'category': 'vegetable', 'name': 'carrot'},
            {'category': 'fruit', 'name': 'banana'},
            {'category': 'vegetable', 'name': 'broccoli'}
        ]
        result = group_by_key(input_list, 'category')
        
        assert 'fruit' in result
        assert 'vegetable' in result
        assert len(result['fruit']) == 2
        assert len(result['vegetable']) == 2
    
    def test_group_by_key_single_group(self):
        """Test grouping where all items have same key value."""
        input_list = [
            {'type': 'A', 'value': 1},
            {'type': 'A', 'value': 2},
            {'type': 'A', 'value': 3}
        ]
        result = group_by_key(input_list, 'type')
        
        assert len(result) == 1
        assert 'A' in result
        assert len(result['A']) == 3
    
    def test_group_by_key_empty_list(self):
        """Test grouping empty list."""
        result = group_by_key([], 'any_key')
        assert result == {}
    
    def test_group_by_key_missing_key(self):
        """Test grouping when some items missing the key."""
        input_list = [
            {'category': 'A', 'value': 1},
            {'value': 2},  # Missing category
            {'category': 'B', 'value': 3}
        ]
        with pytest.raises(KeyError):
            group_by_key(input_list, 'category')


class TestFindInList:
    """Test find_in_list function."""
    
    def test_find_in_list_basic(self):
        """Test basic item finding in list."""
        input_list = [1, 2, 3, 4, 5]
        assert find_in_list(input_list, lambda x: x == 3) == 3
        assert find_in_list(input_list, lambda x: x > 3) == 4
    
    def test_find_in_list_not_found(self):
        """Test finding item that doesn't exist."""
        input_list = [1, 2, 3, 4, 5]
        assert find_in_list(input_list, lambda x: x > 10) is None
    
    def test_find_in_list_first_match(self):
        """Test that first matching item is returned."""
        input_list = [1, 2, 3, 2, 4]
        assert find_in_list(input_list, lambda x: x == 2) == 2
    
    def test_find_in_list_empty(self):
        """Test finding in empty list."""
        assert find_in_list([], lambda x: True) is None
    
    def test_find_in_list_complex_condition(self):
        """Test finding with complex condition."""
        input_list = [
            {'name': 'Alice', 'age': 30},
            {'name': 'Bob', 'age': 25},
            {'name': 'Charlie', 'age': 35}
        ]
        result = find_in_list(input_list, lambda x: x['age'] > 30)
        assert result == {'name': 'Charlie', 'age': 35}


class TestListOperations:
    """Test list set operations."""
    
    def test_list_intersection(self):
        """Test list intersection."""
        list1 = [1, 2, 3, 4, 5]
        list2 = [3, 4, 5, 6, 7]
        result = list_intersection(list1, list2)
        assert set(result) == {3, 4, 5}
    
    def test_list_intersection_no_common(self):
        """Test intersection with no common elements."""
        list1 = [1, 2, 3]
        list2 = [4, 5, 6]
        result = list_intersection(list1, list2)
        assert result == []
    
    def test_list_union(self):
        """Test list union."""
        list1 = [1, 2, 3]
        list2 = [3, 4, 5]
        result = list_union(list1, list2)
        assert set(result) == {1, 2, 3, 4, 5}
    
    def test_list_union_duplicates(self):
        """Test that union removes duplicates."""
        list1 = [1, 2, 2, 3]
        list2 = [3, 3, 4, 5]
        result = list_union(list1, list2)
        assert set(result) == {1, 2, 3, 4, 5}
    
    def test_list_difference(self):
        """Test list difference."""
        list1 = [1, 2, 3, 4, 5]
        list2 = [3, 4, 5]
        result = list_difference(list1, list2)
        assert set(result) == {1, 2}
    
    def test_list_difference_no_difference(self):
        """Test difference when lists are identical."""
        list1 = [1, 2, 3]
        list2 = [1, 2, 3]
        result = list_difference(list1, list2)
        assert result == []


class TestAdvancedListOperations:
    """Test advanced list operations."""
    
    def test_rotate_list_right(self):
        """Test rotating list to the right."""
        input_list = [1, 2, 3, 4, 5]
        result = rotate_list(input_list, 2)
        assert result == [4, 5, 1, 2, 3]
    
    def test_rotate_list_left(self):
        """Test rotating list to the left."""
        input_list = [1, 2, 3, 4, 5]
        result = rotate_list(input_list, -2)
        assert result == [3, 4, 5, 1, 2]
    
    def test_rotate_list_full_rotation(self):
        """Test full rotation (should return original list)."""
        input_list = [1, 2, 3, 4, 5]
        result = rotate_list(input_list, 5)
        assert result == input_list
    
    def test_rotate_empty_list(self):
        """Test rotating empty list."""
        result = rotate_list([], 3)
        assert result == []
    
    def test_partition_list(self):
        """Test partitioning list based on condition."""
        input_list = [1, 2, 3, 4, 5, 6]
        true_list, false_list = partition_list(input_list, lambda x: x % 2 == 0)
        
        assert true_list == [2, 4, 6]
        assert false_list == [1, 3, 5]
    
    def test_partition_list_all_true(self):
        """Test partitioning where all items match condition."""
        input_list = [2, 4, 6, 8]
        true_list, false_list = partition_list(input_list, lambda x: x % 2 == 0)
        
        assert true_list == [2, 4, 6, 8]
        assert false_list == []
    
    def test_partition_list_all_false(self):
        """Test partitioning where no items match condition."""
        input_list = [1, 3, 5, 7]
        true_list, false_list = partition_list(input_list, lambda x: x % 2 == 0)
        
        assert true_list == []
        assert false_list == [1, 3, 5, 7]
    
    def test_merge_sorted_lists(self):
        """Test merging sorted lists."""
        list1 = [1, 3, 5, 7]
        list2 = [2, 4, 6, 8]
        result = merge_sorted_lists(list1, list2)
        assert result == [1, 2, 3, 4, 5, 6, 7, 8]
    
    def test_merge_sorted_lists_different_lengths(self):
        """Test merging sorted lists of different lengths."""
        list1 = [1, 5, 9]
        list2 = [2, 3, 4, 6, 7, 8]
        result = merge_sorted_lists(list1, list2)
        assert result == [1, 2, 3, 4, 5, 6, 7, 8, 9]
    
    def test_merge_sorted_lists_empty(self):
        """Test merging with empty lists."""
        list1 = [1, 2, 3]
        list2 = []
        result = merge_sorted_lists(list1, list2)
        assert result == [1, 2, 3]
        
        result = merge_sorted_lists([], list1)
        assert result == [1, 2, 3]


class TestGetListStatistics:
    """Test get_list_statistics function."""
    
    def test_get_statistics_numeric_list(self):
        """Test statistics for numeric list."""
        input_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        stats = get_list_statistics(input_list)
        
        assert stats['count'] == 10
        assert stats['sum'] == 55
        assert stats['mean'] == 5.5
        assert stats['min'] == 1
        assert stats['max'] == 10
        assert stats['median'] == 5.5
    
    def test_get_statistics_single_element(self):
        """Test statistics for single element list."""
        input_list = [42]
        stats = get_list_statistics(input_list)
        
        assert stats['count'] == 1
        assert stats['sum'] == 42
        assert stats['mean'] == 42
        assert stats['min'] == 42
        assert stats['max'] == 42
        assert stats['median'] == 42
    
    def test_get_statistics_empty_list(self):
        """Test statistics for empty list."""
        stats = get_list_statistics([])
        
        assert stats['count'] == 0
        assert stats['sum'] == 0
        assert stats['mean'] is None
        assert stats['min'] is None
        assert stats['max'] is None
        assert stats['median'] is None
    
    def test_get_statistics_odd_length(self):
        """Test statistics for odd-length list."""
        input_list = [1, 2, 3, 4, 5]
        stats = get_list_statistics(input_list)
        
        assert stats['median'] == 3
    
    def test_get_statistics_even_length(self):
        """Test statistics for even-length list."""
        input_list = [1, 2, 3, 4]
        stats = get_list_statistics(input_list)
        
        assert stats['median'] == 2.5
    
    def test_get_statistics_non_numeric(self):
        """Test statistics for non-numeric list."""
        input_list = ['a', 'b', 'c']
        with pytest.raises((TypeError, ValueError)):
            get_list_statistics(input_list)