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
            is_selected = selected_markers.get(marker, False)
            btn_text = f"✅ {marker}" if is_selected else marker
            markup.add(types.KeyboardButton(btn_text))

        markup.add(types.KeyboardButton(tr("btn_back", lang)))

        self.bot.send_message(
            chat_id,
            tr("choose_markers", lang),
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

        marker_name = text.replace("✅ ", "").strip()
        selected_markers = self.markers_db.load_marker_state(chat_id)

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
