import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest

# ═══════════════════════════════════════════════════════════════
#                    НАСТРОЙКИ БОТА
# ═══════════════════════════════════════════════════════════════

BOT_TOKEN = "8651295072:AAGGtuMtdI9dv_WrFPDgclA1b_xBR4PSSWM"
ADMIN_ID = 8672112132

# === FILE_ID КАРТИНОК (для экранов) ===
PHOTO_MAIN = "AgACAgIAAxkBAAOtaqgFb9jdIGgOEVmhSCKQdduvEl4AAsQfaxuPZUBJpS7q7CFEAAG8AQADAgADeAADPQQ"
PHOTO_ZAPIS = "AgACAgIAAxkBAAO1aqgbVVIQv8zhLofcL7uCjP210gQAAgQhaxuPZUhJCsivtHvjmrIBAAMCAAN5AAM9BA"
PHOTO_INFO = "AgACAgIAAxkBAAIBHmqo2cvLB8tJPaNUGyshUMwPAcHnAAKCI2sbj2VISdFVZjYLOlf4AQADAgADeAADPQQ"
PHOTO_CHANNELS = "AgACAgIAAxkBAAIBIGqo2i5Hi0WXWzui2DHoH-x08fxyAAKEI2sbj2VISVMUHjfOSy2_AQADAgADeAADPQQ"

# ═══════════════════════════════════════════════════════════════
#                    ОБЪЕКТЫ
# ═══════════════════════════════════════════════════════════════

OBJECTS = [
    {
        "photo": "AgACAgIAAxkBAAIBt2qpEfWHHz2W9oFo1IQ-FgtKtmpmAAIUNWsboAFJSe54_NyHIF6zAQADAgADeQADPQQ",
        "area": "43.5 м²",
        "address": "Ленинский 72 к1",
        "rooms": "1-комнатная",
        "link": "https://www.avito.ru/sankt-peterburg/kvartiry/1-k._kvartira_435_m_1114_et._8292024879?utm_campaign=native&utm_medium=item_page_android&utm_source=soc_sharing_seller",
    },
    {
        "photo": "AgACAgIAAxkBAAIBsmqpEVmdphe4janaEK9UAuFzhtjwAAISNWsboAFJSSZcRg3i6gTaAQADAgADeQADPQQ",
        "area": "44.6 м²",
        "address": "Пр. Энергетиков 66 к2",
        "rooms": "2-комнатная",
        "link": "https://www.avito.ru/sankt-peterburg/kvartiry/2-k._kvartira_446_m_45_et._8324266300?utm_campaign=native&utm_medium=item_page_android&utm_source=soc_sharing_seller",
    },
]

# ═══════════════════════════════════════════════════════════════
#                    ТЕКСТЫ
# ═══════════════════════════════════════════════════════════════

WELCOME_TEXT = (
    "<b>Здравствуйте!</b>\n\n"
    "Я помощник Марии, который создан на случай, если она занята.\n\n"
    "Так же здесь есть информация о ней."
)

INFO_TEXT = (
    "<b>Недвижимость</b> — моя профессия и пространство, где я умею видеть больше, чем стены и квадратные метры.\n\n"
    "Я работаю в сфере недвижимости <b>более 12 лет</b>: помогаю покупать, продавать и инвестировать. "
    "Знаю специфику семейных сделок и элитного сегмента, умею находить решения в нестандартных ситуациях.\n\n"
    "Моя география — <b>Санкт-Петербург, регионы России и зарубежные направления</b>.\n\n"
    "Я работаю с теми, кто ценит время, комфорт и качество. Помогаю подобрать недвижимость под цели, "
    "образ жизни и финансовые планы — от семейной квартиры и продажи дорогих объектов до переезда, "
    "ипотеки и сложных юридических вопросов.\n\n"
    "Отдельное направление — <b>страхование</b>: дом, квартира, автомобиль, здоровье и ипотека.\n\n"
    "Я считаю, что хороший специалист не просто закрывает сделку. Он умеет слышать, анализировать, "
    "предупреждать о рисках и быть рядом, когда особенно важно принять правильное решение.\n\n"
    "<b>Я — Мария. И я знаю, как находить возможности в недвижимости.</b>"
)

CHANNELS_TEXT = "📢 <b>Каналы:</b>"

ROLE_TEXT = "Выберите свою роль:"
ENTER_TEXT = "Введите текст."
ERROR_TEXT = "❌ Ошибка: сообщение не верно.\n\nПожалуйста, используйте кнопки в меню."

THANKS_TEXT = "✅ Спасибо! Ваше сообщение передано Марии.\nМы свяжемся с вами в ближайшее время."

# ═══════════════════════════════════════════════════════════════
#                    ИНИЦИАЛИЗАЦИЯ
# ═══════════════════════════════════════════════════════════════

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

class Form(StatesGroup):
    waiting_for_message = State()

# ═══════════════════════════════════════════════════════════════
#                    КЛАВИАТУРЫ
# ═══════════════════════════════════════════════════════════════

def get_main_menu():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Запись", callback_data="zapis", style="success"),
    )
    builder.row(
        InlineKeyboardButton(text="Информация", callback_data="info", style="primary"),
    )
    builder.row(
        InlineKeyboardButton(text="Объекты", callback_data="objects_0", style="success"),
    )
    builder.row(
        InlineKeyboardButton(text="Каналы", callback_data="channels", style="danger"),
    )
    return builder.as_markup()

def get_role_menu():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Покупатель", callback_data="role_buyer", style="danger"),
        InlineKeyboardButton(text="Продавец", callback_data="role_seller", style="primary"),
    )
    builder.row(
        InlineKeyboardButton(text="Назад", callback_data="back_to_main", style="danger"),
    )
    return builder.as_markup()

def get_exit_menu():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Выход в главное меню", callback_data="back_to_main", style="success"),
    )
    return builder.as_markup()

def get_back_to_main_menu():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Назад", callback_data="back_to_main", style="danger"),
    )
    return builder.as_markup()

def get_channels_menu():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Хочу Домой", url="https://t.me/hoch_fomoji", style="success"),
    )
    builder.row(
        InlineKeyboardButton(text="Камбоджа с Марией", url="https://t.me/Serenko_Combodja", style="primary"),
    )
    builder.row(
        InlineKeyboardButton(text="Назад", callback_data="back_to_main", style="danger"),
    )
    return builder.as_markup()

def get_object_menu(index: int, link: str):
    total = len(OBJECTS)
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔗 Открыть объявление", url=link, style="success"),
    )
    builder.row(
        InlineKeyboardButton(text="⬅️", callback_data=f"objects_{index - 1}"),
        InlineKeyboardButton(text=f"{index + 1}/{total}", callback_data="noop"),
        InlineKeyboardButton(text="➡️", callback_data=f"objects_{index + 1}"),
    )
    builder.row(
        InlineKeyboardButton(text="Назад", callback_data="back_to_main", style="danger"),
    )
    return builder.as_markup()

# ═══════════════════════════════════════════════════════════════
#                    ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ═══════════════════════════════════════════════════════════════

async def safe_delete(message: types.Message):
    try:
        await message.delete()
    except Exception:
        pass

def get_object_text(obj: dict) -> str:
    return (
        f"🏠 <b>{obj['rooms']}</b>\n\n"
        f"📐 <b>{obj['area']}</b>\n\n"
        f"📍 <b>{obj['address']}</b>"
    )

async def send_screen(callback: types.CallbackQuery, photo: str, caption: str, markup=None, parse_mode=None):
    await safe_delete(callback.message)
    try:
        await callback.message.answer_photo(
            photo=photo,
            caption=caption,
            reply_markup=markup,
            parse_mode=parse_mode
        )
    except TelegramBadRequest as e:
        logging.error(f"Ошибка отправки картинки: {e}")
        await callback.message.answer(
            text=caption,
            reply_markup=markup,
            parse_mode=parse_mode
        )

# ═══════════════════════════════════════════════════════════════
#                    ХЭНДЛЕРЫ
# ═══════════════════════════════════════════════════════════════

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer_photo(
        photo=PHOTO_MAIN,
        caption=WELCOME_TEXT,
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )

@dp.callback_query(F.data == "info")
async def show_info(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await send_screen(
        callback=callback,
        photo=PHOTO_INFO,
        caption=INFO_TEXT,
        markup=get_back_to_main_menu(),
        parse_mode="HTML"
    )
    await callback.answer()

@dp.callback_query(F.data == "channels")
async def show_channels(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await send_screen(
        callback=callback,
        photo=PHOTO_CHANNELS,
        caption=CHANNELS_TEXT,
        markup=get_channels_menu(),
        parse_mode="HTML"
    )
    await callback.answer()

@dp.callback_query(F.data == "zapis")
async def show_roles(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await send_screen(
        callback=callback,
        photo=PHOTO_ZAPIS,
        caption=ROLE_TEXT,
        markup=get_role_menu()
    )
    await callback.answer()

@dp.callback_query(F.data.in_({"role_seller", "role_buyer"}))
async def choose_role(callback: types.CallbackQuery, state: FSMContext):
    role = "Продавец" if callback.data == "role_seller" else "Покупатель"
    await state.update_data(role=role)
    
    await safe_delete(callback.message)
    await callback.message.answer(ENTER_TEXT)
    await state.set_state(Form.waiting_for_message)
    await callback.answer()

@dp.message(Form.waiting_for_message)
async def process_message(message: types.Message, state: FSMContext):
    data = await state.get_data()
    role = data.get("role", "Не указана")
    
    if not message.text:
        await message.answer(ERROR_TEXT)
        return
    
    user_text = message.text
    user_name = message.from_user.full_name
    user_username = f"@{message.from_user.username}" if message.from_user.username else "нет username"
    
    admin_text = (
        f"🔔 <b>НОВАЯ ЗАЯВКА!</b>\n\n"
        f"👤 Роль: <b>{role}</b>\n"
        f"🙍 От: {user_name} ({user_username})\n"
        f"🆔 ID: <code>{message.from_user.id}</code>\n\n"
        f"💬 Сообщение:\n{user_text}"
    )
    
    try:
        await bot.send_message(chat_id=ADMIN_ID, text=admin_text, parse_mode="HTML")
    except Exception as e:
        logging.error(f"Ошибка отправки админу: {e}")
    
    await message.answer(
        THANKS_TEXT,
        reply_markup=get_exit_menu()
    )
    await state.clear()

# === ОБЪЕКТЫ: листание ===
@dp.callback_query(F.data.startswith("objects_"))
async def show_object(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    total = len(OBJECTS)
    try:
        index = int(callback.data.split("_")[1])
    except (ValueError, IndexError):
        index = 0
    
    if index < 0:
        index = total - 1
    elif index >= total:
        index = 0
    
    obj = OBJECTS[index]
    await send_screen(
        callback=callback,
        photo=obj["photo"],
        caption=get_object_text(obj),
        markup=get_object_menu(index, obj["link"]),
        parse_mode="HTML"
    )
    await callback.answer()

@dp.callback_query(F.data == "noop")
async def noop(callback: types.CallbackQuery):
    await callback.answer()

# === НАЗАД В ГЛАВНОЕ ===
@dp.callback_query(F.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await send_screen(
        callback=callback,
        photo=PHOTO_MAIN,
        caption=WELCOME_TEXT,
        markup=get_main_menu(),
        parse_mode="HTML"
    )
    await callback.answer()

# ═══════════════════════════════════════════════════════════════
#   FALLBACK
# ═══════════════════════════════════════════════════════════════

@dp.message()
async def fallback_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None:
        return
    
    await message.answer(ERROR_TEXT)

# ═══════════════════════════════════════════════════════════════
#                    ЗАПУСК
# ═══════════════════════════════════════════════════════════════

async def main():
    logging.basicConfig(level=logging.INFO)
    print("✅ Бот запущен. Напишите /start в Telegram.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
