"""Manager for saved search configuration files."""

import json
from pathlib import Path
from typing import List, Optional, Dict
import click


def get_saved_searches_dir() -> Path:
    """Get the saved_searches directory path."""
    # Navigate up from GoodWillShoppingSearch/utils to project root
    return Path(__file__).parent.parent.parent / 'saved_searches'


def get_search_config_path(name: str) -> Path:
    """Get the path to a saved search configuration file."""
    return get_saved_searches_dir() / f"{name}.json"


def _prompt_for_search_params(existing_params: Optional[Dict] = None) -> Dict:
    """
    Interactively prompt user for search parameters.

    Args:
        existing_params: Optional dict of existing parameters to use as defaults

    Returns:
        Dictionary of search parameters
    """
    from GoodWillShoppingSearch.utils.enum_utils import find_category, find_location

    if existing_params is None:
        existing_params = {}

    params = {}

    # Keyword search (required)
    current_keyword = existing_params.get('keyword_search', '')
    if current_keyword:
        params['keyword_search'] = click.prompt(
            'Keyword search',
            type=str,
            default=current_keyword
        )
    else:
        params['keyword_search'] = click.prompt('Keyword search', type=str)

    # Category (optional)
    current_category = existing_params.get('categories', '')
    category_prompt = 'Category (name or ID, optional)'

    if current_category:
        category = click.prompt(
            category_prompt,
            type=str,
            default=current_category,
            show_default=True
        )
    else:
        category = click.prompt(category_prompt, type=str, default='', show_default=False)

    if category:
        try:
            cat_enum = find_category(category)
            params['categories'] = cat_enum.value
        except ValueError as e:
            click.echo(f"Warning: {e}")

    # Location (optional)
    current_location = existing_params.get('good_will_location', '')
    location_prompt = 'Location (name or ID, optional)'

    if current_location:
        location = click.prompt(
            location_prompt,
            type=str,
            default=current_location,
            show_default=True
        )
    else:
        location = click.prompt(location_prompt, type=str, default='', show_default=False)

    if location:
        try:
            loc_enum = find_location(location)
            params['good_will_location'] = loc_enum.value
        except ValueError as e:
            click.echo(f"Warning: {e}")

    # Price range (optional)
    has_price_range = 'low_price' in existing_params or 'high_price' in existing_params

    if click.confirm('Set price range?', default=has_price_range):
        low_price = click.prompt(
            'Minimum price',
            type=int,
            default=existing_params.get('low_price', 0)
        )
        high_price = click.prompt(
            'Maximum price',
            type=int,
            default=existing_params.get('high_price', 999999)
        )
        params['low_price'] = low_price
        params['high_price'] = high_price

    # Other boolean options
    if click.confirm('Show only Buy Now items?', default=existing_params.get('show_buy_now_only', False)):
        params['show_buy_now_only'] = True

    if click.confirm('Show only items with $0.01 shipping?', default=existing_params.get('show_one_cent_ship_only', False)):
        params['show_one_cent_ship_only'] = True

    return params


def create_search_config(name: str, params: dict, interactive: bool = False) -> Path:
    """
    Create a new saved search configuration.

    Args:
        name: Name for the saved search (without .json extension)
        params: Dictionary of search parameters
        interactive: If True, prompt user for parameters

    Returns:
        Path to created JSON file
    """
    if interactive:
        params = _prompt_for_search_params()

    # Validate name
    if not name or '/' in name or '\\' in name or '..' in name:
        raise ValueError(f"Invalid search name: {name}")

    # Ensure keyword_search is present
    if 'keyword_search' not in params:
        raise ValueError("keyword_search is required")

    # Create saved_searches directory if it doesn't exist
    saves_dir = get_saved_searches_dir()
    saves_dir.mkdir(exist_ok=True)

    # Write JSON file
    file_path = get_search_config_path(name)
    with open(file_path, 'w') as f:
        json.dump(params, f, indent=4)

    return file_path


def edit_search_config(name: str) -> None:
    """
    Edit an existing saved search configuration.

    Args:
        name: Name of the saved search (without .json extension)
    """
    file_path = get_search_config_path(name)

    if not file_path.exists():
        raise FileNotFoundError(f"Saved search '{name}' not found")

    # Load existing config
    with open(file_path, 'r') as f:
        existing_params = json.load(f)

    # Re-create interactively with existing values as defaults
    click.echo(f"Editing saved search: {name}")
    click.echo("Press Enter to keep current value, or type new value\n")

    params = _prompt_for_search_params(existing_params)

    # Write updated config
    with open(file_path, 'w') as f:
        json.dump(params, f, indent=4)

    click.echo(f"\n✓ Updated {file_path}")


def delete_search_config(name: str) -> None:
    """
    Delete a saved search configuration.

    Args:
        name: Name of the saved search (without .json extension)
    """
    file_path = get_search_config_path(name)

    if not file_path.exists():
        raise FileNotFoundError(f"Saved search '{name}' not found")

    file_path.unlink()


def list_search_configs() -> List[str]:
    """
    List all saved search configuration names.

    Returns:
        List of search names (without .json extension)
    """
    saves_dir = get_saved_searches_dir()

    if not saves_dir.exists():
        return []

    configs = []
    for json_file in saves_dir.glob('*.json'):
        configs.append(json_file.stem)

    return sorted(configs)


def get_search_config(name: str) -> dict:
    """
    Get a saved search configuration.

    Args:
        name: Name of the saved search (without .json extension)

    Returns:
        Dictionary of search parameters
    """
    file_path = get_search_config_path(name)

    if not file_path.exists():
        raise FileNotFoundError(f"Saved search '{name}' not found")

    with open(file_path, 'r') as f:
        return json.load(f)
