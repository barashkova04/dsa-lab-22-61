from aiogram import Bot, Dispatcher, F, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, BotCommand, BotCommandScopeDefault, BotCommandScopeChat
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import asyncio
import requests

# Настройка бота
bot = Bot(
    token='7516738774:AAEl3uMKJr334jJH3SxjAVfOewa1yTuFEfE',
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# Адреса микросервисов
CURRENCY_MANAGER_URL = 'http://localhost:5001'
DATA_MANAGER_URL = 'http://localhost:5002'

# --- Состояния FSM ---
class CurrencyForm(StatesGroup):
    name = State()
    rate = State()
    delete = State()
    update_name = State()
    update_rate = State()

class ConvertForm(StatesGroup):
    currency = State()
    amount = State()

# --- Проверка администратора ---
def is_admin(chat_id: str) -> bool:
    return chat_id == "1628249976"

# --- /start ---
@dp.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Привет! Я бот для конвертации валют.\n"
        "Команды:\n"
        "/get_currencies – список валют\n"
        "/convert – перевести в рубли\n"
        "/manage_currency – управление (для админов)"
    )

# --- /me ---
@dp.message(Command("me"))
async def cmd_me(message: Message) -> None:
    await message.answer(f"Твой chat_id: {message.chat.id}")

# --- /get_currencies ---
@dp.message(Command("get_currencies"))
async def cmd_get_currencies(message: Message) -> None:
    try:
        response = requests.get(f"{DATA_MANAGER_URL}/currencies")
        currencies = response.json()
        if not currencies:
            await message.answer("Список валют пуст.")
            return
        text = "Валюты:\n" + "\n".join([f"• {c['currency_name']} = {c['rate']} RUB" for c in currencies])
        await message.answer(text)
    except Exception:
        await message.answer("Ошибка при получении данных.")

# --- /convert ---
@dp.message(Command("convert"))
async def cmd_convert(message: Message, state: FSMContext) -> None:
    await message.answer("Введите название валюты:")
    await state.set_state(ConvertForm.currency)

@dp.message(ConvertForm.currency)
async def process_currency(message: Message, state: FSMContext) -> None:
    currency = message.text.strip().upper()
    try:
        response = requests.get(f"{DATA_MANAGER_URL}/currencies")
        currencies = response.json()
        match = next((c for c in currencies if c['currency_name'] == currency), None)
        if not match:
            await message.answer("Валюта не найдена.")
            await state.clear()
            return
        await state.update_data(currency_name=currency, rate=match['rate'])
        await message.answer(f"Введите сумму в {currency}:")
        await state.set_state(ConvertForm.amount)
    except Exception:
        await message.answer("Ошибка при обращении к серверу.")
        await state.clear()

@dp.message(ConvertForm.amount)
async def process_amount(message: Message, state: FSMContext) -> None:
    try:
        amount = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("Введите корректное число.")
        return

    data = await state.get_data()
    result = amount * float(data["rate"])
    await message.answer(
        f"{amount} {data['currency_name']} = {result:.2f} RUB "
        f"(курс: {data['rate']} RUB)"
    )
    await state.clear()

# --- /manage_currency ---
@dp.message(Command("manage_currency"))
async def cmd_manage_currency(message: Message) -> None:
    if not is_admin(str(message.chat.id)):
        await message.answer("⛔ Доступ только для админов.")
        return

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Добавить валюту"), KeyboardButton(text="Удалить валюту")],
            [KeyboardButton(text="Изменить курс валюты")]
        ],
        resize_keyboard=True
    )
    await message.answer("Выберите действие:", reply_markup=keyboard)

# --- Добавить валюту ---
@dp.message(F.text == "Добавить валюту")
async def add_currency(message: Message, state: FSMContext) -> None:
    await message.answer("Введите название валюты:")
    await state.set_state(CurrencyForm.name)

@dp.message(CurrencyForm.name)
async def enter_currency_name(message: Message, state: FSMContext) -> None:
    currency = message.text.strip().upper()
    response = requests.get(f"{DATA_MANAGER_URL}/currencies")
    if any(c['currency_name'] == currency for c in response.json()):
        await message.answer("Данная валюта уже существует.")
        await state.clear()
        return
    await state.update_data(currency_name=currency)
    await message.answer("Введите курс к рублю:")
    await state.set_state(CurrencyForm.rate)

@dp.message(CurrencyForm.rate)
async def save_currency(message: Message, state: FSMContext) -> None:
    try:
        rate = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("Введите корректное число.")
        return

    data = await state.get_data()
    response = requests.post(f"{CURRENCY_MANAGER_URL}/load", json={
        "currency_name": data['currency_name'],
        "rate": rate
    })
    if response.status_code == 200:
        await message.answer(f"Валюта {data['currency_name']} добавлена.")
    else:
        await message.answer("Ошибка при добавлении.")
    await state.clear()

# --- Удалить валюту ---
@dp.message(F.text == "Удалить валюту")
async def delete_currency(message: Message, state: FSMContext) -> None:
    await message.answer("Введите название валюты:")
    await state.set_state(CurrencyForm.delete)

@dp.message(CurrencyForm.delete)
async def confirm_delete_currency(message: Message, state: FSMContext) -> None:
    name = message.text.strip().upper()
    response = requests.post(f"{CURRENCY_MANAGER_URL}/delete", json={"currency_name": name})
    if response.status_code == 200:
        await message.answer(f"Валюта {name} удалена.")
    else:
        await message.answer("Ошибка при удалении.")
    await state.clear()

# --- Изменить курс ---
@dp.message(F.text == "Изменить курс валюты")
async def update_currency(message: Message, state: FSMContext) -> None:
    await message.answer("Введите название валюты:")
    await state.set_state(CurrencyForm.update_name)

@dp.message(CurrencyForm.update_name)
async def get_update_name(message: Message, state: FSMContext) -> None:
    await state.update_data(currency_name=message.text.strip().upper())
    await message.answer("Введите новый курс:")
    await state.set_state(CurrencyForm.update_rate)

@dp.message(CurrencyForm.update_rate)
async def save_new_rate(message: Message, state: FSMContext) -> None:
    try:
        rate = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("Введите корректное число.")
        return

    data = await state.get_data()
    response = requests.post(f"{CURRENCY_MANAGER_URL}/update_currency", json={
        "currency_name": data['currency_name'],
        "rate": rate
    })
    if response.status_code == 200:
        await message.answer(f"Курс валюты {data['currency_name']} обновлён.")
    else:
        await message.answer("Ошибка при обновлении.")
    await state.clear()

# --- Команды по ролям ---
async def set_commands():
    admin_id = 1628249976
    await bot.set_my_commands([
        BotCommand(command="start", description="Начать"),
        BotCommand(command="get_currencies", description="Список валют"),
        BotCommand(command="convert", description="Конвертация"),
        BotCommand(command="manage_currency", description="Управление валютами"),
        BotCommand(command="me", description="Узнать chat_id")
    ], scope=BotCommandScopeChat(chat_id=admin_id))

    await bot.set_my_commands([
        BotCommand(command="start", description="Начать"),
        BotCommand(command="get_currencies", description="Список валют"),
        BotCommand(command="convert", description="Конвертация"),
        BotCommand(command="me", description="Узнать chat_id")
    ], scope=BotCommandScopeChat(chat_id=admin_id))

# --- Точка входа ---
async def main():
    await set_commands()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
