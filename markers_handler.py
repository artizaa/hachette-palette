from telebot import types
from markers import Markers
from user_markers_db import UserMarkersDB
from language_module import tr, get_user_lang
from user_state import UserStateDB


class MarkersHandler:
    def __init__(self, bot):
        self.bot = bot
        self.markers = Markers()
        self.markers_db = UserMarkersDB()
        self.user_state_db = UserStateDB()

    def show_markers_menu(self, message):
        chat_id = message.chat.id
        lang = get_user_lang(message)

        self.user_state_db.save_state(chat_id, state="choose_markers")
        selected_markers = self.markers_db.load_marker_state(chat_id) or {}
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

        for marker in self.markers.get_options():
            if marker == "Languo Series":
                is_selected = self.markers_db.has_selected_series(chat_id)
            else:
                is_selected = selected_markers.get(marker, False)
            btn_text = f"✅ {marker}" if is_selected else marker
            markup.add(types.KeyboardButton(btn_text))

        markup.add(types.KeyboardButton(tr("btn_back", lang)))

        self.bot.send_message(
            chat_id,
            tr("choose_markers", lang),
            reply_markup=markup
        )

    def show_languo_series_menu(self, chat_id, lang):
        selected_series = self.markers_db.load_marker_series(chat_id) or {}

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

        # кнопка "Выбрать все"
        markup.add(types.KeyboardButton(tr("btn_select_all", lang)))

        # список всех серий
        for series_name in self.markers.series_ranges:
            name = series_name[3]
            is_selected = selected_series.get(name, False)
            btn_text = f"✅ {name}" if is_selected else name
            markup.add(types.KeyboardButton(btn_text))

        # кнопка "Назад"
        markup.add(types.KeyboardButton(tr("btn_back", lang)))

        self.bot.send_message(
            chat_id,
            tr("choose_languo_series", lang),
            reply_markup=markup
        )

    def handle_marker_selection(self, message):
        chat_id = message.chat.id
        lang = get_user_lang(message)
        text = message.text.strip()

        # --- Назад в главное меню ---
        if text == tr("btn_back", lang):
            self.user_state_db.save_state(chat_id, state="main_menu")
            return {"handled": True, "action": "back"}

        # --- Проверяем, что текст — это допустимый маркер ---
        valid_markers = self.markers.get_options()
        if text.replace("✅ ", "").strip() not in valid_markers:
            # Игнорируем или выводим сообщение об ошибке
            self.bot.send_message(chat_id, tr("invalid_input", lang))
            return {"handled": True, "action": None}

        marker_name = text.replace("✅ ", "").strip()
        selected_markers = self.markers_db.load_marker_state(chat_id)

        if marker_name == "Languo Series":
            self.user_state_db.save_state(chat_id, state="choose_languo_series")
            self.show_languo_series_menu(chat_id, lang)
            return {"handled": True, "action": None}

        # --- переключаем состояние маркера ---
        current_state = selected_markers.get(marker_name, False)
        selected_markers[marker_name] = not current_state
        marker_type = self.markers.get_marker_type(marker_name)

        self.markers_db.save_marker_state(
            chat_id,
            marker_name,
            marker_type,
            selected_markers[marker_name]
        )

        self.show_markers_menu(message)
        return {"handled": True, "action": None}

    def handle_languo_series_selection(self, message):
        chat_id = message.chat.id
        lang = get_user_lang(message)
        text = message.text.strip()

        if text == tr("btn_back", lang):
            self.user_state_db.save_state(chat_id, "choose_markers")
            self.show_markers_menu(message)
            return {"handled": True, "action": "back"}

        if text == tr("btn_select_all", lang):
            # выбираем все серии
            for _, _, _, series_name in self.markers.series_ranges:
                self.markers_db.save_marker_series(chat_id, "Languo Series", "brush", series_name, True)
            self.show_languo_series_menu(chat_id, lang)
            return {"handled": True, "action": None}

        # убираем галочку если есть
        series_name = text.replace("✅ ", "").strip()

        # текущее состояние серий
        series_state = self.markers_db.load_marker_series(chat_id)
        current_selected = series_state.get(series_name, False)
        marker_type = self.markers.get_marker_type("Languo Series")

        # сохраняем новое состояние
        self.markers_db.save_marker_series(
            chat_id=chat_id,
            marker_name="Languo Series",
            marker_type=marker_type,
            series=series_name,
            selected=not current_selected
        )

        # перерисовываем меню серий
        self.show_languo_series_menu(chat_id, lang)

        return {"action": None}