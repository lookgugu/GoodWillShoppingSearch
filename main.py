import os
from tzlocal import get_localzone
from GoodWillShoppingSearch.models.goodwillsearch import GoodWillSearch


def main():
    search_byjson()
    run_search()


def search_byjson():
    SGW_TIMEZONE = get_localzone()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    searchJson = os.path.join(dir_path, 'austincomputer.json')
    search = GoodWillSearch(SGW_TIMEZONE, searchJson)
    search.print_search_params()
    search.search("dell")
    # print(search.search_url())


def run_search():
    SGW_TIMEZONE = get_localzone()
    search = GoodWillSearch(SGW_TIMEZONE)

    products = {
        "rack mount",
        "wyze",
        "tiffany",
        "google home hub",
        "ryzen",
        "amd",
        "radeon"
    }

    results = search.search_multiple(products)

    for result in results:
        result.print_product()


if __name__ == '__main__':
    main()