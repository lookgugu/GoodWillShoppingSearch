from datetime import datetime
from urllib.parse import quote
import pytz
from bs4 import BeautifulSoup
import requests
import json

from GoodWillShoppingSearch.models.queryitem import QueryItem
from GoodWillShoppingSearch.enums.goodwillsearchgallery import GoodWillSearchGallery
from GoodWillShoppingSearch.enums.goodwillcategories import GoodWillCategories
from GoodWillShoppingSearch.enums.goodwilllocations import GoodWillLocations
from GoodWillShoppingSearch.models.goodwillproduct import GoodWillProduct


class GoodWillSearch:
    def __init__(self, time_zone: pytz.timezone, json_search_params_file: str = None):
        self.time_zone = time_zone
        self.set_default_search()
        if json_search_params_file is not None:
            self.load_json_search_file(json_search_params_file)


    def set_default_search(self):
        self.url = "https://www.shopgoodwill.com/Listings"
        self._search_gallery = QueryItem("sg", GoodWillSearchGallery.Empty)
        self._keyword_search = QueryItem("st", "")
        self._categories = QueryItem("c", GoodWillCategories.Empty)
        self._good_will_location = QueryItem("s", GoodWillLocations.Empty)
        self._low_price = QueryItem("lp", 0)
        self._high_price = QueryItem("hp", 999999)
        self._show_buy_now_only = QueryItem("sbn", False)
        self._show_pick_up_only = QueryItem("spo", False)
        self._hide_pick_up_only = QueryItem("snpo", False)
        self._show_one_cent_ship_only = QueryItem("socs", False)
        self._search_description = QueryItem("sd", True)
        self._show_closed_auctions = QueryItem("sca", False)
        self._closed_auction_end_date = QueryItem("caed", '11/14/2018')
        self._day_back = QueryItem("cadb", 9)
        self._search_canada = QueryItem("scs", False)
        self._search_international = QueryItem("sis", False)
        self._field_order = QueryItem("col", 0)
        self._page_number = QueryItem("p", 0)
        self._page_size = QueryItem("ps", 40)
        self._short_description = QueryItem("desc", True)
        self._saved_search_id = QueryItem("ss", 0)
        self._use_buyer_preferences = QueryItem("UseBuyerPrefs", True)

    def load_json_search_file(self, filename):
        with open(filename) as json_file:
            json_data = json.load(json_file)
            self.search_params_by_json(json_data)

    def search_params_by_json(self, json_data):
        if 'keyword_search' in json_data:
            self.keyword_search = json_data['keyword_search']
        if 'search_gallery' in json_data:
            self._search_gallery.value_set(GoodWillSearchGallery(json_data['search_gallery']))
        if 'categories' in json_data:
            self._categories.value_set(GoodWillCategories(json_data['categories']))
        if 'good_will_location' in json_data:
            self._good_will_location.value_set(GoodWillLocations(json_data['good_will_location']))
        if 'low_price' in json_data:
            self._low_price.value_set(json_data['low_price'])
        if 'high_price' in json_data:
            self._high_price.value_set(json_data['high_price'])
        if 'show_buy_now_only' in json_data:
            self._show_buy_now_only.value_set(json_data['show_buy_now_only'])
        if 'show_pick_up_only' in json_data:
            self._show_pick_up_only.value_set(json_data['show_pick_up_only'])
        if 'hide_pick_up_only' in json_data:
            self._hide_pick_up_only.value_set(json_data['hide_pick_up_only'])
        if 'show_one_cent_ship_only' in json_data:
            self._show_one_cent_ship_only.value_set(json_data['show_one_cent_ship_only'])
        if 'search_description' in json_data:
            self._search_description.value_set(json_data['search_description'])
        if 'show_closed_auctions' in json_data:
            self._show_closed_auctions.value_set(json_data['show_closed_auctions'])
        if 'closed_auction_end_date' in json_data:
            self._closed_auction_end_date.value_set(json_data['closed_auction_end_date'])
        if 'day_back' in json_data:
            self._day_back.value_set(json_data['day_back'])
        if 'search_canada' in json_data:
            self._search_canada.value_set(json_data['search_canada'])
        if 'search_international' in json_data:
            self._search_international.value_set(json_data['search_international'])
        if 'field_order' in json_data:
            self._field_order.value_set(json_data['field_order'])
        if 'page_number' in json_data:
            self._page_number.value_set(json_data['page_number'])
        if 'page_size' in json_data:
            self._page_size.value_set(json_data['page_size'])
        if 'short_description' in json_data:
            self._short_description.value_set(json_data['short_description'])
        if 'saved_search_id' in json_data:
            self._saved_search_id.value_set(json_data['saved_search_id'])

    def print_search_params(self):
        print(f'url: {self.url}')
        print(f'search_gallery: {self._search_gallery.get_value()}')
        print(f'keyword_search: {self._keyword_search.get_value()}')
        print(f'categories: {self._categories.get_value()}')
        print(f'good_will_location: {self._good_will_location.get_value()}')
        print(f'low_price: {self._low_price.get_value()}')
        print(f'high_price: {self._high_price.get_value()}')
        print(f'show_buy_now_only: {self._show_buy_now_only.get_value()}')
        print(f'show_pick_up_only: {self._show_pick_up_only.get_value()}')
        print(f'hide_pick_up_only: {self._hide_pick_up_only.get_value()}')
        print(f'show_one_cent_ship_only: {self._show_one_cent_ship_only.get_value()}')
        print(f'search_description: {self._search_description.get_value()}')
        print(f'show_closed_auctions: {self._show_closed_auctions.get_value()}')
        print(f'closed_auction_end_date: {self._closed_auction_end_date.get_value()}')
        print(f'day_back: {self._day_back.get_value()}')
        print(f'search_canada: {self._search_canada.get_value()}')
        print(f'search_international: {self._search_international.get_value()}')
        print(f'field_order: {self._field_order.get_value()}')
        print(f'page_number: {self._page_number.get_value()}')
        print(f'page_size: {self._page_size.get_value()}')
        print(f'short_description: {self._short_description.get_value()}')
        print(f'saved_search_id: {self._saved_search_id.get_value()}')
        print(f'use_buyer_preferences: {self._use_buyer_preferences.get_value()}')


    def search(self, keyword_search: str):
        self.keyword_search = keyword_search
        return self.parse_results(requests.get(self.search_url()).text)

    def search_multiple(self, keyword_search: set[str]):
        goodWillProducts = []
        for keyword in keyword_search:
            goodWillProducts.extend(self.search(keyword))

        return goodWillProducts

    def parse_results(self, response):
        goodWillProducts = []
        soup = BeautifulSoup(response, 'html.parser')
        products = soup.find_all('span', {'class': 'data-container'})
        for product in products:
            goodWillProduct = GoodWillProduct(product, self.time_zone)
            goodWillProduct.print_product()
            goodWillProducts.append(goodWillProduct)

        return goodWillProducts

    def query_string(self):
        query_string = "?"
        for attrib, value in self.__dict__.items():
            if isinstance(value, QueryItem):
                query_string += f'{value.query_string_value()}&'

        return query_string.rstrip('&')

    def search_url(self):
        return self.url + self.query_string()

    @property
    def search_gallery(self):
        return self._search_gallery.get_value()

    @search_gallery.setter
    def search_gallery(self, value: GoodWillSearchGallery):
        self._search_gallery.value_set(value)

    @property
    def keyword_search(self):
        return self._keyword_search.get_value()

    @keyword_search.setter
    def keyword_search(self, value: str):
        self._keyword_search.value_set(value)

    @property
    def categories(self):
        return self._categories.get_value()

    @categories.setter
    def categories(self, value: GoodWillCategories):
        self._categories.value_set(value)

    @property
    def good_will_location(self):
        return self._good_will_location.get_value()

    @good_will_location.setter
    def good_will_location(self, value: GoodWillLocations):
        self._good_will_location.value_set(value)

    @property
    def low_price(self):
        return self._low_price.get_value()

    @low_price.setter
    def low_price(self, value: int):
        self._low_price.value_set(value)

    @property
    def high_price(self):
        return self._high_price.get_value()

    @high_price.setter
    def high_price(self, value: int):
        self._high_price.value_set(value)

    @property
    def show_buy_now_only(self):
        return self._show_buy_now_only.get_value()

    @show_buy_now_only.setter
    def show_buy_now_only(self, value: bool):
        self._show_buy_now_only.value_set(value)

    @property
    def show_pick_up_only(self):
        return self._show_pick_up_only.get_value()

    @show_pick_up_only.setter
    def show_pick_up_only(self, value: bool):
        self._show_pick_up_only.value_set(value)

    @property
    def hide_pick_up_only(self):
        return self._hide_pick_up_only.get_value()

    @hide_pick_up_only.setter
    def hide_pick_up_only(self, value: bool):
        self._hide_pick_up_only.value_set(value)

    @property
    def show_one_cent_ship_only(self):
        return self._show_one_cent_ship_only.get_value()

    @show_one_cent_ship_only.setter
    def show_one_cent_ship_only(self, value: bool):
        self._show_one_cent_ship_only.value_set(value)

    @property
    def search_description(self):
        return self._search_description.get_value()

    @search_description.setter
    def search_description(self, value: bool):
        self._search_description.value_set(value)

    @property
    def show_closed_auctions(self):
        return self._show_closed_auctions.get_value()

    @show_closed_auctions.setter
    def show_closed_auctions(self, value: bool):
        self._show_closed_auctions.value_set(value)

    @property
    def closed_auction_end_date(self):
        return self._closed_auction_end_date.get_value()

    @closed_auction_end_date.setter
    def closed_auction_end_date(self, value: datetime):
        self._closed_auction_end_date.value_set(value)

    @property
    def day_back(self):
        return self._day_back.get_value()

    @day_back.setter
    def day_back(self, value: int):
        self._day_back.value_set(value)

    @property
    def search_canada(self):
        return self._search_canada.get_value()

    @search_canada.setter
    def search_canada(self, value: bool):
        self._search_canada.value_set(value)

    @property
    def search_international(self):
        return self._search_international.get_value()

    @search_international.setter
    def search_international(self, value: bool):
        self._search_international.value_set(value)

    @property
    def page_number(self):
        return self._page_number.get_value()

    @page_number.setter
    def page_number(self, value: int):
        self._page_number.value_set(value)

    @property
    def page_size(self):
        return self._page_size.get_value()

    @page_size.setter
    def page_size(self, value: int):
        self._page_size.value_set(value)

    @property
    def short_description(self):
        return self._short_description.get_value()

    @short_description.setter
    def short_description(self, value: bool):
        self._short_description.value_set(value)

    @property
    def saved_search_id(self):
        return self._saved_search_id.get_value()

    @saved_search_id.setter
    def saved_search_id(self, value: int):
        self._saved_search_id.value_set(value)

    @property
    def use_buyer_preferences(self):
        return self._use_buyer_preferences.get_value()

    @use_buyer_preferences.setter
    def use_buyer_preferences(self, value: bool):
        self._use_buyer_preferences.value_set(value)
