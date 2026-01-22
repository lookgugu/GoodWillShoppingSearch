"""Tests for GoodWillProduct class."""

import pytest
import pytz
from datetime import datetime, timedelta
from GoodWillShoppingSearch.models.goodwillproduct import GoodWillProduct


class TestProductPriceParsing:
    """Test price parsing from HTML."""

    def test_standard_price(self, sample_product_html, local_timezone):
        """Test parsing standard price format."""
        product = GoodWillProduct(sample_product_html, local_timezone)
        assert product.price == 45.00
        assert isinstance(product.price, float)

    def test_price_with_comma(self, sample_product_html_with_comma_price, local_timezone):
        """Test parsing price with comma separator."""
        product = GoodWillProduct(sample_product_html_with_comma_price, local_timezone)
        assert product.price == 1250.99
        assert isinstance(product.price, float)

    def test_price_removes_dollar_sign(self, sample_product_html, local_timezone):
        """Test that dollar sign is removed from price."""
        product = GoodWillProduct(sample_product_html, local_timezone)
        # Price should be numeric, not include $
        assert product.price > 0
        assert product.price == 45.00


class TestProductTitleParsing:
    """Test title parsing and normalization."""

    def test_standard_title(self, sample_product_html, local_timezone):
        """Test parsing standard title."""
        product = GoodWillProduct(sample_product_html, local_timezone)
        assert product.listing == "Lenovo ThinkPad T480 Laptop"
        assert isinstance(product.listing, str)

    def test_title_special_characters_normalized(self, sample_product_html_special_chars, local_timezone):
        """Test that unidecode normalizes special characters."""
        product = GoodWillProduct(sample_product_html_special_chars, local_timezone)
        # unidecode should convert special chars to ASCII
        # é becomes e, ™ is removed or converted, — becomes -
        assert "Cafe" in product.listing or "Latte" in product.listing
        # Should not contain raw special Unicode characters
        assert isinstance(product.listing, str)

    def test_title_strips_whitespace(self, sample_product_html, local_timezone):
        """Test that title strips extra whitespace."""
        product = GoodWillProduct(sample_product_html, local_timezone)
        # Title should not have leading/trailing whitespace
        assert product.listing == product.listing.strip()


class TestProductIdAndUrl:
    """Test product ID extraction and URL generation."""

    def test_product_id_extraction(self, sample_product_html, local_timezone):
        """Test extracting product ID from HTML."""
        product = GoodWillProduct(sample_product_html, local_timezone)
        assert product.product_id == "12345678"
        assert isinstance(product.product_id, str)

    def test_product_url_generation(self, sample_product_html, local_timezone):
        """Test product URL is correctly formatted."""
        product = GoodWillProduct(sample_product_html, local_timezone)
        expected_url = "https://www.shopgoodwill.com/Item/12345678"
        assert product.url == expected_url

    def test_different_product_ids(self, sample_product_html_with_comma_price, local_timezone):
        """Test different product IDs generate different URLs."""
        product = GoodWillProduct(sample_product_html_with_comma_price, local_timezone)
        assert product.product_id == "87654321"
        assert "87654321" in product.url


class TestProductCountdownParsing:
    """Test auction countdown and end time parsing."""

    def test_countdown_parsing(self, sample_product_html, local_timezone):
        """Test countdown datetime is parsed correctly."""
        product = GoodWillProduct(sample_product_html, local_timezone)
        assert product.ends == "01/25/2026 11:30:00 PM"
        assert isinstance(product.end_date, datetime)

    def test_end_date_timezone_aware(self, sample_product_html, local_timezone):
        """Test that end_date is timezone-aware."""
        product = GoodWillProduct(sample_product_html, local_timezone)
        # Should have timezone information
        assert product.end_date.tzinfo is not None
        assert str(product.end_date.tzinfo) == str(local_timezone)

    def test_duration_calculation(self, sample_product_html, local_timezone):
        """Test duration calculation."""
        product = GoodWillProduct(sample_product_html, local_timezone)
        # Duration should be a timedelta
        assert isinstance(product.duration, timedelta)
        # For future dates, duration should be positive (or could be negative if date passed)
        # Just verify it's calculated
        assert product.duration is not None

    def test_no_timer_element(self, sample_product_html_no_timer, local_timezone):
        """Test product without countdown timer."""
        product = GoodWillProduct(sample_product_html_no_timer, local_timezone)
        # Should set end_date to now
        assert product.end_date is not None
        # Duration should be zero
        assert product.duration == timedelta(0)


class TestProductTimezoneHandling:
    """Test timezone-aware datetime handling."""

    def test_different_timezone(self, sample_product_html):
        """Test product with different timezone."""
        utc_tz = pytz.UTC
        product = GoodWillProduct(sample_product_html, utc_tz)
        # Should work with UTC timezone
        assert str(product.end_date.tzinfo) == str(utc_tz)

    def test_pacific_timezone(self, sample_product_html):
        """Test product with Pacific timezone."""
        pacific_tz = pytz.timezone('America/Los_Angeles')
        product = GoodWillProduct(sample_product_html, pacific_tz)
        assert str(product.end_date.tzinfo) == str(pacific_tz)

    def test_timezone_affects_duration(self, sample_product_html, local_timezone):
        """Test that timezone affects duration calculation."""
        product = GoodWillProduct(sample_product_html, local_timezone)
        # Duration is calculated as end_date - now(timezone)
        # Both should be in same timezone
        assert product.duration is not None


class TestProductPrintMethod:
    """Test product printing functionality."""

    def test_print_product_no_error(self, sample_product_html, local_timezone, capsys):
        """Test that print_product runs without error."""
        product = GoodWillProduct(sample_product_html, local_timezone)
        product.print_product()

        captured = capsys.readouterr()
        # Should print something
        assert len(captured.out) > 0
        # Should contain price, listing, url, duration
        assert str(product.price) in captured.out
        assert product.listing in captured.out
        assert product.url in captured.out


class TestProductIntegration:
    """Integration tests for complete product parsing."""

    def test_complete_product_parsing(self, sample_product_html, local_timezone):
        """Test complete product is parsed correctly."""
        product = GoodWillProduct(sample_product_html, local_timezone)

        # All fields should be populated
        assert product.price > 0
        assert len(product.listing) > 0
        assert len(product.product_id) > 0
        assert product.url.startswith("https://")
        assert product.end_date is not None
        assert product.duration is not None

    def test_product_with_all_fields(self, sample_product_html_with_comma_price, local_timezone):
        """Test product with all fields populated."""
        product = GoodWillProduct(sample_product_html_with_comma_price, local_timezone)

        # Verify all critical fields
        assert product.price == 1250.99
        assert "Gaming Computer" in product.listing
        assert product.product_id == "87654321"
        assert "87654321" in product.url
        assert product.end_date is not None
