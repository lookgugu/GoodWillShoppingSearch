"""Tests for search wrapper functions."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from GoodWillShoppingSearch.utils.search_wrapper import (
    suppress_print_product,
    execute_search,
    execute_search_from_file
)
from GoodWillShoppingSearch.models.goodwillproduct import GoodWillProduct


class TestSuppressPrintProduct:
    """Test suppress_print_product context manager."""

    def test_suppress_restores_original_method(self):
        """Test that original print_product is restored after context."""
        original_method = GoodWillProduct.print_product

        with suppress_print_product():
            # Inside context, method should be replaced
            assert GoodWillProduct.print_product != original_method

        # After context, method should be restored
        assert GoodWillProduct.print_product == original_method

    def test_suppress_replaces_with_noop(self):
        """Test that print_product is replaced with no-op inside context."""
        with suppress_print_product():
            # Create a mock product
            mock_product = Mock(spec=GoodWillProduct)
            # Call the suppressed method (should do nothing)
            GoodWillProduct.print_product(mock_product)
            # No exception should be raised

    def test_suppress_restores_on_exception(self):
        """Test that original method is restored even if exception occurs."""
        original_method = GoodWillProduct.print_product

        try:
            with suppress_print_product():
                raise ValueError("Test exception")
        except ValueError:
            pass

        # Method should still be restored
        assert GoodWillProduct.print_product == original_method


class TestExecuteSearch:
    """Test execute_search function."""

    @patch('GoodWillShoppingSearch.utils.search_wrapper.get_localzone')
    @patch('GoodWillShoppingSearch.utils.search_wrapper.GoodWillSearch')
    def test_execute_search_basic(self, mock_search_class, mock_get_tz):
        """Test basic search execution."""
        # Setup mocks
        mock_tz = Mock()
        mock_get_tz.return_value = mock_tz

        mock_search_instance = Mock()
        mock_products = [Mock(), Mock()]
        mock_search_instance.search.return_value = mock_products
        mock_search_class.return_value = mock_search_instance

        # Execute search
        params = {'keyword_search': 'laptop'}
        result = execute_search(params, suppress_output=True)

        # Verify
        mock_search_class.assert_called_once_with(mock_tz, None)
        mock_search_instance.search_params_by_json.assert_called_once_with(params)
        mock_search_instance.search.assert_called_once_with('laptop')
        assert result == mock_products

    @patch('GoodWillShoppingSearch.utils.search_wrapper.get_localzone')
    @patch('GoodWillShoppingSearch.utils.search_wrapper.GoodWillSearch')
    def test_execute_search_with_params(self, mock_search_class, mock_get_tz):
        """Test search with additional parameters."""
        mock_tz = Mock()
        mock_get_tz.return_value = mock_tz

        mock_search_instance = Mock()
        mock_products = [Mock()]
        mock_search_instance.search.return_value = mock_products
        mock_search_class.return_value = mock_search_instance

        params = {
            'keyword_search': 'computer',
            'categories': '7',
            'low_price': '100',
            'high_price': '500'
        }
        result = execute_search(params, suppress_output=True)

        mock_search_instance.search_params_by_json.assert_called_once_with(params)
        assert result == mock_products

    @patch('GoodWillShoppingSearch.utils.search_wrapper.get_localzone')
    @patch('GoodWillShoppingSearch.utils.search_wrapper.GoodWillSearch')
    def test_execute_search_missing_keyword(self, mock_search_class, mock_get_tz):
        """Test that missing keyword raises ValueError."""
        mock_tz = Mock()
        mock_get_tz.return_value = mock_tz

        params = {'categories': '7'}

        with pytest.raises(ValueError, match="keyword_search is required"):
            execute_search(params, suppress_output=True)

    @patch('GoodWillShoppingSearch.utils.search_wrapper.get_localzone')
    @patch('GoodWillShoppingSearch.utils.search_wrapper.GoodWillSearch')
    def test_execute_search_empty_keyword(self, mock_search_class, mock_get_tz):
        """Test that empty keyword raises ValueError."""
        mock_tz = Mock()
        mock_get_tz.return_value = mock_tz

        params = {'keyword_search': ''}

        with pytest.raises(ValueError, match="keyword_search is required"):
            execute_search(params, suppress_output=True)

    @patch('GoodWillShoppingSearch.utils.search_wrapper.suppress_print_product')
    @patch('GoodWillShoppingSearch.utils.search_wrapper.get_localzone')
    @patch('GoodWillShoppingSearch.utils.search_wrapper.GoodWillSearch')
    def test_execute_search_suppresses_output(self, mock_search_class, mock_get_tz, mock_suppress):
        """Test that output is suppressed when suppress_output=True."""
        mock_tz = Mock()
        mock_get_tz.return_value = mock_tz

        mock_search_instance = Mock()
        mock_products = [Mock()]
        mock_search_instance.search.return_value = mock_products
        mock_search_class.return_value = mock_search_instance

        # Mock suppress_print_product as a context manager
        mock_suppress.return_value.__enter__ = Mock()
        mock_suppress.return_value.__exit__ = Mock()

        params = {'keyword_search': 'laptop'}
        execute_search(params, suppress_output=True)

        # Verify suppress_print_product was called
        mock_suppress.assert_called_once()

    @patch('GoodWillShoppingSearch.utils.search_wrapper.get_localzone')
    @patch('GoodWillShoppingSearch.utils.search_wrapper.GoodWillSearch')
    def test_execute_search_no_suppress(self, mock_search_class, mock_get_tz):
        """Test search without output suppression."""
        mock_tz = Mock()
        mock_get_tz.return_value = mock_tz

        mock_search_instance = Mock()
        mock_products = [Mock()]
        mock_search_instance.search.return_value = mock_products
        mock_search_class.return_value = mock_search_instance

        params = {'keyword_search': 'laptop'}
        result = execute_search(params, suppress_output=False)

        # Should still return products
        assert result == mock_products


class TestExecuteSearchFromFile:
    """Test execute_search_from_file function."""

    @patch('GoodWillShoppingSearch.utils.search_wrapper.get_localzone')
    @patch('GoodWillShoppingSearch.utils.search_wrapper.GoodWillSearch')
    def test_execute_search_from_file_basic(self, mock_search_class, mock_get_tz):
        """Test basic search from file."""
        mock_tz = Mock()
        mock_get_tz.return_value = mock_tz

        mock_search_instance = Mock()
        mock_search_instance.keyword_search = 'laptop'
        mock_products = [Mock(), Mock()]
        mock_search_instance.search.return_value = mock_products
        mock_search_class.return_value = mock_search_instance

        result = execute_search_from_file('/path/to/config.json', suppress_output=True)

        mock_search_class.assert_called_once_with(mock_tz, '/path/to/config.json')
        mock_search_instance.search.assert_called_once_with('laptop')
        assert result == mock_products

    @patch('GoodWillShoppingSearch.utils.search_wrapper.get_localzone')
    @patch('GoodWillShoppingSearch.utils.search_wrapper.GoodWillSearch')
    def test_execute_search_from_file_missing_keyword(self, mock_search_class, mock_get_tz):
        """Test that missing keyword in file raises ValueError."""
        mock_tz = Mock()
        mock_get_tz.return_value = mock_tz

        mock_search_instance = Mock()
        mock_search_instance.keyword_search = None
        mock_search_class.return_value = mock_search_instance

        with pytest.raises(ValueError, match="No keyword_search specified"):
            execute_search_from_file('/path/to/config.json', suppress_output=True)

    @patch('GoodWillShoppingSearch.utils.search_wrapper.get_localzone')
    @patch('GoodWillShoppingSearch.utils.search_wrapper.GoodWillSearch')
    def test_execute_search_from_file_empty_keyword(self, mock_search_class, mock_get_tz):
        """Test that empty keyword in file raises ValueError."""
        mock_tz = Mock()
        mock_get_tz.return_value = mock_tz

        mock_search_instance = Mock()
        mock_search_instance.keyword_search = ''
        mock_search_class.return_value = mock_search_instance

        with pytest.raises(ValueError, match="No keyword_search specified"):
            execute_search_from_file('/path/to/config.json', suppress_output=True)

    @patch('GoodWillShoppingSearch.utils.search_wrapper.suppress_print_product')
    @patch('GoodWillShoppingSearch.utils.search_wrapper.get_localzone')
    @patch('GoodWillShoppingSearch.utils.search_wrapper.GoodWillSearch')
    def test_execute_search_from_file_suppresses_output(self, mock_search_class, mock_get_tz, mock_suppress):
        """Test that output is suppressed when suppress_output=True."""
        mock_tz = Mock()
        mock_get_tz.return_value = mock_tz

        mock_search_instance = Mock()
        mock_search_instance.keyword_search = 'laptop'
        mock_products = [Mock()]
        mock_search_instance.search.return_value = mock_products
        mock_search_class.return_value = mock_search_instance

        mock_suppress.return_value.__enter__ = Mock()
        mock_suppress.return_value.__exit__ = Mock()

        execute_search_from_file('/path/to/config.json', suppress_output=True)

        mock_suppress.assert_called_once()

    @patch('GoodWillShoppingSearch.utils.search_wrapper.get_localzone')
    @patch('GoodWillShoppingSearch.utils.search_wrapper.GoodWillSearch')
    def test_execute_search_from_file_no_suppress(self, mock_search_class, mock_get_tz):
        """Test search from file without output suppression."""
        mock_tz = Mock()
        mock_get_tz.return_value = mock_tz

        mock_search_instance = Mock()
        mock_search_instance.keyword_search = 'laptop'
        mock_products = [Mock()]
        mock_search_instance.search.return_value = mock_products
        mock_search_class.return_value = mock_search_instance

        result = execute_search_from_file('/path/to/config.json', suppress_output=False)

        assert result == mock_products


class TestIntegration:
    """Test integration scenarios."""

    @patch('GoodWillShoppingSearch.utils.search_wrapper.get_localzone')
    @patch('GoodWillShoppingSearch.utils.search_wrapper.GoodWillSearch')
    def test_both_functions_use_same_timezone(self, mock_search_class, mock_get_tz):
        """Test that both functions use get_localzone consistently."""
        mock_tz = Mock()
        mock_get_tz.return_value = mock_tz

        mock_search_instance = Mock()
        mock_search_instance.keyword_search = 'test'
        mock_search_instance.search.return_value = []
        mock_search_class.return_value = mock_search_instance

        # Test execute_search
        execute_search({'keyword_search': 'test'}, suppress_output=True)
        first_call_tz = mock_search_class.call_args[0][0]

        mock_search_class.reset_mock()

        # Test execute_search_from_file
        execute_search_from_file('/path/to/file.json', suppress_output=True)
        second_call_tz = mock_search_class.call_args[0][0]

        assert first_call_tz == second_call_tz == mock_tz

    @patch('GoodWillShoppingSearch.utils.search_wrapper.get_localzone')
    @patch('GoodWillShoppingSearch.utils.search_wrapper.GoodWillSearch')
    def test_execute_search_returns_empty_list(self, mock_search_class, mock_get_tz):
        """Test handling of empty search results."""
        mock_tz = Mock()
        mock_get_tz.return_value = mock_tz

        mock_search_instance = Mock()
        mock_search_instance.search.return_value = []
        mock_search_class.return_value = mock_search_instance

        params = {'keyword_search': 'nonexistent_item_xyz'}
        result = execute_search(params, suppress_output=True)

        assert result == []
        assert len(result) == 0
