---
name: new-search-config
description: Create a new ShopGoodwill.com search configuration JSON file with validation
disable-model-invocation: true
---

# New Search Config Skill

Create a validated search configuration file for ShopGoodwill.com in the `saved_searches/` directory.

## Instructions

When invoked, create a new search configuration following these steps:

### 1. Gather Search Parameters

Ask the user for search parameters. Explain available options:

**Required:**
- `keyword_search`: Search term (e.g., "T480", "laptop", "vintage camera")

**Optional:**
- `categories`: Numeric category code (refer to REFERENCE.md for valid codes)
  - Example: 7 = Computers/Electronics
- `price_min`: Minimum price (dollars, no $ symbol)
- `price_max`: Maximum price (dollars, no $ symbol)
- `locations`: Numeric location code (refer to REFERENCE.md for valid regions)
- `search_gallery`: Display mode - "New", "Ending", or leave empty for default

### 2. Validate Inputs

Before creating the file:

- **keyword_search**: Must not be empty
- **categories**: If provided, verify it exists in REFERENCE.md categories list
- **locations**: If provided, verify it exists in REFERENCE.md locations list
- **price_min/price_max**: If both provided, ensure price_min < price_max
- **search_gallery**: If provided, must be "New" or "Ending"

### 3. Create JSON File

Create file in `saved_searches/` directory:

**Filename**: Use keyword_search (sanitized for filesystem) with `.json` extension
- Remove special characters, spaces → underscores
- Example: "T480 Laptop" → "T480_Laptop.json"

**Format**: Use minimal JSON format (only include non-empty parameters)

**Example minimal config** (keyword only):
```json
{
  "categories": "7",
  "keyword_search": "T480"
}
```

**Example full config**:
```json
{
  "categories": "7",
  "keyword_search": "laptop",
  "price_min": "50",
  "price_max": "500",
  "locations": "1",
  "search_gallery": "Ending"
}
```

### 4. Confirm Creation

After creating the file:
- Display the full path to the created file
- Show the JSON content created
- Suggest running the search: `make run` or `python main.py`

## Reference Data Location

For category and location codes, refer to `/Users/beno/Documents/Projects/GoodWillShoppingSearch/REFERENCE.md`

Common categories to mention:
- 7 = Computers/Electronics
- Check REFERENCE.md for complete list

## Notes

- All string values in JSON should be quoted
- Numeric codes are stored as strings in JSON (e.g., "7" not 7)
- Use minimal format - only include parameters the user specifies
- The application will use defaults for any omitted parameters
