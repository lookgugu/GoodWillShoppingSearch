# GoodWillShoppingSearch

GoodWillShoppingSearch is a Python application that allows you to search for products on ShopGoodwill.com, a popular online auction site for Goodwill stores.

## Purpose

This application automates the process of searching for items on ShopGoodwill.com. It provides a flexible way to define search queries, including keywords, categories, price ranges, and other filters. You can use it to monitor for specific items and receive notifications (email functionality to be implemented).

## Features

*   Search for products using keywords.
*   Filter searches by category, price, and other criteria.
*   Load search parameters from a JSON file for easy configuration.
*   Parses search results to extract product information.
*   Uses your computer's local timezone for accurate time calculations.
*   Extensible design for adding new features like email notifications.

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/your-username/GoodWillShoppingSearch.git
    ```
2.  Create a virtual environment:
    ```bash
    python -m venv venv
    ```
3.  Activate the virtual environment:
    *   **Windows:**
        ```bash
        venv\Scripts\activate
        ```
    *   **macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```
4.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

You can run the application from the command line:

```bash
python main.py
```

This will execute the `main` function in `main.py`, which currently performs two searches:
1.  A search based on the `austincomputer.json` file for the keyword "dell".
2.  A search for a predefined set of products.

### Searching for Products

You can customize the search by modifying the `main.py` file or by creating your own JSON configuration file.

#### Basic Search

To perform a simple keyword search, you can use the `search` method of the `GoodWillSearch` class:

```python
from GoodWillShoppingSearch.models.goodwillsearch import GoodWillSearch
from tzlocal import get_localzone

SGW_TIMEZONE = get_localzone()
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
from tzlocal import get_localzone
import os

SGW_TIMEZONE = get_localzone()
dir_path = os.path.dirname(os.path.realpath(__file__))
searchJson = os.path.join(dir_path, 'austincomputer.json')
search = GoodWillSearch(SGW_TIMEZONE, searchJson)
results = search.search("your-keyword")

for product in results:
    product.print_product()
```

This allows you to easily manage and reuse your search configurations.