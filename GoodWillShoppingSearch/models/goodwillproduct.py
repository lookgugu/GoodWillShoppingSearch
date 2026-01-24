from bs4.element import PageElement
from unidecode import unidecode
from datetime import datetime, timedelta
import pytz


class GoodWillProduct:
    def __init__(self, product: PageElement, time_zone: pytz.timezone):
        self.time_zone = time_zone
        self.html_product = product
        self.ends = None
        self.duration = None
        self.parse_product(product)

    def print_product(self):
        print(f'price {self.price} - listing: {self.listing} - url: {self.url} duration: {self.duration}')
        print(self.end_date)

    def parse_product(self, product: PageElement):
        # Try new format first (feat-item structure)
        price_elem = product.find('p', {'class': 'feat-item_price'})
        if not price_elem:
            # Fallback to old format
            price_elem = product.find('div', {'class': 'price'})

        if not price_elem:
            raise ValueError(f"Could not find price element in product: {product.get('class', 'unknown')}")

        price_text = price_elem.text.strip()
        self.price = float(price_text.lstrip('$').replace(',', ''))

        # Try new format for title
        title_elem = product.find('a', {'class': 'feat-item_name'})
        if title_elem:
            self.listing = unidecode(title_elem.text.strip())
            # Product ID is in the href: /item/253468405
            href = title_elem.get('href', '')
            self.product_id = href.split('/')[-1]
        else:
            # Fallback to old format
            title_elem_old = product.find('div', {'class': 'title'})
            if not title_elem_old:
                raise ValueError(f"Could not find title element in product: {product.get('class', 'unknown')}")
            title_text = title_elem_old.text.strip()
            self.listing = unidecode(title_text.split('\n')[0].strip())

            product_num_elem = product.find('div', {'class': 'product-number'})
            if not product_num_elem:
                raise ValueError("Could not find product-number element")
            self.product_id = product_num_elem.text.split(' ')[2]

        self.url = f'https://www.shopgoodwill.com/Item/{self.product_id}'

        # Try to find timer in new format
        time_li = product.find('li', {'class': 'text-danger'})
        if time_li:
            # New format: "1m 41s" or "2h 30m" etc.
            time_text = time_li.text.replace('Time remaining:', '').strip()
            self.duration = self._parse_duration_text(time_text)
            self.end_date = datetime.now(self.time_zone) + self.duration
        else:
            # Try old format
            timer_element = product.find('div', {'class': 'timer countdown-classic product-countdown'})
            if timer_element:
                self.ends = timer_element['data-countdown']
                self.end_date = self.time_zone.localize(datetime.strptime(self.ends, '%m/%d/%Y %I:%M:%S %p'))
                self.duration = self.end_date - datetime.now(self.time_zone)
            else:
                self.end_date = datetime.now(self.time_zone)
                self.duration = timedelta(0)

    def _parse_duration_text(self, duration_text: str) -> timedelta:
        """Parse duration from text like '1m 41s', '2h 30m', '3d 5h' etc."""
        try:
            total_seconds = 0
            parts = duration_text.strip().split()

            for part in parts:
                part = part.strip()
                if 'd' in part:
                    days = int(part.replace('d', ''))
                    total_seconds += days * 24 * 60 * 60
                elif 'h' in part:
                    hours = int(part.replace('h', ''))
                    total_seconds += hours * 60 * 60
                elif 'm' in part:
                    minutes = int(part.replace('m', ''))
                    total_seconds += minutes * 60
                elif 's' in part:
                    seconds = int(part.replace('s', ''))
                    total_seconds += seconds

            return timedelta(seconds=total_seconds)
        except:
            # If parsing fails, return 0
            return timedelta(0)
