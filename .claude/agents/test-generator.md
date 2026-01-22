# Test Generator Agent

Generate a comprehensive pytest test suite for GoodWillShoppingSearch using modern web scraping testing best practices.

## Objective

Create a complete test suite with proper fixtures, mocking, and edge case coverage to ensure the scraper remains reliable as ShopGoodwill.com changes.

## Test Strategy

### Directory Structure

Create tests in the following structure:
```
tests/
├── __init__.py
├── conftest.py                 # Shared fixtures
├── fixtures/
│   ├── sample_html.py         # Sample HTML responses
│   └── sample_json.py         # Sample JSON configs
├── test_goodwillproduct.py    # Product parsing tests
├── test_goodwillsearch.py     # Search orchestration tests
└── test_queryitem.py          # Query parameter tests
```

### Core Testing Principles

1. **Mock all HTTP requests** - Use `unittest.mock.patch` or `responses` library
2. **Use fixtures for test data** - Define reusable HTML/JSON samples in conftest.py
3. **Test edge cases** - Missing data, malformed HTML, timezone edge cases
4. **Fast execution** - No live network calls, tests should run in < 5 seconds total
5. **High coverage** - Target 95%+ code coverage

## Fixtures to Create (conftest.py)

### 1. Sample Product HTML
```python
@pytest.fixture
def sample_product_html():
    """Mock BeautifulSoup PageElement for a typical product listing"""
    html = '''
    <span class="data-container">
        <span class="itemPrice">$45.00</span>
        <span class="itemTitle">Lenovo ThinkPad T480 Laptop</span>
        <span data-countdown="01/25/2026 11:30:00 PM"></span>
        <a href="/Item/12345678"></a>
    </span>
    '''
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    return soup.find('span', class_='data-container')
```

### 2. Mock HTTP Response
```python
@pytest.fixture
def mock_search_response():
    """Mock successful requests.Response with product listings"""
    # Return HTML with multiple product containers
    pass
```

### 3. Sample JSON Config
```python
@pytest.fixture
def sample_json_config(tmp_path):
    """Create temporary JSON search configuration file"""
    config = {
        "categories": "7",
        "keyword_search": "T480",
        "price_min": "50",
        "price_max": "500"
    }
    json_file = tmp_path / "test_search.json"
    json_file.write_text(json.dumps(config))
    return str(json_file)
```

### 4. Timezone Fixture
```python
@pytest.fixture
def local_timezone():
    """Provide consistent timezone for testing"""
    from tzlocal import get_localzone
    return get_localzone()
```

## Test Coverage Requirements

### test_goodwillproduct.py

Test the GoodWillProduct class (models/goodwillproduct.py):

**Price Parsing Tests:**
- ✓ Standard price format: "$45.00"
- ✓ Price with commas: "$1,250.99"
- ✓ Missing dollar sign edge case
- ✓ Invalid price format (should handle gracefully)

**Title Normalization Tests:**
- ✓ Standard ASCII title
- ✓ Special characters (unidecode conversion)
- ✓ Empty title edge case

**Countdown/Duration Tests:**
- ✓ Valid countdown datetime parsing
- ✓ Duration calculation accuracy
- ✓ Timezone-aware datetime handling
- ✓ Past auction end time (negative duration)
- ✓ Malformed countdown format

**Product ID/URL Tests:**
- ✓ Extract product ID from href
- ✓ Construct full product URL correctly

### test_goodwillsearch.py

Test the GoodWillSearch class (models/goodwillsearch.py):

**Query String Construction:**
- ✓ Empty parameters (minimal query)
- ✓ All parameters populated
- ✓ Enum value extraction (categories, locations)
- ✓ Boolean parameter handling
- ✓ URL encoding special characters

**JSON Configuration Loading:**
- ✓ Valid JSON file loads correctly
- ✓ Missing optional parameters use defaults
- ✓ Invalid JSON raises appropriate error
- ✓ File not found handling

**Search Execution (with mocked requests):**
- ✓ Successful search returns GoodWillProduct list
- ✓ HTTP 404 error handling
- ✓ HTTP 429 rate limit handling
- ✓ Connection timeout handling
- ✓ Empty search results (no products found)
- ✓ Malformed HTML response

**Search URL Generation:**
- ✓ Base URL construction
- ✓ Query parameter ordering
- ✓ Special character escaping

### test_queryitem.py

Test the QueryItem class (models/queryitem.py):

**Type Conversion:**
- ✓ String values
- ✓ Boolean values (true/false conversion)
- ✓ Integer values
- ✓ Enum values (extract .value attribute)

**Value Normalization:**
- ✓ Lowercase conversion
- ✓ Empty string handling
- ✓ None/null handling

**Query String Formatting:**
- ✓ Key=value pair generation
- ✓ URL encoding special characters

## Mocking Patterns

### Mock HTTP Requests (requests.get)

```python
from unittest.mock import patch, MagicMock

@patch('GoodWillShoppingSearch.models.goodwillsearch.requests.get')
def test_successful_search(mock_get, sample_search_response, local_timezone):
    # Setup mock
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = sample_search_response
    mock_get.return_value = mock_response

    # Execute search
    search = GoodWillSearch(local_timezone)
    results = search.search("laptop")

    # Assertions
    assert len(results) > 0
    assert isinstance(results[0], GoodWillProduct)
    mock_get.assert_called_once()
```

### Mock Network Errors

```python
@patch('GoodWillShoppingSearch.models.goodwillsearch.requests.get')
def test_connection_timeout(mock_get, local_timezone):
    from requests.exceptions import Timeout
    mock_get.side_effect = Timeout("Connection timed out")

    search = GoodWillSearch(local_timezone)
    # Test should handle timeout gracefully (may need to add error handling first)
```

## Edge Cases to Test

1. **Malformed HTML**: Missing required elements (price, title, countdown)
2. **Timezone edge cases**: DST transitions, different timezone inputs
3. **Encoding issues**: Unicode characters in product titles
4. **Empty results**: ShopGoodwill returns no products
5. **Rate limiting**: HTTP 429 responses
6. **Network failures**: Timeouts, connection errors, DNS failures

## Test Execution

Create pytest.ini configuration:
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --verbose
    --cov=GoodWillShoppingSearch
    --cov-report=term-missing
    --cov-report=html
```

## Success Criteria

- ✓ All tests pass
- ✓ 95%+ code coverage
- ✓ Tests run in < 5 seconds
- ✓ No live network calls (all mocked)
- ✓ Clear test names describing what's tested
- ✓ Edge cases covered
- ✓ Proper fixture usage for reusable test data

## Dependencies to Add

Update requirements.txt:
```
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-mock>=3.10.0
responses>=0.23.0  # Alternative to unittest.mock for HTTP mocking
```

## Implementation Notes

When generating tests:
1. Start with conftest.py fixtures
2. Create sample HTML/JSON in fixtures/ directory
3. Write tests for simplest component first (QueryItem)
4. Progress to GoodWillProduct, then GoodWillSearch
5. Add error handling tests last
6. Run coverage report and identify gaps
7. Add tests for uncovered code paths

## Current Gaps in Source Code

The test generator should identify that the source code lacks:
- HTTP error handling (404, 429, timeouts)
- Retry logic for failed requests
- Input validation for JSON configs
- Graceful handling of malformed HTML

Tests should be written to document expected behavior even if error handling doesn't exist yet, making it clear what needs to be implemented.
