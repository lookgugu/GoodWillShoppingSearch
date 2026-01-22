"""Tests for GoodWillSearch class."""

import pytest
import json
from unittest.mock import patch, MagicMock
from requests.exceptions import Timeout, ConnectionError, HTTPError
from GoodWillShoppingSearch.models.goodwillsearch import GoodWillSearch
from GoodWillShoppingSearch.models.goodwillproduct import GoodWillProduct
from GoodWillShoppingSearch.enums.goodwillcategories import GoodWillCategories
from GoodWillShoppingSearch.enums.goodwilllocations import GoodWillLocations
from GoodWillShoppingSearch.enums.goodwillsearchgallery import GoodWillSearchGallery


class TestGoodWillSearchInitialization:
    """Test GoodWillSearch initialization."""

    def test_init_with_timezone_only(self, local_timezone):
        """Test initialization with just timezone."""
        search = GoodWillSearch(local_timezone)
        assert search.time_zone == local_timezone
        assert search.url == "https://www.shopgoodwill.com/Listings"

    def test_init_with_json_file(self, local_timezone, sample_json_config):
        """Test initialization with JSON config file."""
        search = GoodWillSearch(local_timezone, sample_json_config)
        assert search.keyword_search == "t480"  # QueryItem lowercases all string values
        assert search.categories == "7"

    def test_default_search_parameters(self, local_timezone):
        """Test that default search parameters are set."""
        search = GoodWillSearch(local_timezone)
        # Check some default values
        assert search.low_price == "0"
        assert search.high_price == "999999"
        assert search.page_size == "40"


class TestJSONConfigLoading:
    """Test loading search parameters from JSON files."""

    def test_load_minimal_json(self, local_timezone, sample_json_config_minimal):
        """Test loading minimal JSON with only keyword."""
        search = GoodWillSearch(local_timezone, sample_json_config_minimal)
        assert search.keyword_search == "laptop"

    def test_load_full_json(self, local_timezone, sample_json_config_full):
        """Test loading comprehensive JSON config."""
        search = GoodWillSearch(local_timezone, sample_json_config_full)
        assert search.keyword_search == "computer"
        assert search.categories == "7"
        assert search.low_price == "100"
        assert search.high_price == "1000"

    def test_json_with_price_range(self, local_timezone, sample_json_config):
        """Test JSON loading with price range."""
        search = GoodWillSearch(local_timezone, sample_json_config)
        assert search.low_price == "50"
        assert search.high_price == "500"

    def test_invalid_json_file(self, local_timezone, invalid_json_file):
        """Test that invalid JSON raises error."""
        with pytest.raises(json.JSONDecodeError):
            GoodWillSearch(local_timezone, invalid_json_file)

    def test_nonexistent_json_file(self, local_timezone):
        """Test that nonexistent file raises error."""
        with pytest.raises(FileNotFoundError):
            GoodWillSearch(local_timezone, "/nonexistent/file.json")


class TestQueryStringGeneration:
    """Test query string construction."""

    def test_empty_keyword_search(self, local_timezone):
        """Test query string with empty keyword."""
        search = GoodWillSearch(local_timezone)
        query = search.query_string()
        assert query.startswith("?")
        assert "st=" in query  # keyword search parameter

    def test_query_string_with_keyword(self, local_timezone):
        """Test query string with keyword search."""
        search = GoodWillSearch(local_timezone)
        search.keyword_search = "laptop"
        query = search.query_string()
        assert "st=laptop" in query

    def test_query_string_with_category(self, local_timezone):
        """Test query string with category."""
        search = GoodWillSearch(local_timezone)
        search.categories = GoodWillCategories.ComputersAndElectronics
        query = search.query_string()
        assert "c=7" in query

    def test_query_string_with_price_range(self, local_timezone):
        """Test query string with price range."""
        search = GoodWillSearch(local_timezone)
        search.low_price = 50
        search.high_price = 500
        query = search.query_string()
        assert "lp=50" in query
        assert "hp=500" in query

    def test_query_string_with_boolean_flags(self, local_timezone):
        """Test query string with boolean parameters."""
        search = GoodWillSearch(local_timezone)
        search.show_buy_now_only = True
        query = search.query_string()
        assert "sbn=true" in query

    def test_query_string_format(self, local_timezone):
        """Test query string has proper format."""
        search = GoodWillSearch(local_timezone)
        query = search.query_string()
        # Should start with ?
        assert query.startswith("?")
        # Should have key=value pairs separated by &
        assert "&" in query
        # Should not end with &
        assert not query.endswith("&")


class TestSearchURLGeneration:
    """Test search URL construction."""

    def test_search_url_base(self, local_timezone):
        """Test search URL contains base URL."""
        search = GoodWillSearch(local_timezone)
        url = search.search_url()
        assert url.startswith("https://www.shopgoodwill.com/Listings")

    def test_search_url_includes_query_string(self, local_timezone):
        """Test search URL includes query parameters."""
        search = GoodWillSearch(local_timezone)
        search.keyword_search = "test"
        url = search.search_url()
        assert "?" in url
        assert "st=test" in url

    def test_search_url_complete(self, local_timezone):
        """Test complete search URL format."""
        search = GoodWillSearch(local_timezone)
        search.keyword_search = "laptop"
        search.categories = GoodWillCategories.ComputersAndElectronics
        url = search.search_url()
        assert "https://www.shopgoodwill.com/Listings?" in url
        assert "st=laptop" in url
        assert "c=7" in url


class TestSearchExecution:
    """Test search execution with mocked HTTP requests."""

    @patch('GoodWillShoppingSearch.models.goodwillsearch.requests.get')
    def test_successful_search(self, mock_get, local_timezone, sample_search_response_html):
        """Test successful search returns product list."""
        # Setup mock
        mock_response = MagicMock()
        mock_response.text = sample_search_response_html
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Execute search
        search = GoodWillSearch(local_timezone)
        results = search.search("laptop")

        # Assertions
        assert len(results) == 3
        assert all(isinstance(p, GoodWillProduct) for p in results)
        mock_get.assert_called_once()

    @patch('GoodWillShoppingSearch.models.goodwillsearch.requests.get')
    def test_empty_search_results(self, mock_get, local_timezone, sample_empty_search_response):
        """Test search with no results."""
        # Setup mock
        mock_response = MagicMock()
        mock_response.text = sample_empty_search_response
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Execute search
        search = GoodWillSearch(local_timezone)
        results = search.search("nonexistent")

        # Should return empty list
        assert len(results) == 0
        assert isinstance(results, list)

    @patch('GoodWillShoppingSearch.models.goodwillsearch.requests.get')
    def test_search_sets_keyword(self, mock_get, local_timezone, sample_search_response_html):
        """Test that search() sets the keyword_search property."""
        # Setup mock
        mock_response = MagicMock()
        mock_response.text = sample_search_response_html
        mock_get.return_value = mock_response

        # Execute search
        search = GoodWillSearch(local_timezone)
        search.search("test_keyword")

        # Keyword should be set
        assert search.keyword_search == "test_keyword"

    @patch('GoodWillShoppingSearch.models.goodwillsearch.requests.get')
    def test_search_calls_correct_url(self, mock_get, local_timezone, sample_search_response_html):
        """Test that search calls the correct URL."""
        # Setup mock
        mock_response = MagicMock()
        mock_response.text = sample_search_response_html
        mock_get.return_value = mock_response

        # Execute search
        search = GoodWillSearch(local_timezone)
        search.search("laptop")

        # Verify URL called
        called_url = mock_get.call_args[0][0]
        assert "https://www.shopgoodwill.com/Listings" in called_url
        assert "st=laptop" in called_url


class TestSearchMultiple:
    """Test searching with multiple keywords."""

    @patch('GoodWillShoppingSearch.models.goodwillsearch.requests.get')
    def test_search_multiple_keywords(self, mock_get, local_timezone, sample_search_response_html):
        """Test searching with multiple keywords."""
        # Setup mock
        mock_response = MagicMock()
        mock_response.text = sample_search_response_html
        mock_get.return_value = mock_response

        # Execute multiple searches
        search = GoodWillSearch(local_timezone)
        keywords = {"laptop", "computer"}
        results = search.search_multiple(keywords)

        # Should call search twice and combine results
        assert mock_get.call_count == 2
        # Results should be combined
        assert len(results) > 0


class TestSearchErrorHandling:
    """Test error handling during search (tests expected behavior, not implemented)."""

    @patch('GoodWillShoppingSearch.models.goodwillsearch.requests.get')
    def test_timeout_error(self, mock_get, local_timezone):
        """Test handling of connection timeout."""
        mock_get.side_effect = Timeout("Connection timed out")

        search = GoodWillSearch(local_timezone)
        # Currently no error handling - this will raise
        # Future: should handle gracefully
        with pytest.raises(Timeout):
            search.search("laptop")

    @patch('GoodWillShoppingSearch.models.goodwillsearch.requests.get')
    def test_connection_error(self, mock_get, local_timezone):
        """Test handling of connection error."""
        mock_get.side_effect = ConnectionError("Network unreachable")

        search = GoodWillSearch(local_timezone)
        # Currently no error handling - this will raise
        # Future: should handle gracefully
        with pytest.raises(ConnectionError):
            search.search("laptop")


class TestPropertyAccessors:
    """Test property getters and setters."""

    def test_keyword_search_property(self, local_timezone):
        """Test keyword_search getter/setter."""
        search = GoodWillSearch(local_timezone)
        search.keyword_search = "TEST"
        # Should be lowercased by QueryItem
        assert search.keyword_search == "test"

    def test_categories_property(self, local_timezone):
        """Test categories getter/setter."""
        search = GoodWillSearch(local_timezone)
        search.categories = GoodWillCategories.ComputersAndElectronics
        assert search.categories == "7"

    def test_price_properties(self, local_timezone):
        """Test price getter/setter."""
        search = GoodWillSearch(local_timezone)
        search.low_price = 100
        search.high_price = 500
        assert search.low_price == "100"
        assert search.high_price == "500"

    def test_boolean_properties(self, local_timezone):
        """Test boolean property getter/setter."""
        search = GoodWillSearch(local_timezone)
        search.show_buy_now_only = True
        assert search.show_buy_now_only == "true"

        search.show_buy_now_only = False
        assert search.show_buy_now_only == "false"


class TestPrintSearchParams:
    """Test search parameter printing."""

    def test_print_search_params_no_error(self, local_timezone, capsys):
        """Test that print_search_params runs without error."""
        search = GoodWillSearch(local_timezone)
        search.keyword_search = "laptop"
        search.print_search_params()

        captured = capsys.readouterr()
        # Should print something
        assert len(captured.out) > 0
        # Should contain keyword search
        assert "laptop" in captured.out


class TestAllPropertySetters:
    """Comprehensive tests for all property setters to increase coverage."""

    def test_search_gallery_setter(self, local_timezone):
        """Test search_gallery property setter."""
        search = GoodWillSearch(local_timezone)
        search.search_gallery = GoodWillSearchGallery.EndingToday
        assert search.search_gallery == "Ending"

    def test_good_will_location_setter(self, local_timezone):
        """Test good_will_location property setter."""
        search = GoodWillSearch(local_timezone)
        search.good_will_location = GoodWillLocations.CA_Los_Angeles
        assert search.good_will_location == "78"

    def test_show_pick_up_only_setter(self, local_timezone):
        """Test show_pick_up_only property setter."""
        search = GoodWillSearch(local_timezone)
        search.show_pick_up_only = True
        assert search.show_pick_up_only == "true"

    def test_hide_pick_up_only_setter(self, local_timezone):
        """Test hide_pick_up_only property setter."""
        search = GoodWillSearch(local_timezone)
        search.hide_pick_up_only = True
        assert search.hide_pick_up_only == "true"

    def test_show_one_cent_ship_only_setter(self, local_timezone):
        """Test show_one_cent_ship_only property setter."""
        search = GoodWillSearch(local_timezone)
        search.show_one_cent_ship_only = True
        assert search.show_one_cent_ship_only == "true"

    def test_search_description_setter(self, local_timezone):
        """Test search_description property setter."""
        search = GoodWillSearch(local_timezone)
        search.search_description = True
        assert search.search_description == "true"

    def test_show_closed_auctions_setter(self, local_timezone):
        """Test show_closed_auctions property setter."""
        search = GoodWillSearch(local_timezone)
        search.show_closed_auctions = True
        assert search.show_closed_auctions == "true"

    def test_closed_auction_end_date_setter(self, local_timezone):
        """Test closed_auction_end_date property setter."""
        from datetime import datetime
        search = GoodWillSearch(local_timezone)
        test_date = datetime(2026, 1, 1)
        search.closed_auction_end_date = test_date
        assert search.closed_auction_end_date == str(test_date).lower()

    def test_day_back_setter(self, local_timezone):
        """Test day_back property setter."""
        search = GoodWillSearch(local_timezone)
        search.day_back = 7
        assert search.day_back == "7"

    def test_search_canada_setter(self, local_timezone):
        """Test search_canada property setter."""
        search = GoodWillSearch(local_timezone)
        search.search_canada = True
        assert search.search_canada == "true"

    def test_search_international_setter(self, local_timezone):
        """Test search_international property setter."""
        search = GoodWillSearch(local_timezone)
        search.search_international = True
        assert search.search_international == "true"

    def test_page_number_setter(self, local_timezone):
        """Test page_number property setter."""
        search = GoodWillSearch(local_timezone)
        search.page_number = 2
        assert search.page_number == "2"

    def test_page_size_setter(self, local_timezone):
        """Test page_size property setter."""
        search = GoodWillSearch(local_timezone)
        search.page_size = 100
        assert search.page_size == "100"

    def test_short_description_setter(self, local_timezone):
        """Test short_description property setter."""
        search = GoodWillSearch(local_timezone)
        search.short_description = True
        assert search.short_description == "true"

    def test_saved_search_id_setter(self, local_timezone):
        """Test saved_search_id property setter."""
        search = GoodWillSearch(local_timezone)
        search.saved_search_id = 123
        assert search.saved_search_id == "123"

    def test_use_buyer_preferences_setter(self, local_timezone):
        """Test use_buyer_preferences property setter."""
        search = GoodWillSearch(local_timezone)
        search.use_buyer_preferences = False
        assert search.use_buyer_preferences == "false"


class TestComprehensiveJSONLoading:
    """Test JSON loading with all possible parameters."""

    def test_json_with_all_parameters(self, local_timezone, tmp_path):
        """Test loading JSON with all possible parameters."""
        from datetime import datetime
        config = {
            "keyword_search": "test",
            "search_gallery": "New",
            "categories": "7",
            "good_will_location": "78",
            "low_price": "10",
            "high_price": "100",
            "show_buy_now_only": True,
            "show_pick_up_only": True,
            "hide_pick_up_only": False,
            "show_one_cent_ship_only": True,
            "search_description": True,
            "show_closed_auctions": False,
            "closed_auction_end_date": "2026-01-01",
            "day_back": 30,
            "search_canada": False,
            "search_international": False,
            "field_order": "1",
            "page_number": 1,
            "page_size": 40,
            "short_description": False,
            "saved_search_id": 999
        }
        json_file = tmp_path / "comprehensive_search.json"
        json_file.write_text(json.dumps(config, indent=2))

        search = GoodWillSearch(local_timezone, str(json_file))

        # Verify all parameters loaded correctly
        assert search.keyword_search == "test"
        assert search.search_gallery == "New"
        assert search.categories == "7"
        assert search.good_will_location == "78"
        assert search.low_price == "10"
        assert search.high_price == "100"
        assert search.show_buy_now_only == "true"
        assert search.show_pick_up_only == "true"
        assert search.hide_pick_up_only == "false"
        assert search.show_one_cent_ship_only == "true"
        assert search.search_description == "true"
        assert search.show_closed_auctions == "false"
        assert search.day_back == "30"
        assert search.search_canada == "false"
        assert search.search_international == "false"
        assert search.page_number == "1"
        assert search.page_size == "40"
        assert search.short_description == "false"
        assert search.saved_search_id == "999"
