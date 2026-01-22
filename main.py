from pathlib import Path

from tzlocal import get_localzone

from GoodWillShoppingSearch.models.goodwillsearch import GoodWillSearch


def main():
    search_by_json_files()


def search_by_json_files():
    timezone = get_localzone()
    searches_path = Path(__file__).parent / 'saved_searches'

    for json_file in searches_path.glob('*.json'):
        search = GoodWillSearch(timezone, str(json_file))
        search.print_search_params()
        if search.keyword_search:
            search.search(search.keyword_search)
        else:
            print("No keyword search specified in the JSON file.")


if __name__ == '__main__':
    main()