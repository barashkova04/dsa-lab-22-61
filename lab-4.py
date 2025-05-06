import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from dotenv import load_dotenv
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получение токена из переменных окружения
API_TOKEN = os.getenv('API_TOKEN')
if not API_TOKEN:
    logger.error("Не задан API_TOKEN в переменных окружения!")
    exit(1)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()  # Хранилище состояний в памяти
dp = Dispatcher(bot, storage=storage)

# Хранение курсов валют
currency_rates = {}

# Состояния для FSM (Finite State Machine)
class CurrencyStates(StatesGroup):
    waiting_for_currency_name = State()
    waiting_for_currency_rate = State()
    waiting_for_convert_currency = State()
    waiting_for_convert_amount = State()

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.reply(
        "Привет! Я бот для конвертации валют.\n"
        "Доступные команды:\n"
        "/save_currency - сохранить курс валюты\n"
        "/convert - конвертировать валюту в рубли\n"
        "/list_currencies - показать доступные валюты"
    )

# Обработчик команды /save_currency
@dp.message_handler(commands=['save_currency'], state=None)
async def cmd_save_currency(message: types.Message):
    await CurrencyStates.waiting_for_currency_name.set()
    await message.reply("Введите название валюты (например, USD, EUR):")

# Обработчик ввода названия валюты
@dp.message_handler(state=CurrencyStates.waiting_for_currency_name)
async def process_currency_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['currency_name'] = message.text.upper()
    
    await CurrencyStates.next()
    await message.reply(f"Введите курс {data['currency_name']} к рублю (например, 75.5):")

# Обработчик ввода курса валюты
@dp.message_handler(state=CurrencyStates.waiting_for_currency_rate)
async def process_currency_rate(message: types.Message, state: FSMContext):
    try:
        rate = float(message.text.replace(',', '.'))
        async with state.proxy() as data:
            currency_name = data['currency_name']
            currency_rates[currency_name] = rate
            await message.reply(
                f"Курс {currency_name} сохранен: 1 {currency_name} = {rate} RUB\n"
                f"Теперь можно использовать команду /convert"
            )
    except ValueError:
        await message.reply("Пожалуйста, введите число для курса валюты.")
        return
    
    await state.finish()

# Обработчик команды /convert
@dp.message_handler(commands=['convert'], state=None)
async def cmd_convert(message: types.Message):
    if not currency_rates:
        await message.reply("Сначала сохраните курсы валют с помощью /save_currency")
        return
    
    await CurrencyStates.waiting_for_convert_currency.set()
    await message.reply(
        "Введите название валюты для конвертации:\n"
        f"Доступные валюты: {', '.join(currency_rates.keys())}"
    )

# Обработчик выбора валюты для конвертации
@dp.message_handler(state=CurrencyStates.waiting_for_convert_currency)
async def process_convert_currency(message: types.Message, state: FSMContext):
    currency = message.text.upper()
    if currency not in currency_rates:
        await message.reply("Эта валюта не найдена. Попробуйте еще раз.")
        return
    
    async with state.proxy() as data:
        data['convert_currency'] = currency
    
    await CurrencyStates.next()
    await message.reply(f"Введите сумму в {currency} для конвертации в рубли:")

# Обработчик ввода суммы для конвертации
@dp.message_handler(state=CurrencyStates.waiting_for_convert_amount)
async def process_convert_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text.replace(',', '.'))
        async with state.proxy() as data:
            currency = data['convert_currency']
            rate = currency_rates[currency]
            result = amount * rate
            await message.reply(
                f"Результат конвертации:\n"
                f"{amount} {currency} = {result:.2f} RUB\n"
                f"По курсу: 1 {currency} = {rate} RUB"
            )
    except ValueError:
        await message.reply("Пожалуйста, введите число для суммы.")
        return
    
    await state.finish()

# Обработчик команды /list_currencies
@dp.message_handler(commands=['list_currencies'])
async def cmd_list_currencies(message: types.Message):
    if not currency_rates:
        await message.reply("Нет сохраненных валют. Используйте /save_currency")
        return
    
    response = "Сохраненные курсы валют:\n"
    for currency, rate in currency_rates.items():
        response += f"- 1 {currency} = {rate} RUB\n"
    
    await message.reply(response)

# Запуск бота
if __name__ == '__main__':
    logger.info("Бот запущен")
    executor.start_polling(dp, skip_updates=True)