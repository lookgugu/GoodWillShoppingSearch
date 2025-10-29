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
        self.price = product.find('div', {'class': 'price'}).text.split(' ')[0].strip()[1:]
        self.price = float(self.price.replace(',', ''))
        self.listing = product.find('div', {'class': 'title'}).text.strip().split('\n')[0].strip()
        self.product_id = product.find('div', {'class': 'product-number'}).text.split(' ')[2]
        self.url = 'https://www.shopgoodwill.com/Item/{}'.format(self.product_id)

        timer_element = product.find('div', {'class': 'timer countdown-classic product-countdown'})
        if timer_element:
            self.ends = timer_element['data-countdown']
            self.end_date = self.time_zone.localize(datetime.strptime(self.ends, '%m/%d/%Y %I:%M:%S %p'))
            self.duration = self.end_date - datetime.now(self.time_zone)
        else:
            self.end_date = datetime.now(self.time_zone)
            self.duration = timedelta(0)

        self.listing = unidecode(self.listing)
