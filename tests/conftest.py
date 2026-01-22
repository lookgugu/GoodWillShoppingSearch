"""Pytest configuration and shared fixtures for GoodWillShoppingSearch tests."""

import pytest
import json
import pytz
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from pathlib import Path


@pytest.fixture
def local_timezone():
    """Provide consistent timezone for testing."""
    return pytz.timezone('America/New_York')


@pytest.fixture
def sample_product_html():
    """Mock BeautifulSoup PageElement for a typical product listing."""
    html = '''
    <span class="data-container">
        <div class="price">$45.00</div>
        <div class="title">Lenovo ThinkPad T480 Laptop</div>
        <div class="product-number">Item # 12345678</div>
        <div class="timer countdown-classic product-countdown" data-countdown="01/25/2026 11:30:00 PM"></div>
    </span>
    '''
    soup = BeautifulSoup(html, 'html.parser')
    return soup.find('span', class_='data-container')


@pytest.fixture
def sample_product_html_with_comma_price():
    """Mock product with price containing commas."""
    html = '''
    <span class="data-container">
        <div class="price">$1,250.99</div>
        <div class="title">High-End Gaming Computer</div>
        <div class="product-number">Item # 87654321</div>
        <div class="timer countdown-classic product-countdown" data-countdown="02/15/2026 03:45:00 PM"></div>
    </span>
    '''
    soup = BeautifulSoup(html, 'html.parser')
    return soup.find('span', class_='data-container')


@pytest.fixture
def sample_product_html_special_chars():
    """Mock product with special characters in title."""
    html = '''
    <span class="data-container">
        <div class="price">$25.50</div>
        <div class="title">Café Latte Maker™ — Premium Edition</div>
        <div class="product-number">Item # 11223344</div>
        <div class="timer countdown-classic product-countdown" data-countdown="01/30/2026 09:00:00 AM"></div>
    </span>
    '''
    soup = BeautifulSoup(html, 'html.parser')
    return soup.find('span', class_='data-container')


@pytest.fixture
def sample_product_html_no_timer():
    """Mock product without countdown timer."""
    html = '''
    <span class="data-container">
        <div class="price">$10.00</div>
        <div class="title">Vintage Camera</div>
        <div class="product-number">Item # 99887766</div>
    </span>
    '''
    soup = BeautifulSoup(html, 'html.parser')
    return soup.find('span', class_='data-container')


@pytest.fixture
def sample_search_response_html():
    """Mock successful search response with multiple products."""
    return '''
    <html>
    <body>
        <span class="data-container">
            <div class="price">$45.00</div>
            <div class="title">Lenovo ThinkPad T480</div>
            <div class="product-number">Item # 12345678</div>
            <div class="timer countdown-classic product-countdown" data-countdown="01/25/2026 11:30:00 PM"></div>
        </span>
        <span class="data-container">
            <div class="price">$125.00</div>
            <div class="title">Dell Latitude E7470</div>
            <div class="product-number">Item # 23456789</div>
            <div class="timer countdown-classic product-countdown" data-countdown="01/26/2026 02:15:00 PM"></div>
        </span>
        <span class="data-container">
            <div class="price">$85.50</div>
            <div class="title">HP EliteBook 840</div>
            <div class="product-number">Item # 34567890</div>
            <div class="timer countdown-classic product-countdown" data-countdown="01/27/2026 08:00:00 AM"></div>
        </span>
    </body>
    </html>
    '''


@pytest.fixture
def sample_empty_search_response():
    """Mock search response with no products."""
    return '''
    <html>
    <body>
        <div class="no-results">No items found matching your search criteria.</div>
    </body>
    </html>
    '''


@pytest.fixture
def sample_json_config(tmp_path):
    """Create temporary JSON search configuration file."""
    config = {
        "categories": "7",
        "keyword_search": "T480",
        "low_price": "50",
        "high_price": "500"
    }
    json_file = tmp_path / "test_search.json"
    json_file.write_text(json.dumps(config, indent=2))
    return str(json_file)


@pytest.fixture
def sample_json_config_minimal(tmp_path):
    """Create minimal JSON config with only keyword."""
    config = {
        "keyword_search": "laptop"
    }
    json_file = tmp_path / "minimal_search.json"
    json_file.write_text(json.dumps(config, indent=2))
    return str(json_file)


@pytest.fixture
def sample_json_config_full(tmp_path):
    """Create comprehensive JSON config with all parameters."""
    config = {
        "keyword_search": "computer",
        "search_gallery": "Ending",
        "categories": "7",
        "good_will_location": "53",  # AL_Mobile - valid GoodWillLocations enum value
        "low_price": "100",
        "high_price": "1000",
        "show_buy_now_only": True,
        "search_description": True
    }
    json_file = tmp_path / "full_search.json"
    json_file.write_text(json.dumps(config, indent=2))
    return str(json_file)


@pytest.fixture
def invalid_json_file(tmp_path):
    """Create invalid JSON file for error testing."""
    json_file = tmp_path / "invalid.json"
    json_file.write_text("{ invalid json content }")
    return str(json_file)
