import os
from tzlocal import get_localzone
from GoodWillShoppingSearch.models.goodwillsearch import GoodWillSearch


def main():
    search_by_json_files()


def search_by_json_files():
    SGW_TIMEZONE = get_localzone()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    searches_path = os.path.join(dir_path, 'saved_searches')
    for filename in os.listdir(searches_path):
        if filename.endswith('.json'):
            search_json_file = os.path.join(searches_path, filename)
            search = GoodWillSearch(SGW_TIMEZONE, search_json_file)
            search.print_search_params()
            if search.keyword_search:
                search.search(search.keyword_search)
            else:
                print("No keyword search specified in the JSON file.")


if __name__ == '__main__':
    main()