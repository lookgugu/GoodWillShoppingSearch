"""Tests for enum utility functions."""

import pytest
from GoodWillShoppingSearch.utils.enum_utils import (
    find_category,
    find_location,
    list_categories,
    list_locations
)
from GoodWillShoppingSearch.enums.goodwillcategories import GoodWillCategories
from GoodWillShoppingSearch.enums.goodwilllocations import GoodWillLocations


class TestFindCategory:
    """Test find_category function."""

    def test_find_category_by_id(self):
        """Test finding category by numeric ID."""
        result = find_category("30")
        assert result == GoodWillCategories.Computers
        assert result.value == "30"

    def test_find_category_by_exact_name(self):
        """Test finding category by exact name match."""
        result = find_category("Computers")
        assert result == GoodWillCategories.Computers

    def test_find_category_case_insensitive(self):
        """Test finding category with different case."""
        result = find_category("computers")
        assert result == GoodWillCategories.Computers

    def test_find_category_with_spaces(self):
        """Test finding category with spaces in name."""
        result = find_category("Computers And Electronics")
        assert result == GoodWillCategories.ComputersAndElectronics

    def test_find_category_fuzzy_match(self):
        """Test fuzzy matching for category names."""
        # "laptop" should fuzzy match to something related to computers
        result = find_category("Compute")
        assert result == GoodWillCategories.Computers

    def test_find_category_not_found(self):
        """Test error when category not found."""
        with pytest.raises(ValueError, match="Category .* not found"):
            find_category("NonexistentCategory12345")

    def test_find_category_ambiguous(self):
        """Test error when category match is ambiguous."""
        # This test is difficult to trigger reliably as it depends on
        # fuzzy matching cutoff and enum names. Skip for now.
        pytest.skip("Ambiguous matching is difficult to trigger reliably")

    def test_find_category_with_underscores(self):
        """Test finding category with underscores instead of spaces."""
        result = find_category("Computers_And_Electronics")
        assert result == GoodWillCategories.ComputersAndElectronics


class TestFindLocation:
    """Test find_location function."""

    def test_find_location_by_id(self):
        """Test finding location by numeric ID."""
        result = find_location("43")
        assert result == GoodWillLocations.TX_Austin
        assert result.value == "43"

    def test_find_location_by_exact_name(self):
        """Test finding location by exact name match."""
        result = find_location("TX_Austin")
        assert result == GoodWillLocations.TX_Austin

    def test_find_location_case_insensitive(self):
        """Test finding location with different case."""
        result = find_location("tx_austin")
        assert result == GoodWillLocations.TX_Austin

    def test_find_location_fuzzy_match(self):
        """Test fuzzy matching for location names."""
        result = find_location("Austin")
        assert result == GoodWillLocations.TX_Austin

    def test_find_location_not_found(self):
        """Test error when location not found."""
        with pytest.raises(ValueError, match="Location .* not found"):
            find_location("NonexistentLocation12345")

    def test_find_location_ambiguous(self):
        """Test error when location match is ambiguous."""
        # This test is difficult to trigger reliably as it depends on
        # fuzzy matching cutoff and enum names. Skip for now.
        pytest.skip("Ambiguous matching is difficult to trigger reliably")

    def test_find_location_without_state_prefix(self):
        """Test finding location without state prefix."""
        # This tests fuzzy matching capability
        result = find_location("Austin")
        assert "Austin" in result.name


class TestListCategories:
    """Test list_categories function."""

    def test_list_categories_all(self):
        """Test listing all categories."""
        categories = list_categories()
        assert len(categories) > 0
        assert all(isinstance(item, tuple) for item in categories)
        assert all(len(item) == 2 for item in categories)
        # Verify it's sorted by name
        names = [cat[0] for cat in categories]
        assert names == sorted(names)

    def test_list_categories_excludes_empty(self):
        """Test that Empty category is excluded."""
        categories = list_categories()
        names = [cat[0] for cat in categories]
        assert "Empty" not in names

    def test_list_categories_with_filter(self):
        """Test filtering categories by text."""
        categories = list_categories("Computer")
        assert len(categories) > 0
        # All results should contain "Computer" in name
        assert all("Computer" in cat[0] for cat in categories)

    def test_list_categories_filter_case_insensitive(self):
        """Test that filtering is case-insensitive."""
        lower_results = list_categories("computer")
        upper_results = list_categories("COMPUTER")
        assert len(lower_results) == len(upper_results)

    def test_list_categories_filter_no_matches(self):
        """Test filtering with no matches returns empty list."""
        categories = list_categories("XYZ123456789")
        assert len(categories) == 0

    def test_list_categories_format(self):
        """Test that each category has correct format (name, id)."""
        categories = list_categories()
        for name, id_val in categories:
            assert isinstance(name, str)
            assert isinstance(id_val, str)
            assert len(name) > 0
            assert len(id_val) > 0


class TestListLocations:
    """Test list_locations function."""

    def test_list_locations_all(self):
        """Test listing all locations."""
        locations = list_locations()
        assert len(locations) > 0
        assert all(isinstance(item, tuple) for item in locations)
        assert all(len(item) == 2 for item in locations)
        # Verify it's sorted by name
        names = [loc[0] for loc in locations]
        assert names == sorted(names)

    def test_list_locations_excludes_empty(self):
        """Test that Empty location is excluded."""
        locations = list_locations()
        names = [loc[0] for loc in locations]
        assert "Empty" not in names

    def test_list_locations_with_filter(self):
        """Test filtering locations by text."""
        locations = list_locations("TX")
        assert len(locations) > 0
        # All results should contain "TX" in name
        assert all("TX" in loc[0] for loc in locations)

    def test_list_locations_filter_case_insensitive(self):
        """Test that filtering is case-insensitive."""
        lower_results = list_locations("tx")
        upper_results = list_locations("TX")
        assert len(lower_results) == len(upper_results)

    def test_list_locations_filter_no_matches(self):
        """Test filtering with no matches returns empty list."""
        locations = list_locations("XYZ123456789")
        assert len(locations) == 0

    def test_list_locations_format(self):
        """Test that each location has correct format (name, id)."""
        locations = list_locations()
        for name, id_val in locations:
            assert isinstance(name, str)
            assert isinstance(id_val, str)
            assert len(name) > 0
            assert len(id_val) > 0

    def test_list_locations_contains_texas_austin(self):
        """Test that TX_Austin location exists in list."""
        locations = list_locations()
        tx_austin = [loc for loc in locations if "Austin" in loc[0]]
        assert len(tx_austin) > 0


class TestIntegration:
    """Test integration scenarios with find and list functions."""

    def test_find_category_from_list_results(self):
        """Test that categories from list can be found by ID."""
        all_categories = list_categories()
        # Pick first category and try to find it by ID
        first_name, first_id = all_categories[0]
        result = find_category(first_id)
        assert result.value == first_id

    def test_find_location_from_list_results(self):
        """Test that locations from list can be found by ID."""
        all_locations = list_locations()
        # Pick first location and try to find it by ID
        first_name, first_id = all_locations[0]
        result = find_location(first_id)
        assert result.value == first_id

    def test_filter_then_find(self):
        """Test filtering then finding a specific item."""
        # Filter for computer categories
        computer_cats = list_categories("Computer")
        assert len(computer_cats) > 0
        # Find the first one by name
        first_name, first_id = computer_cats[0]
        result = find_category(first_name)
        assert result.value == first_id
