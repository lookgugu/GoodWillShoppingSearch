"""Tests for QueryItem class."""

import pytest
from enum import Enum
from GoodWillShoppingSearch.models.queryitem import QueryItem
from GoodWillShoppingSearch.enums.goodwillcategories import GoodWillCategories
from GoodWillShoppingSearch.enums.goodwillsearchgallery import GoodWillSearchGallery


class TestQueryItemBasics:
    """Test basic QueryItem functionality."""

    def test_string_value(self):
        """Test QueryItem with string value."""
        item = QueryItem("test", "VALUE")
        assert item.get_value() == "value"  # Should be lowercased
        assert item.query_string_value() == "test=value"

    def test_string_value_already_lowercase(self):
        """Test QueryItem with already lowercase string."""
        item = QueryItem("param", "lowercase")
        assert item.get_value() == "lowercase"
        assert item.query_string_value() == "param=lowercase"

    def test_integer_value(self):
        """Test QueryItem with integer value."""
        item = QueryItem("price", 100)
        assert item.get_value() == "100"
        assert item.query_string_value() == "price=100"

    def test_integer_zero(self):
        """Test QueryItem with zero value."""
        item = QueryItem("count", 0)
        assert item.get_value() == "0"
        assert item.query_string_value() == "count=0"

    def test_boolean_true(self):
        """Test QueryItem with boolean True."""
        item = QueryItem("flag", True)
        assert item.get_value() == "true"
        assert item.query_string_value() == "flag=true"

    def test_boolean_false(self):
        """Test QueryItem with boolean False."""
        item = QueryItem("flag", False)
        assert item.get_value() == "false"
        assert item.query_string_value() == "flag=false"

    def test_empty_string(self):
        """Test QueryItem with empty string."""
        item = QueryItem("search", "")
        assert item.get_value() == ""
        assert item.query_string_value() == "search="


class TestQueryItemEnums:
    """Test QueryItem with Enum values."""

    def test_enum_category_value(self):
        """Test QueryItem with GoodWillCategories enum."""
        item = QueryItem("c", GoodWillCategories.ComputersAndElectronics)
        # Should extract the numeric value from enum
        assert item.get_value() == str(GoodWillCategories.ComputersAndElectronics.value)

    def test_enum_search_gallery(self):
        """Test QueryItem with GoodWillSearchGallery enum."""
        item = QueryItem("sg", GoodWillSearchGallery.NewToday)
        assert item.get_value() == str(GoodWillSearchGallery.NewToday.value)

    def test_enum_empty_value(self):
        """Test QueryItem with Empty enum value."""
        item = QueryItem("c", GoodWillCategories.Empty)
        assert item.get_value() == str(GoodWillCategories.Empty.value)


class TestQueryItemValueSetting:
    """Test QueryItem value_set method."""

    def test_value_set_string(self):
        """Test updating QueryItem with new string value."""
        item = QueryItem("param", "initial")
        assert item.get_value() == "initial"

        item.value_set("UPDATED")
        assert item.get_value() == "updated"

    def test_value_set_integer(self):
        """Test updating QueryItem with new integer value."""
        item = QueryItem("num", 10)
        assert item.get_value() == "10"

        item.value_set(999)
        assert item.get_value() == "999"

    def test_value_set_boolean(self):
        """Test updating QueryItem with new boolean value."""
        item = QueryItem("enabled", False)
        assert item.get_value() == "false"

        item.value_set(True)
        assert item.get_value() == "true"

    def test_value_set_enum(self):
        """Test updating QueryItem with new enum value."""
        item = QueryItem("cat", GoodWillCategories.Empty)
        original = item.get_value()

        item.value_set(GoodWillCategories.ComputersAndElectronics)
        assert item.get_value() != original
        assert item.get_value() == str(GoodWillCategories.ComputersAndElectronics.value)


class TestQueryItemEdgeCases:
    """Test edge cases and special scenarios."""

    def test_mixed_case_string(self):
        """Test string with mixed case gets lowercased."""
        item = QueryItem("text", "MiXeD CaSe")
        assert item.get_value() == "mixed case"

    def test_string_with_numbers(self):
        """Test string containing numbers."""
        item = QueryItem("code", "ABC123")
        assert item.get_value() == "abc123"

    def test_negative_integer(self):
        """Test negative integer value."""
        item = QueryItem("delta", -50)
        assert item.get_value() == "-50"

    def test_large_integer(self):
        """Test large integer value."""
        item = QueryItem("max", 999999)
        assert item.get_value() == "999999"

    def test_query_string_format(self):
        """Test query string format is correct."""
        item = QueryItem("key", "value")
        result = item.query_string_value()
        assert "=" in result
        assert result.startswith("key")
        assert result.endswith("value")

    def test_special_characters_in_string(self):
        """Test string with special characters."""
        # QueryItem lowercases but doesn't URL encode
        item = QueryItem("text", "Hello World!")
        assert item.get_value() == "hello world!"
