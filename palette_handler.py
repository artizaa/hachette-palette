from telebot import types

from coloring_book import ColoringBook
from language_module import tr, get_user_lang
from markers import Markers
from user_markers_db import UserMarkersDB
from user_state import UserStateDB
from palette_visualizer import PaletteVisualizer

class PaletteHandler:
    def __init__(self, bot):
        self.bot = bot
        self.coloring = ColoringBook()
        self.markers = Markers()

        self.visualizer = PaletteVisualizer()
        self.db = UserStateDB()
        self.db_markers = UserMarkersDB()

    def show_books(self, message):
        lang = get_user_lang(message)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for book in self.coloring.get_books():
            markup.add(types.KeyboardButton(book))
        markup.add(types.KeyboardButton(tr("btn_back", lang)))

        self.bot.send_message(
            message.chat.id,
            tr("choose_coloring_book", lang),
            reply_markup=markup
        )

        self.db.save_state(message.chat.id, state="choose_book", book=None, page=None)

    def handle_message(self, message):
        chat_id = message.chat.id
        text = message.text
        lang = get_user_lang(message)

        state_data = self.db.load_state(chat_id) or {"state": "main_menu", "book": None, "page": None}
        current_state = state_data["state"]
        current_book = state_data["book"]
        current_page = state_data["page"]

        # --- Нажали "назад" ---
        if text == tr("btn_back", lang):
            self.db.save_state(chat_id, state="main_menu", book=None, page=None)
            return {"handled": True, "action": "back"}

        # --- Выбор книги ---
        if current_state == "choose_book":
            # Пользователь выбрал другую книгу
            if text in self.coloring.get_books():
                pages = self.coloring.get_pages(text)
                self.db.save_state(chat_id, state="choose_book", book=text, page=None)
                self.bot.send_message(
                    chat_id,
                    tr("enter_page_number", lang, book=text, pages=pages)
                )
                return {"handled": True, "action": None}

            # Пользователь ввёл страницу
            if current_book is None:
                # Книга ещё не выбрана
                self.bot.send_message(chat_id, tr("invalid_coloring_book", lang))
                return {"handled": True, "action": None}

            try:
                page = int(text)
                max_pages = self.coloring.get_pages(current_book)
                if 1 <= page <= max_pages:
                    self.db.save_state(chat_id, state="choose_book", book=current_book, page=page)
                    self.bot.send_message(
                        chat_id,
                        tr("ok_page_selected", lang, page=page, book=current_book)
                    )

                    # --- Асинхронный запуск генерации картинки ---
                    #threading.Thread(target=self.generate_and_send_image, args=(chat_id, current_book, page)).start()
                    self.generate_and_send_image(chat_id, current_book, page)

                    return {"handled": True, "action": None}
                else:
                    self.bot.send_message(chat_id, tr("enter_page_number", lang, book=current_book, pages=max_pages))
                    return {"handled": True, "action": None}
            except ValueError:
                self.bot.send_message(chat_id, tr("invalid_number", lang))
                return {"handled": True, "action": None}

        # main_menu или другие стадии
        return {"handled": False, "action": None}

    def generate_and_send_image(self, chat_id, book, page, lang="en"):
        """
        Генерация LPIPS-картинки и отправка пользователю.
        lang передаем явно, чтобы не пытаться получить его через get_chat
        """
        rows_colors_dict_all = self.coloring.load_dictionary(book)
        page_key = str(page)

        if page_key not in rows_colors_dict_all:
            self.bot.send_message(chat_id, tr("colors_not_found", lang, page=page))
            return

        rows_colors = rows_colors_dict_all[page_key]

        # --- загрузка маркерных словарей, выбранных пользователем ---
        user_markers = self.db_markers.load_marker_state(chat_id) or {}
        user_languo_series = self.db_markers.load_marker_series(chat_id) or {}
        marker_dict = self.markers.load_selected_markers(user_markers, user_languo_series)

        if not marker_dict:
            self.bot.send_message(chat_id, tr("no_markers_selected", lang))
            return

        img = self.visualizer.create_lpips_image_for_page(rows_colors, marker_dict, top_n=3)

        from io import BytesIO
        bio = BytesIO()
        img.save(bio, format="PNG")
        bio.seek(0)
        self.bot.send_photo(chat_id, bio)

        self.bot.send_message(chat_id, tr("ok_page_selected", lang, page=page, book=book))

