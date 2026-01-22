# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GoodWillShoppingSearch is a Python application that automates searching for products on ShopGoodwill.com. It uses web scraping to parse search results and supports flexible search configurations via JSON files.

## Common Commands

### Running the Application

**Traditional Method (JSON-based):**
```bash
python main.py
```
This runs all saved searches in the [saved_searches/](saved_searches/) directory.

**CLI Method (Command-line interface):**
```bash
# Quick search without saving
python cli.py search "laptop" --category computers --max-price 500

# Create a saved search interactively
python cli.py create my-search

# Run a specific saved search
python cli.py run my-search

# Run all saved searches
python cli.py run --all

# List all saved searches
python cli.py list

# Edit a saved search
python cli.py edit my-search

# Delete a saved search
python cli.py delete my-search

# Browse categories and locations
python cli.py list-categories --filter computer
python cli.py list-locations --filter TX
```

### Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt
```

### Dependencies
- beautifulsoup4 - HTML parsing for web scraping
- unidecode - Text normalization
- requests - HTTP requests to ShopGoodwill.com
- pytz - Timezone support (legacy, used alongside tzlocal)
- tzlocal - Local timezone detection
- click - CLI framework for command-line interface
- tabulate - Table formatting for CLI output

## CLI Interface

### Overview

The CLI provides a modern command-line interface for searching ShopGoodwill.com. It offers:
- **Quick searches** without creating JSON files
- **Interactive wizards** for creating and editing saved searches
- **Multiple output formats** (table, JSON, quiet)
- **Fuzzy matching** for categories and locations
- **Backward compatibility** with existing JSON-based workflow

### CLI Architecture

**Entry Point:** [cli.py](cli.py)
- Uses Click framework for command parsing
- All commands defined as Click command functions
- Integrates with existing GoodWillSearch models (zero modifications to core code)

**Key Components:**

1. **Enum Utilities** ([GoodWillShoppingSearch/utils/enum_utils.py](GoodWillShoppingSearch/utils/enum_utils.py))
   - Fuzzy matching for category/location names using difflib
   - Resolves user-friendly names to enum values
   - Example: "computers" → GoodWillCategories.Computers (ID: 30)

2. **Search Wrapper** ([GoodWillShoppingSearch/utils/search_wrapper.py](GoodWillShoppingSearch/utils/search_wrapper.py))
   - Executes searches with output control
   - Suppresses default print_product() output for CLI formatting
   - Returns product lists for custom formatting

3. **Config Manager** ([GoodWillShoppingSearch/utils/config_manager.py](GoodWillShoppingSearch/utils/config_manager.py))
   - CRUD operations for saved search JSON files
   - Interactive prompts for creating/editing searches
   - Validates search parameters

4. **Output Formatters** ([GoodWillShoppingSearch/formatters/output.py](GoodWillShoppingSearch/formatters/output.py))
   - `table` - Pretty table format with aligned columns
   - `json` - Structured JSON output for scripting
   - `quiet` - URLs only (one per line) for piping

### CLI Commands

**search** - Quick search without saving
```bash
python cli.py search "keyword" [OPTIONS]
  --category, -c      Category name or ID
  --location, -l      Location name or ID
  --min-price         Minimum price
  --max-price         Maximum price
  --format, -f        Output format (table|json|quiet)
  --page-size         Results per page (default: 40)
```

**create** - Create new saved search interactively
```bash
python cli.py create <name>
```

**edit** - Edit existing saved search
```bash
python cli.py edit <name>
```

**list** - List all saved searches
```bash
python cli.py list
```

**delete** - Delete saved search
```bash
python cli.py delete <name> [--yes]
```

**run** - Run saved search(es)
```bash
python cli.py run <name>          # Run specific search
python cli.py run --all            # Run all saved searches
```

**list-categories** - Browse categories
```bash
python cli.py list-categories [--filter <text>]
```

**list-locations** - Browse locations
```bash
python cli.py list-locations [--filter <text>]
```

### Fuzzy Matching

The CLI accepts category and location names in addition to numeric IDs:

**Examples:**
- `--category computers` → Category ID 30
- `--category "Computers And Electronics"` → Category ID 7
- `--location TX_Austin` → Location ID 43
- `--location austin` → Location ID 43 (fuzzy match)

If the match is ambiguous, the CLI suggests alternatives:
```
Error: Ambiguous category 'comp'. Did you mean: Computers (30), ComputerComponents (465)?
```

### Output Formats

**Table (default):**
```
+----------+------------------------------------------+------------------+----------------------------------+
| Price    | Title                                    | Time Remaining   | URL                              |
+==========+==========================================+==================+==================================+
| $45.00   | Lenovo ThinkPad T480 Laptop             | 3 days, 10:30:00 | https://shopgoodwill.com/Item... |
+----------+------------------------------------------+------------------+----------------------------------+

Total results: 1
```

**JSON:**
```json
[
  {
    "price": 45.0,
    "listing": "Lenovo ThinkPad T480 Laptop",
    "product_id": "12345678",
    "url": "https://www.shopgoodwill.com/Item/12345678",
    "end_date": "2026-01-25T23:30:00-05:00",
    "duration_seconds": 295800.0
  }
]
```

**Quiet (URLs only):**
```
https://www.shopgoodwill.com/Item/12345678
https://www.shopgoodwill.com/Item/87654321
```

### Integration with Existing Workflow

The CLI is **completely backward compatible**:
- `python main.py` still works exactly as before
- Existing JSON files in saved_searches/ work with both methods
- No changes to GoodWillSearch, GoodWillProduct, or QueryItem classes
- CLI creates/reads standard JSON configuration files

## Architecture

### Core Components

**GoodWillSearch** ([GoodWillShoppingSearch/models/goodwillsearch.py](GoodWillShoppingSearch/models/goodwillsearch.py))
- Main search orchestrator that constructs ShopGoodwill.com query URLs
- Manages search parameters through QueryItem instances
- Each search parameter (price, category, location, etc.) is stored as a private QueryItem with property accessors
- Supports loading search configurations from JSON files via `load_json_search_file()`
- The `query_string()` method iterates through all QueryItem attributes to build the URL query string
- The `search()` method performs HTTP GET request and returns parsed GoodWillProduct objects

**GoodWillProduct** ([GoodWillShoppingSearch/models/goodwillproduct.py](GoodWillShoppingSearch/models/goodwillproduct.py))
- Represents individual product listings scraped from search results
- Parses BeautifulSoup PageElement to extract: price, title, product ID/URL, auction end time
- Handles timezone-aware datetime calculations using the provided timezone
- Uses unidecode to normalize listing titles (removes special characters)
- Duration calculation shows time remaining until auction ends

**QueryItem** ([GoodWillShoppingSearch/models/queryitem.py](GoodWillShoppingSearch/models/queryitem.py))
- Abstraction layer for URL query parameters
- Converts Python types (str, bool, int, Enum) to proper query string format
- Handles enum values by extracting their `.value` attribute
- All values are lowercased for consistency

### Enums

Located in [GoodWillShoppingSearch/enums/](GoodWillShoppingSearch/enums/):
- **GoodWillCategories**: Product categories (e.g., 7 = Computers/Electronics)
- **GoodWillLocations**: Goodwill store locations by region
- **GoodWillSearchGallery**: Search view options (New, Ending, or Empty)

Category and location numeric values are documented in [REFERENCE.md](REFERENCE.md).

### Search Configuration

**JSON Configuration Files**
- Stored in [saved_searches/](saved_searches/) directory
- [main.py](main.py) automatically processes all JSON files in this directory
- Minimal example (see [saved_searches/T480.json](saved_searches/T480.json)):
  ```json
  {
    "categories": "7",
    "keyword_search": "T480"
  }
  ```
- Full example available in root directory's austincomputer.json (not in saved_searches)
- Only `keyword_search` is required; all other parameters have defaults

### Timezone Handling

The application requires timezone awareness for accurate auction end time calculations:
- Uses `tzlocal.get_localzone()` to detect the system's local timezone
- All GoodWillSearch instances require a timezone parameter
- Auction end times from ShopGoodwill.com are localized using this timezone
- The product duration calculation compares timezone-aware datetimes

## Application Flow

1. [main.py](main.py) calls `search_by_json_files()` which iterates through saved_searches/ directory
2. For each JSON file:
   - Instantiate GoodWillSearch with local timezone and JSON file path
   - GoodWillSearch loads parameters from JSON via `load_json_search_file()`
   - If `keyword_search` is specified in JSON, execute search
   - Search constructs URL via `search_url()` which calls `query_string()`
   - HTTP GET request retrieves HTML results
   - `parse_results()` uses BeautifulSoup to find product containers with class 'data-container'
   - Each product span is parsed into a GoodWillProduct instance
   - Products are printed via `print_product()` showing price, listing, URL, and duration

## Key Implementation Details

- ShopGoodwill.com base URL: `https://www.shopgoodwill.com/Listings`
- Product detail URL pattern: `https://www.shopgoodwill.com/Item/{product_id}`
- Web scraping targets elements with class 'data-container' for product listings
- Price parsing removes dollar sign and commas, converts to float
- Product countdown timer uses 'data-countdown' attribute with format `%m/%d/%Y %I:%M:%S %p`

## Testing and Development

This project does not currently have automated tests. The setup.py file lists pytest and flake8 as validation dependencies but no tests directory exists.

When adding features:
- Maintain the QueryItem pattern for new search parameters
- Update JSON schema documentation if adding new configuration options
- Ensure timezone awareness is preserved for any time-related features
- Follow the existing property/setter pattern in GoodWillSearch for new parameters
