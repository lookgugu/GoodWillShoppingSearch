#!/usr/bin/env python3
"""GoodWill Shopping Search CLI - Command-line interface for searching ShopGoodwill.com"""

import click
from pathlib import Path
from tabulate import tabulate

from GoodWillShoppingSearch.utils.enum_utils import (
    find_category,
    find_location,
    list_categories,
    list_locations
)
from GoodWillShoppingSearch.utils.config_manager import (
    create_search_config,
    edit_search_config,
    delete_search_config,
    list_search_configs,
    get_saved_searches_dir,
    get_search_config_path
)
from GoodWillShoppingSearch.utils.search_wrapper import (
    execute_search,
    execute_search_from_file
)
from GoodWillShoppingSearch.formatters.output import format_products


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """
    GoodWill Shopping Search CLI

    Search for items on ShopGoodwill.com from the command line.
    """
    pass


@cli.command()
@click.argument('keyword')
@click.option('--category', '-c', help='Category name or ID (e.g., "Computers" or "30")')
@click.option('--location', '-l', help='Location name or ID (e.g., "TX_Austin" or "43")')
@click.option('--min-price', type=int, help='Minimum price (whole dollars)')
@click.option('--max-price', type=int, help='Maximum price (whole dollars)')
@click.option('--format', '-f', type=click.Choice(['table', 'json', 'quiet']), default='table', help='Output format')
@click.option('--page-size', type=int, default=40, help='Number of results per page')
def search(keyword, category, location, min_price, max_price, format, page_size):
    """
    Quick search without saving.

    Example:
        goodwill search "T480" --category computers --max-price 500
    """
    params = {'keyword_search': keyword}

    # Resolve category if provided
    if category:
        try:
            cat_enum = find_category(category)
            params['categories'] = cat_enum.value
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            raise click.Abort()

    # Resolve location if provided
    if location:
        try:
            loc_enum = find_location(location)
            params['good_will_location'] = loc_enum.value
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            raise click.Abort()

    # Add price filters
    if min_price is not None:
        params['low_price'] = min_price
    if max_price is not None:
        params['high_price'] = max_price

    # Add page size
    if page_size != 40:
        params['page_size'] = page_size

    # Execute search
    try:
        click.echo(f"Searching for '{keyword}'...")
        products = execute_search(params, suppress_output=True)
        format_products(products, format)
    except Exception as e:
        click.echo(f"Search failed: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.argument('name')
def create(name):
    """
    Create a new saved search interactively.

    Example:
        goodwill create laptop-deals
    """
    try:
        file_path = create_search_config(name, {}, interactive=True)
        click.echo(f"✓ Saved search created: {file_path}")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"Failed to create search: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.argument('name')
def edit(name):
    """
    Edit an existing saved search.

    Example:
        goodwill edit laptop-deals
    """
    try:
        edit_search_config(name)
        click.echo(f"✓ Saved search '{name}' updated")
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"Failed to edit search: {e}", err=True)
        raise click.Abort()


@cli.command(name='list')
def list_saved():
    """
    List all saved searches.

    Example:
        goodwill list
    """
    configs = list_search_configs()

    if not configs:
        click.echo("No saved searches found.")
        click.echo(f"Create one with: goodwill create <name>")
        return

    click.echo(f"Saved searches in {get_saved_searches_dir()}:\n")
    for name in configs:
        click.echo(f"  • {name}")

    click.echo(f"\nTotal: {len(configs)} saved searches")


@cli.command()
@click.argument('name')
@click.option('--yes', '-y', is_flag=True, help='Skip confirmation')
def delete(name, yes):
    """
    Delete a saved search.

    Example:
        goodwill delete old-search
    """
    if not yes:
        if not click.confirm(f"Delete saved search '{name}'?"):
            click.echo("Cancelled")
            return

    try:
        delete_search_config(name)
        click.echo(f"✓ Deleted saved search '{name}'")
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"Failed to delete search: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.argument('name', required=False)
@click.option('--all', '-a', is_flag=True, help='Run all saved searches')
@click.option('--format', '-f', type=click.Choice(['table', 'json', 'quiet']), default='table', help='Output format')
def run(name, all, format):
    """
    Run saved search(es).

    Examples:
        goodwill run laptop-deals
        goodwill run --all
    """
    if all:
        # Run all saved searches
        configs = list_search_configs()
        if not configs:
            click.echo("No saved searches found.")
            return

        for config_name in configs:
            click.echo(f"\n{'=' * 60}")
            click.echo(f"Running: {config_name}")
            click.echo(f"{'=' * 60}\n")

            try:
                file_path = str(get_search_config_path(config_name))
                products = execute_search_from_file(file_path, suppress_output=True)
                format_products(products, format)
            except Exception as e:
                click.echo(f"Failed: {e}", err=True)

    elif name:
        # Run specific saved search
        try:
            file_path = str(get_search_config_path(name))

            click.echo(f"Running saved search: {name}")
            products = execute_search_from_file(file_path, suppress_output=True)
            format_products(products, format)
        except FileNotFoundError:
            click.echo(f"Error: Saved search '{name}' not found", err=True)
            raise click.Abort()
        except Exception as e:
            click.echo(f"Search failed: {e}", err=True)
            raise click.Abort()
    else:
        click.echo("Error: Specify a search name or use --all")
        click.echo("Usage: goodwill run <name> OR goodwill run --all")
        raise click.Abort()


@cli.command(name='list-categories')
@click.option('--filter', '-f', help='Filter categories by name')
def cmd_list_categories(filter):
    """
    List all available categories.

    Examples:
        goodwill list-categories
        goodwill list-categories --filter computer
    """
    categories = list_categories(filter)

    if not categories:
        click.echo("No categories found matching your filter.")
        return

    # Format as table
    headers = ['Category Name', 'ID']
    rows = [[name, id] for name, id in categories]

    click.echo(tabulate(rows, headers=headers, tablefmt='simple'))
    click.echo(f"\nTotal: {len(categories)} categories")

    if not filter:
        click.echo("\nTip: Use --filter to search categories (e.g., --filter computer)")


@cli.command(name='list-locations')
@click.option('--filter', '-f', help='Filter locations by name')
def cmd_list_locations(filter):
    """
    List all available Goodwill locations.

    Examples:
        goodwill list-locations
        goodwill list-locations --filter california
    """
    locations = list_locations(filter)

    if not locations:
        click.echo("No locations found matching your filter.")
        return

    # Format as table
    headers = ['Location Name', 'ID']
    rows = [[name, id] for name, id in locations]

    click.echo(tabulate(rows, headers=headers, tablefmt='simple'))
    click.echo(f"\nTotal: {len(locations)} locations")

    if not filter:
        click.echo("\nTip: Use --filter to search locations (e.g., --filter TX)")


if __name__ == '__main__':
    cli()
