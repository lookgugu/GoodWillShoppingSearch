# GoodWillShoppingSearch Test Suite

Comprehensive pytest test suite for the GoodWillShoppingSearch web scraper.

## Quick Start

### Install Test Dependencies

```bash
pip install -r requirements.txt
```

### Run All Tests

```bash
pytest
```

### Run with Coverage Report

```bash
pytest --cov=GoodWillShoppingSearch --cov-report=html
```

Then open `htmlcov/index.html` in your browser to see detailed coverage.

## Test Structure

```
tests/
├── conftest.py                    # Shared pytest fixtures
├── fixtures/                      # Test data fixtures
├── test_queryitem.py             # Tests for QueryItem class (17 tests)
├── test_goodwillproduct.py       # Tests for GoodWillProduct class (20 tests)
└── test_goodwillsearch.py        # Tests for GoodWillSearch class (30+ tests)
```

## Test Coverage

The test suite covers:

- **QueryItem**: Type conversions, enum handling, value normalization
- **GoodWillProduct**: Price parsing, title normalization, countdown parsing, timezone handling
- **GoodWillSearch**: Query string generation, JSON loading, search execution (mocked)

**Target Coverage**: 95%+

## Running Specific Tests

### Run tests for a specific module
```bash
pytest tests/test_queryitem.py
```

### Run tests matching a pattern
```bash
pytest -k "price"
```

### Run with verbose output
```bash
pytest -v
```

### Run fastest tests first
```bash
pytest --durations=10
```

## Test Categories

Tests are marked with categories (defined in pytest.ini):

- `@pytest.mark.unit` - Unit tests for individual components
- `@pytest.mark.integration` - Integration tests with multiple components
- `@pytest.mark.slow` - Tests that take longer to run
- `@pytest.mark.network` - Tests requiring network (currently all mocked)

### Run only unit tests
```bash
pytest -m unit
```

## Key Features

### Mocked HTTP Requests

All network calls are mocked using `unittest.mock.patch`:

```python
@patch('GoodWillShoppingSearch.models.goodwillsearch.requests.get')
def test_successful_search(mock_get, local_timezone, sample_search_response_html):
    # No real HTTP requests made
    mock_response = MagicMock()
    mock_response.text = sample_search_response_html
    mock_get.return_value = mock_response
    # ... test code
```

### Fixtures for Test Data

Reusable fixtures in `conftest.py`:

- `sample_product_html` - Mock product HTML
- `sample_search_response_html` - Mock search results
- `sample_json_config` - Temporary JSON config files
- `local_timezone` - Consistent timezone for tests

### Fast Execution

- No live network calls
- All HTTP requests mocked
- Tests run in < 5 seconds total

## Troubleshooting

### Import Errors

If you get import errors, make sure you're running from the project root:

```bash
cd /path/to/GoodWillShoppingSearch
pytest
```

### Coverage Not Working

Install coverage plugin:

```bash
pip install pytest-cov
```

### Tests Failing Due to Timezone

Tests use `America/New_York` timezone by default. If timezone-related tests fail, check your system timezone configuration.

## Adding New Tests

### 1. Add fixtures to conftest.py if needed
```python
@pytest.fixture
def my_fixture():
    return "test data"
```

### 2. Create test class and methods
```python
class TestMyFeature:
    def test_something(self, my_fixture):
        assert my_fixture == "test data"
```

### 3. Run tests and verify coverage
```bash
pytest --cov
```

## Continuous Integration

To run tests in CI/CD:

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests with coverage
pytest --cov=GoodWillShoppingSearch --cov-fail-under=95

# Generate coverage report
pytest --cov-report=xml
```

## Known Gaps

The source code currently lacks error handling for:

- HTTP 404/429 errors
- Connection timeouts
- Network failures
- Malformed HTML

Tests for these scenarios exist but will fail until error handling is implemented.
