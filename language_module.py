from typing import Optional

# Словарь переводов только на английский и русский
translations = {
    "start_message": {
        "en": "Hello! I'm your friendly palette bot ✨",
        "ru": "Добро пожаловать в бот по подбору палитр к раскраскам Hachette ✨"
    },
    "choose_action": {
        "en": "Choose an action from the menu:",
        "ru": "Выберите действие из меню:"
    },
    "btn_choose_markers": {
        "en": "🎨 Choose Markers",
        "ru": "🎨 Выбрать маркеры"
    },
    "btn_pick_palette": {
        "en": "🌈 Pick a Palette",
        "ru": "🌈 Подобрать палитру"
    },
    "btn_support": {
        "en": "💖 Support",
        "ru": "💖 Поддержать"
    },
    "btn_back": {
        "en": "⬅️ Back",
        "ru": "⬅️ Назад"
    },
    "choose_coloring_book": {
        "en": "Choose a coloring book:",
        "ru": "Выберите раскраску:"
    },
    "enter_page_number": {
        "en": "You selected {book}. Enter a number from 1 to {pages}",
        "ru": "Вы выбрали раскраску {book}. Введите число от 1 до {pages}"
    },
    "ok_page_selected": {
        "en": "OK! You selected page {page} from coloring book '{book}' ✅",
        "ru": "Ок! Вы выбрали страницу {page} из раскраски '{book}' ✅"
    },
    "invalid_coloring_book": {
        "en": "Please select a coloring book from the list or press ⬅️ Back",
        "ru": "Выберите раскраску из списка или нажмите ⬅️ Назад"
    },
    "invalid_number": {
        "en": "Please enter a number, not text!",
        "ru": "Введите число, а не текст!"
    },
    "colors_not_found": {
        "en": "Colors for page {page} not found.",
        "ru": "Цвета для страницы {page} не найдены."
    },
    "thank_you_support": {
        "en": "Thank you for your support! 🙏",
        "ru": "Спасибо за поддержку! 🙏"
    },
    "invalid_input": {
        "en": "Please use the menu buttons 👇",
        "ru": "Пожалуйста, используйте кнопки меню 👇"
    },
    "choose_markers": {
        "en": "Please select markers from the list or press ⬅️ Back",
        "ru": "Выберите маркеры из списка или нажмите ⬅️ Назад"
    },
    "no_markers_selected": {
        "en": "No markers selected. Please choose at least one marker from the list.",
        "ru": "Маркеры не выбраны. Пожалуйста, выберите хотя бы один маркер из списка."
    }
}


def tr(key: str, lang: Optional[str] = "en", **kwargs) -> str:
    """
    Возвращает перевод по ключу key для заданного языка lang.
    kwargs используется для форматирования строки.
    """
    if key not in translations:
        return key  # если ключ не найден, возвращаем его как есть

    text = translations[key].get(lang, translations[key].get("en", key))
    return text.format(**kwargs)

def get_user_lang(message) -> str:
    """Определяет язык пользователя, возвращает 'en' или 'ru'"""
    lang = getattr(message.from_user, "language_code", "en")
    if lang not in ["en", "ru"]:
        lang = "en"
    return lang