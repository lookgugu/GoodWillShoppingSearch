"""Tests for output formatting functions."""

import pytest
import json
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from GoodWillShoppingSearch.formatters.output import format_products


class TestFormatProductsEmpty:
    """Test format_products with empty product lists."""

    @patch('builtins.print')
    def test_format_empty_list_table(self, mock_print):
        """Test formatting empty list with table format."""
        format_products([], 'table')
        mock_print.assert_called_once_with("No results found.")

    @patch('builtins.print')
    def test_format_empty_list_json(self, mock_print):
        """Test formatting empty list with JSON format."""
        format_products([], 'json')
        mock_print.assert_called_once_with("No results found.")

    @patch('builtins.print')
    def test_format_empty_list_quiet(self, mock_print):
        """Test formatting empty list with quiet format."""
        format_products([], 'quiet')
        mock_print.assert_called_once_with("No results found.")


class TestFormatTableOutput:
    """Test table format output."""

    def create_mock_product(self, price=45.0, listing="Test Product",
                           product_id="12345678", duration_seconds=3600):
        """Helper to create mock product."""
        mock = Mock()
        mock.price = price
        mock.listing = listing
        mock.product_id = product_id
        mock.url = f"https://www.shopgoodwill.com/Item/{product_id}"

        if duration_seconds is not None:
            mock.duration = timedelta(seconds=duration_seconds)
        else:
            mock.duration = None

        return mock

    @patch('builtins.print')
    def test_format_single_product_table(self, mock_print):
        """Test formatting single product as table."""
        products = [self.create_mock_product()]
        format_products(products, 'table')

        # Check that print was called (for table and total)
        assert mock_print.call_count >= 2

        # Check that the output contains key elements
        all_output = ' '.join(str(call[0][0]) for call in mock_print.call_args_list)
        assert "$45.00" in all_output
        assert "Test Product" in all_output
        assert "Total results: 1" in all_output

    @patch('builtins.print')
    def test_format_multiple_products_table(self, mock_print):
        """Test formatting multiple products as table."""
        products = [
            self.create_mock_product(price=45.0, listing="Product 1", product_id="111"),
            self.create_mock_product(price=125.0, listing="Product 2", product_id="222"),
            self.create_mock_product(price=85.5, listing="Product 3", product_id="333")
        ]
        format_products(products, 'table')

        all_output = ' '.join(str(call[0][0]) for call in mock_print.call_args_list)
        assert "Total results: 3" in all_output
        assert "$45.00" in all_output
        assert "$125.00" in all_output
        assert "$85.50" in all_output

    @patch('builtins.print')
    def test_format_long_listing_truncated(self, mock_print):
        """Test that long listing titles are truncated."""
        long_title = "A" * 100  # 100 characters
        products = [self.create_mock_product(listing=long_title)]
        format_products(products, 'table')

        all_output = ' '.join(str(call[0][0]) for call in mock_print.call_args_list)
        # Should be truncated to 60 chars + "..."
        assert "..." in all_output

    @patch('builtins.print')
    def test_format_no_duration(self, mock_print):
        """Test formatting product with no duration."""
        products = [self.create_mock_product(duration_seconds=None)]
        format_products(products, 'table')

        all_output = ' '.join(str(call[0][0]) for call in mock_print.call_args_list)
        assert "N/A" in all_output


class TestFormatJSONOutput:
    """Test JSON format output."""

    def create_mock_product(self, price=45.0, listing="Test Product",
                           product_id="12345678", end_date=None, duration_seconds=3600):
        """Helper to create mock product."""
        mock = Mock()
        mock.price = price
        mock.listing = listing
        mock.product_id = product_id
        mock.url = f"https://www.shopgoodwill.com/Item/{product_id}"

        if end_date:
            mock.end_date = end_date
        else:
            mock.end_date = datetime(2026, 1, 25, 23, 30, 0)

        if duration_seconds is not None:
            mock.duration = timedelta(seconds=duration_seconds)
        else:
            mock.duration = None

        return mock

    @patch('builtins.print')
    def test_format_single_product_json(self, mock_print):
        """Test formatting single product as JSON."""
        products = [self.create_mock_product()]
        format_products(products, 'json')

        # Get the printed output
        output = mock_print.call_args[0][0]

        # Parse JSON
        data = json.loads(output)
        assert len(data) == 1
        assert data[0]['price'] == 45.0
        assert data[0]['listing'] == "Test Product"
        assert data[0]['product_id'] == "12345678"
        assert 'url' in data[0]
        assert 'end_date' in data[0]
        assert 'duration_seconds' in data[0]

    @patch('builtins.print')
    def test_format_multiple_products_json(self, mock_print):
        """Test formatting multiple products as JSON."""
        products = [
            self.create_mock_product(price=45.0, listing="Product 1", product_id="111"),
            self.create_mock_product(price=125.0, listing="Product 2", product_id="222"),
            self.create_mock_product(price=85.5, listing="Product 3", product_id="333")
        ]
        format_products(products, 'json')

        output = mock_print.call_args[0][0]
        data = json.loads(output)

        assert len(data) == 3
        assert data[0]['price'] == 45.0
        assert data[1]['price'] == 125.0
        assert data[2]['price'] == 85.5

    @patch('builtins.print')
    def test_format_json_with_null_end_date(self, mock_print):
        """Test JSON formatting with null end date."""
        mock = Mock()
        mock.price = 45.0
        mock.listing = "Test"
        mock.product_id = "123"
        mock.url = "https://example.com"
        mock.end_date = None
        mock.duration = None

        format_products([mock], 'json')

        output = mock_print.call_args[0][0]
        data = json.loads(output)

        assert data[0]['end_date'] is None
        assert data[0]['duration_seconds'] == 0

    @patch('builtins.print')
    def test_format_json_structure(self, mock_print):
        """Test JSON output has correct structure."""
        products = [self.create_mock_product()]
        format_products(products, 'json')

        output = mock_print.call_args[0][0]
        data = json.loads(output)

        # Verify all required fields present
        required_fields = ['price', 'listing', 'product_id', 'url', 'end_date', 'duration_seconds']
        for field in required_fields:
            assert field in data[0]


class TestFormatQuietOutput:
    """Test quiet format output."""

    def create_mock_product(self, product_id="12345678"):
        """Helper to create mock product."""
        mock = Mock()
        mock.url = f"https://www.shopgoodwill.com/Item/{product_id}"
        mock.price = 45.0
        mock.listing = "Test"
        mock.product_id = product_id
        return mock

    @patch('builtins.print')
    def test_format_single_product_quiet(self, mock_print):
        """Test formatting single product in quiet mode."""
        products = [self.create_mock_product()]
        format_products(products, 'quiet')

        mock_print.assert_called_once()
        output = mock_print.call_args[0][0]
        assert output.startswith("https://www.shopgoodwill.com/Item/")

    @patch('builtins.print')
    def test_format_multiple_products_quiet(self, mock_print):
        """Test formatting multiple products in quiet mode."""
        products = [
            self.create_mock_product(product_id="111"),
            self.create_mock_product(product_id="222"),
            self.create_mock_product(product_id="333")
        ]
        format_products(products, 'quiet')

        # Should print one URL per line
        assert mock_print.call_count == 3

        # Verify each call is a URL
        for call in mock_print.call_args_list:
            url = call[0][0]
            assert url.startswith("https://www.shopgoodwill.com/Item/")

    @patch('builtins.print')
    def test_quiet_output_only_urls(self, mock_print):
        """Test that quiet mode only outputs URLs, no other text."""
        products = [self.create_mock_product()]
        format_products(products, 'quiet')

        output = mock_print.call_args[0][0]
        # Should not contain price, title, or other metadata
        assert "$" not in output
        assert "Total" not in output
        assert "results" not in output


class TestFormatDefaultBehavior:
    """Test default format behavior."""

    @patch('builtins.print')
    def test_invalid_format_uses_print_product(self, mock_print):
        """Test that invalid format falls back to print_product."""
        mock_product = Mock()
        mock_product.print_product = Mock()
        mock_product.price = 45.0
        mock_product.listing = "Test"

        format_products([mock_product], 'invalid_format')

        # Should call print_product method on the product
        mock_product.print_product.assert_called_once()

    @patch('builtins.print')
    def test_unspecified_format_uses_print_product(self, mock_print):
        """Test that unspecified format falls back to print_product."""
        mock_product = Mock()
        mock_product.print_product = Mock()
        mock_product.price = 45.0
        mock_product.listing = "Test"

        format_products([mock_product], None)

        mock_product.print_product.assert_called_once()


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    @patch('builtins.print')
    def test_format_with_special_characters(self, mock_print):
        """Test formatting products with special characters in title."""
        mock = Mock()
        mock.price = 25.5
        mock.listing = "Café Latte™ — Test & Product"
        mock.product_id = "123"
        mock.url = "https://example.com/123"
        mock.end_date = None
        mock.duration = None

        # Should not raise errors with special characters
        format_products([mock], 'json')

        output = mock_print.call_args[0][0]
        data = json.loads(output)
        assert "Café Latte™ — Test & Product" in data[0]['listing']

    @patch('builtins.print')
    def test_format_with_very_high_price(self, mock_print):
        """Test formatting products with very high prices."""
        mock = Mock()
        mock.price = 999999.99
        mock.listing = "Expensive Item"
        mock.product_id = "123"
        mock.url = "https://example.com/123"
        mock.duration = timedelta(hours=1)

        format_products([mock], 'table')

        all_output = ' '.join(str(call[0][0]) for call in mock_print.call_args_list)
        assert "999999.99" in all_output

    @patch('builtins.print')
    def test_format_with_zero_price(self, mock_print):
        """Test formatting products with zero price."""
        mock = Mock()
        mock.price = 0.0
        mock.listing = "Free Item"
        mock.product_id = "123"
        mock.url = "https://example.com/123"
        mock.end_date = None
        mock.duration = None

        format_products([mock], 'json')

        output = mock_print.call_args[0][0]
        data = json.loads(output)
        assert data[0]['price'] == 0.0
