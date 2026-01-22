# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GoodWillShoppingSearch is a Python application that automates searching for products on ShopGoodwill.com. It uses web scraping to parse search results and supports flexible search configurations via JSON files.

## Common Commands

### Running the Application
```bash
python main.py
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
