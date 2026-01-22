"""Wrapper for executing searches with output control."""

from contextlib import contextmanager
from typing import List
from tzlocal import get_localzone

from GoodWillShoppingSearch.models.goodwillsearch import GoodWillSearch
from GoodWillShoppingSearch.models.goodwillproduct import GoodWillProduct


@contextmanager
def suppress_print_product():
    """Context manager to suppress GoodWillProduct.print_product() calls."""
    original_method = GoodWillProduct.print_product
    GoodWillProduct.print_product = lambda self: None
    try:
        yield
    finally:
        GoodWillProduct.print_product = original_method


def execute_search(params: dict, suppress_output: bool = True) -> List[GoodWillProduct]:
    """
    Execute a search with the given parameters.

    Args:
        params: Dictionary of search parameters (matches JSON format)
        suppress_output: If True, suppress default print_product() output

    Returns:
        List of GoodWillProduct objects
    """
    timezone = get_localzone()
    search = GoodWillSearch(timezone, None)
    search.search_params_by_json(params)

    keyword = params.get('keyword_search', '')
    if not keyword:
        raise ValueError("keyword_search is required")

    if suppress_output:
        with suppress_print_product():
            products = search.search(keyword)
    else:
        products = search.search(keyword)

    return products


def execute_search_from_file(json_path: str, suppress_output: bool = True) -> List[GoodWillProduct]:
    """
    Execute a search from a JSON configuration file.

    Args:
        json_path: Path to JSON configuration file
        suppress_output: If True, suppress default print_product() output

    Returns:
        List of GoodWillProduct objects
    """
    timezone = get_localzone()
    search = GoodWillSearch(timezone, json_path)

    if not search.keyword_search:
        raise ValueError(f"No keyword_search specified in {json_path}")

    if suppress_output:
        with suppress_print_product():
            products = search.search(search.keyword_search)
    else:
        products = search.search(search.keyword_search)

    return products
