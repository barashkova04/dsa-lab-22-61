import logging
import psycopg2
from decimal import Decimal
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters, CallbackQueryHandler
)
import requests
from datetime import datetime
import traceback

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
REG_NAME, ADD_TYPE, ADD_SUM, ADD_DATE = range(4)
OPERATIONS_CURRENCY = range(1)

# Подключение к базе данных
def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname="telegram_bot",
            user="postgres",
            password="12345678",
            host="localhost",
            port="5432"
        )
        logger.info("Успешное подключение к базе данных")
        return conn
    except psycopg2.Error as e:
        logger.error(f"Ошибка подключения к базе данных: {e}")
        raise

# Проверка существования таблиц
def ensure_tables_exist():
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                chat_id BIGINT UNIQUE NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS operations (
                id SERIAL PRIMARY KEY,
                date DATE NOT NULL,
                sum DECIMAL(10, 2) NOT NULL,
                chat_id BIGINT NOT NULL,
                type_operation VARCHAR(50) NOT NULL CHECK (type_operation IN ('ДОХОД', 'РАСХОД')),
                FOREIGN KEY (chat_id) REFERENCES users(chat_id)
            )
        """)
        conn.commit()
        logger.info("Таблицы users и operations проверены/созданы")
    except psycopg2.Error as e:
        logger.error(f"Ошибка при создании таблиц: {e}\n{traceback.format_exc()}")
        raise
    finally:
        cur.close()
        conn.close()

# Функция для получения курса валют
def get_exchange_rate(base_currency, target_currency):
    api_key = "da978ba70bfa7737a09297a0"  # Замените на ваш ключ exchangerate-api.com
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{base_currency}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data.get('result') == 'success':
            rate = data['conversion_rates'].get(target_currency)
            if rate:
                logger.info(f"Курс {base_currency} -> {target_currency}: {rate}")
                return rate
            else:
                logger.error(f"Валюта {target_currency} не найдена в ответе API")
                return None
        else:
            logger.error(f"Ошибка API: {data.get('error-type')}")
            return None
    except requests.RequestException as e:
        logger.error(f"Ошибка при запросе курса валют: {e}")
        return None

# Проверка регистрации пользователя
def is_user_registered(chat_id):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM users WHERE chat_id = %s", (chat_id,))
        exists = cur.fetchone() is not None
        logger.info(f"Проверка регистрации для chat_id {chat_id}: {'Зарегистрирован' if exists else 'Не зарегистрирован'}")
        return exists
    except psycopg2.Error as e:
        logger.error(f"Ошибка при проверке регистрации: {e}\n{traceback.format_exc()}")
        raise
    finally:
        cur.close()
        conn.close()

# Обработчик команды /menu
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    logger.info(f"Получена команда /menu от chat_id {chat_id}")
    try:
        await update.message.reply_text(
            "Доступные команды:\n"
            "/start — Начать взаимодействие с ботом\n"
            "/reg — Зарегистрироваться\n"
            "/add_operation — Добавить новую операцию\n"
            "/operations — Просмотреть все операции"
        )
    except Exception as e:
        logger.error(f"Ошибка в /menu: {e}\n{traceback.format_exc()}")
        await update.message.reply_text("Произошла ошибка при отображении списка команд. Попробуйте снова.")

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    logger.info(f"Получена команда /start от chat_id {chat_id}")
    try:
        ensure_tables_exist()
        if is_user_registered(chat_id):
            await update.message.reply_text(
                "Добро пожаловать обратно! Вы уже зарегистрированы.\n"
                "Используйте /menu для просмотра команд."
            )
        else:
            await update.message.reply_text(
                "Добро пожаловать! Вы не зарегистрированы.\n"
                "Используйте /menu для регистрации или других команд."
            )
    except Exception as e:
        logger.error(f"Ошибка в /start: {e}\n{traceback.format_exc()}")
        await update.message.reply_text("Произошла ошибка. Попробуйте снова.")

# 2.1.2 Регистрация
async def start_registration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    logger.info(f"Шаг 1: Получена команда /reg от chat_id {chat_id}")
    try:
        # Завершаем любой активный диалог
        if context.user_data.get('conversation_active'):
            logger.info(f"Завершение активного диалога для chat_id {chat_id}")
            context.user_data.clear()
        
        # Шаг 2: Проверка, что пользователь не зарегистрирован
        ensure_tables_exist()
        if is_user_registered(chat_id):
            logger.info(f"Пользователь chat_id {chat_id} уже зарегистрирован")
            await update.message.reply_text("Вы уже зарегистрированы! Используйте /menu для просмотра команд.")
            return ConversationHandler.END
        
        # Шаг 3: Запрос логина
        logger.info(f"Шаг 3: Запрошено введение логина для chat_id {chat_id}")
        await update.message.reply_text("Введите ваш логин (только буквы, цифры, до 50 символов):")
        context.user_data['conversation_active'] = True
        return REG_NAME
    except psycopg2.Error as e:
        logger.error(f"Ошибка базы данных в start_registration: {e}\n{traceback.format_exc()}")
        await update.message.reply_text("Ошибка базы данных. Попробуйте позже.")
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Непредвиденная ошибка в start_registration: {e}\n{traceback.format_exc()}")
        await update.message.reply_text("Произошла ошибка при обработке команды /reg. Попробуйте снова.")
        return ConversationHandler.END

async def save_registration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    name = update.message.text.strip()
    logger.info(f"Шаг 4: Получен логин '{name}' от chat_id {chat_id}")
    
    # Проверка логина
    if not name:
        logger.warning(f"Пустой логин для chat_id {chat_id}")
        await update.message.reply_text("Логин не может быть пустым. Введите логин снова:")
        return REG_NAME
    if len(name) > 50:
        logger.warning(f"Слишком длинный логин для chat_id {chat_id}: {len(name)} символов")
        await update.message.reply_text("Логин слишком длинный (макс. 50 символов). Введите логин снова:")
        return REG_NAME
    if not name.isalnum():
        logger.warning(f"Недопустимые символы в логине для chat_id {chat_id}: {name}")
        await update.message.reply_text("Логин должен содержать только буквы и цифры. Введите логин снова:")
        return REG_NAME
    
    try:
        conn = get_db_connection()
        try:
            cur = conn.cursor()
            # Шаг 4: Сохранение логина и chat_id
            cur.execute("INSERT INTO users (name, chat_id) VALUES (%s, %s)", (name, chat_id))
            conn.commit()
            logger.info(f"Регистрация успешна: chat_id {chat_id}, логин {name}")
            await update.message.reply_text(f"Регистрация успешна! Ваш логин: {name}\nИспользуйте /menu для просмотра команд.")
        except psycopg2.errors.UniqueViolation:
            logger.error(f"Ошибка: chat_id {chat_id} уже существует в базе данных")
            await update.message.reply_text("Этот chat_id уже зарегистрирован. Попробуйте другой аккаунт.")
            return ConversationHandler.END
        except psycopg2.Error as e:
            logger.error(f"Ошибка базы данных при регистрации: {e}\n{traceback.format_exc()}")
            await update.message.reply_text("Ошибка базы данных при регистрации. Попробуйте снова.")
            return ConversationHandler.END
        finally:
            cur.close()
    except Exception as e:
        logger.error(f"Непредвиденная ошибка при регистрации: {e}\n{traceback.format_exc()}")
        await update.message.reply_text("Произошла ошибка при регистрации. Попробуйте снова.")
        return ConversationHandler.END
    finally:
        conn.close()
        context.user_data.clear()  # Очистка состояния диалога
    return ConversationHandler.END

# 2.1.3 Добавление операции
async def start_add_operation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    logger.info(f"Получена команда /add_operation от chat_id {chat_id}")
    try:
        if context.user_data.get('conversation_active'):
            logger.info(f"Завершение активного диалога для chat_id {chat_id}")
            context.user_data.clear()
        
        ensure_tables_exist()
        if not is_user_registered(chat_id):
            await update.message.reply_text("Пожалуйста, зарегистрируйтесь с помощью команды /reg (см. /menu).")
            return ConversationHandler.END
        keyboard = [
            [InlineKeyboardButton("ДОХОД", callback_data="ДОХОД")],
            [InlineKeyboardButton("РАСХОД", callback_data="РАСХОД")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Выберите тип операции:", reply_markup=reply_markup)
        context.user_data['conversation_active'] = True
        return ADD_TYPE
    except Exception as e:
        logger.error(f"Ошибка в start_add_operation: {e}\n{traceback.format_exc()}")
        await update.message.reply_text("Ошибка при обработке команды /add_operation. Попробуйте снова.")
        return ConversationHandler.END

async def select_operation_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data['type_operation'] = query.data
    logger.info(f"Выбран тип операции: {query.data} для chat_id {query.message.chat_id}")
    await query.message.reply_text("Введите сумму операции в рублях:")
    return ADD_SUM

async def save_operation_sum(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        context.user_data['sum'] = float(update.message.text.strip())
        logger.info(f"Введена сумма: {context.user_data['sum']} для chat_id {update.effective_chat.id}")
        await update.message.reply_text("Введите дату операции (ГГГГ-ММ-ДД):")
        return ADD_DATE
    except ValueError:
        logger.warning(f"Некорректная сумма введена для chat_id {update.effective_chat.id}")
        await update.message.reply_text("Пожалуйста, введите корректную сумму в рублях.")
        return ADD_SUM

async def save_operation_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    try:
        date = datetime.strptime(update.message.text.strip(), '%Y-%m-%d').date()
        type_operation = context.user_data['type_operation']
        sum_operation = context.user_data['sum']
        logger.info(f"Сохранение операции: chat_id {chat_id}, дата {date}, сумма {sum_operation}, тип {type_operation}")
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO operations (date, sum, chat_id, type_operation) VALUES (%s, %s, %s, %s)",
            (date, sum_operation, chat_id, type_operation)
        )
        conn.commit()
        await update.message.reply_text("Операция успешно добавлена!\nИспользуйте /menu для просмотра команд.")
    except (ValueError, psycopg2.Error) as e:
        logger.error(f"Ошибка при добавлении операции: {e}\n{traceback.format_exc()}")
        await update.message.reply_text("Ошибка при добавлении операции. Проверьте формат даты (ГГГГ-ММ-ДД).")
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Непредвиденная ошибка при добавлении операции: {e}\n{traceback.format_exc()}")
        await update.message.reply_text("Произошла ошибка. Попробуйте снова.")
        return ConversationHandler.END
    finally:
        cur.close()
        conn.close()
        context.user_data.clear()  # Очистка состояния диалога
    return ConversationHandler.END

# 2.1.4 и 2.2 Просмотр операций (с учетом варианта 4)
async def start_operations(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    logger.info(f"Получена команда /operations от chat_id {chat_id}")
    try:
        if context.user_data.get('conversation_active'):
            logger.info(f"Завершение активного диалога для chat_id {chat_id}")
            context.user_data.clear()
        
        ensure_tables_exist()
        if not is_user_registered(chat_id):
            await update.message.reply_text("Пожалуйста, зарегистрируйтесь с помощью команды /reg (см. /menu).")
            return ConversationHandler.END
        keyboard = [
            [InlineKeyboardButton("RUB", callback_data="RUB")],
            [InlineKeyboardButton("EUR", callback_data="EUR")],
            [InlineKeyboardButton("USD", callback_data="USD")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Выберите валюту для просмотра операций:", reply_markup=reply_markup)
        context.user_data['conversation_active'] = True
        return OPERATIONS_CURRENCY
    except Exception as e:
        logger.error(f"Ошибка в start_operations: {e}\n{traceback.format_exc()}")
        await update.message.reply_text("Ошибка при обработке команды /operations. Попробуйте снова.")
        return ConversationHandler.END

async def show_operations(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    currency = query.data
    chat_id = query.message.chat_id
    logger.info(f"Выбрана валюта {currency} для chat_id {chat_id}")
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT date, sum, type_operation FROM operations WHERE chat_id = %s", (chat_id,))
        operations = cur.fetchall()
        
        if not operations:
            await query.message.reply_text("У вас нет операций.\nИспользуйте /menu для просмотра команд.")
            return ConversationHandler.END
        
        # Получение курса валют
        exchange_rate = 1.0 if currency == "RUB" else get_exchange_rate("RUB", currency)
        if exchange_rate is None:
            await query.message.reply_text("Ошибка получения курса валют. Попробуйте позже.")
            return ConversationHandler.END
        
        # Преобразование exchange_rate в Decimal
        exchange_rate_decimal = Decimal('1.0') if currency == "RUB" else Decimal(str(exchange_rate))
        logger.info(f"exchange_rate_decimal: {exchange_rate_decimal}, type: {type(exchange_rate_decimal)}")
        
        # Расчет доходов и расходов
        total_income = Decimal('0.0')
        total_expense = Decimal('0.0')
        operation_details = []
        
        for op in operations:
            date, sum_op, type_op = op
            logger.info(f"sum_op: {sum_op}, type: {type(sum_op)}, exchange_rate_decimal: {exchange_rate_decimal}")
            converted_sum = sum_op * exchange_rate_decimal
            operation_details.append(f"{date}: {type_op} {converted_sum:.2f} {currency}")
            if type_op == "ДОХОД":
                total_income += converted_sum
            else:
                total_expense += converted_sum
        
        response = "Ваши операции:\n" + "\n".join(operation_details)
        response += f"\n\nОбщий доход: {total_income:.2f} {currency}"
        response += f"\nОбщий расход: {total_expense:.2f} {currency}"
        response += f"\n\nИспользуйте /menu для просмотра команд."
        
        await query.message.reply_text(response)
    except psycopg2.Error as e:
        logger.error(f"Ошибка при получении операций: {e}\n{traceback.format_exc()}")
        await query.message.reply_text("Ошибка при получении операций. Попробуйте позже.")
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Непредвиденная ошибка при получении операций: {e}\n{traceback.format_exc()}")
        await query.message.reply_text("Произошла ошибка. Попробуйте снова.")
        return ConversationHandler.END
    finally:
        cur.close()
        conn.close()
        context.user_data.clear()  # Очистка состояния диалога
    return ConversationHandler.END

def main():
    application = Application.builder().token("7660552153:AAFtxgcA0BjfHAqIkbjk0TEXxyo1H6syi0I").build()

    # Обработчик команды /menu
    application.add_handler(CommandHandler('menu', menu))
    logger.info("Добавлен обработчик для /menu")

    # Обработчик команды /start
    application.add_handler(CommandHandler('start', start))
    logger.info("Добавлен обработчик для /start")

    # Регистрация
    reg_handler = ConversationHandler(
        entry_points=[CommandHandler('reg', start_registration)],
        states={
            REG_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_registration)]
        },
        fallbacks=[]
    )
    application.add_handler(reg_handler)
    logger.info("Добавлен обработчик для /reg (ConversationHandler)")

    # Добавление операции
    add_op_handler = ConversationHandler(
        entry_points=[CommandHandler('add_operation', start_add_operation)],
        states={
            ADD_TYPE: [CallbackQueryHandler(select_operation_type)],
            ADD_SUM: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_operation_sum)],
            ADD_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_operation_date)]
        },
        fallbacks=[]
    )
    application.add_handler(add_op_handler)
    logger.info("Добавлен обработчик для /add_operation (ConversationHandler)")

    # Просмотр операций
    operations_handler = ConversationHandler(
        entry_points=[CommandHandler('operations', start_operations)],
        states={
            OPERATIONS_CURRENCY: [CallbackQueryHandler(show_operations)]
        },
        fallbacks=[]
    )
    application.add_handler(operations_handler)
    logger.info("Добавлен обработчик для /operations (ConversationHandler)")

    logger.info("Запуск бота")
    application.run_polling()

if __name__ == '__main__':
    main()