import telebot
from telebot import types

from markers_handler import MarkersHandler
from language_module import tr, get_user_lang
from palette_handler import PaletteHandler
from config import TOKEN

bot = telebot.TeleBot(TOKEN)

palette_handler = PaletteHandler(bot)
markers_handler = MarkersHandler(bot)

def show_main_menu(message):
    chat_id = message.chat.id
    lang = get_user_lang(message)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(tr("btn_choose_markers", lang))
    btn2 = types.KeyboardButton(tr("btn_pick_palette", lang))
    btn3 = types.KeyboardButton(tr("btn_support", lang))
    markup.add(btn1, btn2, btn3)

    bot.send_message(chat_id, tr("choose_action", lang), reply_markup=markup)
    # Сохраняем состояние
    markers_handler.user_state_db.save_state(chat_id, "main_menu")

@bot.message_handler(commands=['start'])
def start(message):
    # Показываем главное меню
    show_main_menu(message)


@bot.message_handler(func=lambda message: True)
def menu(message):
    chat_id = message.chat.id
    lang = get_user_lang(message)

    state_data = markers_handler.user_state_db.load_state(chat_id) or {"state": "main_menu"}
    current_state = state_data["state"]

    # Главное меню
    if current_state == "main_menu":
        if message.text == tr("btn_choose_markers", lang):
            markers_handler.show_markers_menu(message)
            return
        elif message.text == tr("btn_pick_palette", lang):
            palette_handler.show_books(message)
            return
        elif message.text == tr("btn_support", lang):
            bot.send_message(chat_id, tr("thank_you_support", lang))
            return
        else:
            bot.send_message(chat_id, tr("invalid_input", lang))
            return

    # Выбор маркеров
    if current_state == "choose_markers":
        res = markers_handler.handle_marker_selection(message)
        if res.get("action") == "back":
            show_main_menu(message)
            markers_handler.user_state_db.save_state(chat_id, "main_menu")
        return

    # Выбор книги/страницы
    if current_state in ["choose_book", "choose_page"]:
        res = palette_handler.handle_message(message)
        if res.get("action") == "back":
            show_main_menu(message)
            markers_handler.user_state_db.save_state(chat_id, "main_menu")
        return

    if current_state == "choose_languo_series":
        res = markers_handler.handle_languo_series_selection(message)
        if res.get("action") == "back":
            markers_handler.show_markers_menu(message)
            markers_handler.user_state_db.save_state(chat_id, "choose_markers")
        return

print("Бот запущен...")
bot.infinity_polling()
