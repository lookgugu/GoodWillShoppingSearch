import enum


class QueryItem:
    def __init__(self, query_string: str, value):
        self.query_string = query_string
        self.value_set(value)

    def query_string_value(self):
        return f'{self.query_string}={self.get_value()}'

    def value_set(self, query_value):
        self.query_value = query_value

    def get_value(self):
        if type(self.query_value) is str:
            return self.query_value.lower()
        elif isinstance(self.query_value, enum.Enum):
            return str(self.query_value.value)
        else:
            return str(self.query_value).lower()