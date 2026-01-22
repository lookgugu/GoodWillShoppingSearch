"""Utilities for fuzzy matching and resolving category/location enums."""

from difflib import get_close_matches
from typing import List, Tuple, Type
from enum import Enum

from GoodWillShoppingSearch.enums.goodwillcategories import GoodWillCategories
from GoodWillShoppingSearch.enums.goodwilllocations import GoodWillLocations


def _find_enum(name_or_id: str, enum_class: Type[Enum], empty_value: Enum, entity_name: str) -> Enum:
    """
    Generic function to find an enum value by name or ID with fuzzy matching.

    Args:
        name_or_id: Enum name or ID
        enum_class: The enum class to search in
        empty_value: The empty/default enum value to exclude
        entity_name: Human-readable name for error messages (e.g., "Category", "Location")

    Returns:
        Enum value

    Raises:
        ValueError: If enum not found or ambiguous
    """
    # Try direct ID match first
    for item in enum_class:
        if item.value == str(name_or_id):
            return item

    # Try exact name match (case-insensitive)
    name_upper = name_or_id.upper().replace(" ", "").replace("_", "")
    for item in enum_class:
        item_name_upper = item.name.upper().replace("_", "")
        if item_name_upper == name_upper:
            return item

    # Fuzzy match on enum names
    all_names = [item.name for item in enum_class if item != empty_value]
    matches = get_close_matches(name_or_id, all_names, n=3, cutoff=0.6)

    if not matches:
        raise ValueError(
            f"{entity_name} '{name_or_id}' not found. "
            f"Use 'list-{entity_name.lower()}s' to see all options."
        )

    if len(matches) > 1:
        suggestions = ', '.join([f"{m} ({enum_class[m].value})" for m in matches])
        raise ValueError(
            f"Ambiguous {entity_name.lower()} '{name_or_id}'. Did you mean: {suggestions}?"
        )

    return enum_class[matches[0]]


def _list_enum(enum_class: Type[Enum], empty_value: Enum, filter_text: str = None) -> List[Tuple[str, str]]:
    """
    Generic function to list all enum values as (name, id) tuples.

    Args:
        enum_class: The enum class to list
        empty_value: The empty/default enum value to exclude
        filter_text: Optional filter to match against names

    Returns:
        List of (name, id) tuples sorted by name
    """
    items = []
    for item in enum_class:
        if item == empty_value:
            continue

        if filter_text:
            # Case-insensitive filter
            if filter_text.lower() not in item.name.lower():
                continue

        items.append((item.name, item.value))

    return sorted(items, key=lambda x: x[0])


def find_category(name_or_id: str) -> GoodWillCategories:
    """
    Find a category by name or ID with fuzzy matching.

    Args:
        name_or_id: Category name (e.g., "Computers") or ID (e.g., "30")

    Returns:
        GoodWillCategories enum value

    Raises:
        ValueError: If category not found or ambiguous
    """
    return _find_enum(name_or_id, GoodWillCategories, GoodWillCategories.Empty, "Category")


def find_location(name_or_id: str) -> GoodWillLocations:
    """
    Find a location by name or ID with fuzzy matching.

    Args:
        name_or_id: Location name (e.g., "TX_Austin") or ID (e.g., "43")

    Returns:
        GoodWillLocations enum value

    Raises:
        ValueError: If location not found or ambiguous
    """
    return _find_enum(name_or_id, GoodWillLocations, GoodWillLocations.Empty, "Location")


def list_categories(filter_text: str = None) -> List[Tuple[str, str]]:
    """
    List all categories as (name, id) tuples.

    Args:
        filter_text: Optional filter to match against category names

    Returns:
        List of (name, id) tuples sorted by name
    """
    return _list_enum(GoodWillCategories, GoodWillCategories.Empty, filter_text)


def list_locations(filter_text: str = None) -> List[Tuple[str, str]]:
    """
    List all locations as (name, id) tuples.

    Args:
        filter_text: Optional filter to match against location names

    Returns:
        List of (name, id) tuples sorted by name
    """
    return _list_enum(GoodWillLocations, GoodWillLocations.Empty, filter_text)
