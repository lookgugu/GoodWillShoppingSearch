# GoodWillShoppingSearch

GoodWillShoppingSearch is a Python application that allows you to search for products on ShopGoodwill.com, a popular online auction site for Goodwill stores.

## Purpose

This application automates the process of searching for items on ShopGoodwill.com. It provides a flexible way to define search queries, including keywords, categories, price ranges, and other filters. You can use it to monitor for specific items and receive notifications (email functionality to be implemented).

## Features

*   Search for products using keywords.
*   Filter searches by category, price, and other criteria.
*   Load search parameters from a JSON file for easy configuration.
*   Parses search results to extract product information.
*   Extensible design for adding new features like email notifications.

## Project Structure

The project is organized as follows:

```
/Users/beno/Documents/Projects/GoodWillShoppingSearch/
├───.gitignore
├───austincomputer.json
├───LICENSE
├───main.py
├───makefile
├───pyproject.toml
├───README.md
├───requirements.txt
├───setup.cfg
├───setup.py
├───.git/...
├───GoodWillShoppingSearch/
│   ├───__init__.py
│   ├───version.py
│   ├───enums/
│   │   ├───__init__.py
│   │   ├───goodwillcategories.py
│   │   ├───goodwilllocations.py
│   │   └───goodwillsearchgallery.py
│   └───models/
│       ├───__init__.py
│       ├───goodwillproduct.py
│       ├───goodwillsearch.py
│       └───queryitem.py
├───schemas/
│   ├───search-data.json
│   └───search.json
└───venv/
    ├───bin/...
    ├───include/...
    └───lib/...
```

### Key Files

*   `main.py`: The main entry point of the application.
*   `GoodWillShoppingSearch/models/goodwillsearch.py`: Contains the `GoodWillSearch` class, which is the core of the search functionality.
*   `GoodWillShoppingSearch/models/goodwillproduct.py`: Defines the `GoodWillProduct` class, which represents a single product listing.
*   `austincomputer.json`: An example JSON file for configuring searches.
*   `requirements.txt`: Lists the Python dependencies for the project.

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/your-username/GoodWillShoppingSearch.git
    ```
2.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

You can run the application from the command line:

```bash
python main.py
```

This will execute the `main` function in `main.py`, which currently performs a search based on the `austincomputer.json` file.

### Searching for Products

You can customize the search by modifying the `main.py` file or by creating your own JSON configuration file.

#### Basic Search

To perform a simple keyword search, you can use the `search` method of the `GoodWillSearch` class:

```python
from GoodWillShoppingSearch.models.goodwillsearch import GoodWillSearch
import pytz

SGW_TIMEZONE = pytz.timezone('America/Chicago')
search = GoodWillSearch(SGW_TIMEZONE)
results = search.search("your-keyword")

for product in results:
    product.print_product()
```

#### Advanced Search with JSON Configuration

For more complex searches, you can create a JSON file with your desired search parameters. The `austincomputer.json` file provides an example of the available options:

```json
{
  "search_gallery": "gallery",
  "categories": 2,
  "good_will_location": 0,
  "low_price": 0,
  "high_price": 100,
  "show_buy_now_only": false,
  "show_pick_up_only": false,
  "hide_pick_up_only": false,
  "show_one_cent_ship_only": false,
  "search_description": true,
  "show_closed_auctions": false,
  "closed_auction_end_date": "11/14/2018",
  "day_back": 9,
  "search_canada": false,
  "search_international": false,
  "field_order": 0,
  "page_number": 0,
  "page_size": 40,
  "short_description": true,
  "saved_search_id": 0
}
```

To use the JSON file, you can load it in your Python script:

```python
from GoodWillShoppingSearch.models.goodwillsearch import GoodWillSearch
import pytz
import os

SGW_TIMEZONE = pytz.timezone('America/Chicago')
dir_path = os.path.dirname(os.path.realpath(__file__))
searchJson = os.path.join(dir_path, 'austincomputer.json')
search = GoodWillSearch(SGW_TIMEZONE, searchJson)
results = search.search("your-keyword")

for product in results:
    product.print_product()
```

This allows you to easily manage and reuse your search configurations.
