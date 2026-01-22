"""Output formatters for search results."""

import json
from typing import List
from tabulate import tabulate


def format_products(products: List, format_type: str) -> None:
    """
    Format and print products according to format_type.

    Args:
        products: List of GoodWillProduct objects
        format_type: One of 'table', 'json', 'quiet'
    """
    if not products:
        print("No results found.")
        return

    if format_type == 'table':
        _format_table(products)
    elif format_type == 'json':
        _format_json(products)
    elif format_type == 'quiet':
        _format_quiet(products)
    else:
        # Default to current format
        for product in products:
            product.print_product()


def _format_table(products: List) -> None:
    """Format products as a table."""
    rows = []
    for p in products:
        # Truncate listing if too long
        listing = p.listing[:60] + "..." if len(p.listing) > 60 else p.listing

        # Format duration
        duration_str = str(p.duration).split('.')[0] if p.duration else "N/A"

        rows.append([
            f"${p.price:.2f}",
            listing,
            duration_str,
            p.url
        ])

    headers = ['Price', 'Title', 'Time Remaining', 'URL']
    print(tabulate(rows, headers=headers, tablefmt='grid'))
    print(f"\nTotal results: {len(products)}")


def _format_json(products: List) -> None:
    """Format products as JSON."""
    results = []
    for p in products:
        results.append({
            'price': p.price,
            'listing': p.listing,
            'product_id': p.product_id,
            'url': p.url,
            'end_date': p.end_date.isoformat() if p.end_date else None,
            'duration_seconds': p.duration.total_seconds() if p.duration else 0
        })

    print(json.dumps(results, indent=2))


def _format_quiet(products: List) -> None:
    """Format products as URLs only (one per line)."""
    for p in products:
        print(p.url)
