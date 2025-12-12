import json

class ColoringBook:
    def __init__(self):
        # книги: название -> {pages, dict_file}
        self.books = {
            "Love Stories": {"pages": 99, "dict_file": "coloring_books/love_dict.json"},
            "Family": {"pages": 100, "dict_file": "coloring_books/family_dict.json"},
            "Petites Princesses": {"pages": 50, "dict_file": "coloring_books/petites_princesses_dict.json"},
            "Heroes vs Mechants": {"pages": 100, "dict_file": "coloring_books/heroes_vs_mechants_dict.json"},
            "Loony Tunes 1": {"pages": 100, "dict_file": "coloring_books/loony1_dict.json"},
            "Loony Tunes 2": {"pages": 100, "dict_file": "coloring_books/loony2_dict.json"},
        }

    def get_books(self):
        """Вернёт список доступных книг"""
        return list(self.books.keys())

    def get_pages(self, book_name):
        """Вернёт количество страниц для конкретной раскраски"""
        return self.books.get(book_name, {}).get("pages", 0)

    def load_dictionary(self, book_name):
        """Загружает словарь цветов для конкретной книги"""
        dict_file = self.books.get(book_name, {}).get("dict_file")
        if not dict_file:
            raise ValueError(f"Неизвестная книга: {book_name}")
        with open(dict_file, "r", encoding="utf-8") as f:
            return json.load(f)
