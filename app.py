import logging  # Импортируем модуль для логирования событий
import ssl  # Импортируем модуль для работы с SSL (шифрование)
from aiohttp import web  # Импортируем модуль для создания веб-приложений на asyncio
import telebot  # Импортируем модуль для работы с Telegram Bot API
from database.db_utils import get_data_db  # Импортируем функцию для работы с базой данных
from handlers.message_handlers import setup_message_handlers  # Импортируем функцию для настройки обработчиков сообщений

# Порт для вебхука
WEBHOOK_PORT = 8443
WEBHOOK_LISTEN = '0.0.0.0'  # Прослушивание всех входящих подключений

# Пути к SSL сертификатам
WEBHOOK_SSL_CERT = "/etc/letsencrypt/live/pischasov.nikita.fvds.ru/fullchain.pem"
WEBHOOK_SSL_PRIV = "/etc/letsencrypt/live/pischasov.nikita.fvds.ru/privkey.pem"

try:
    # Получаем токен бота и URL вебхука из базы данных
    API_TOKEN, WEBHOOK_HOST = get_data_db(1)
    if not API_TOKEN:
        raise ValueError("Bot token is not defined")  # Вызываем исключение, если токен бота не определен

    if not WEBHOOK_HOST:
        raise ValueError("Webhook URL is not defined")  # Вызываем исключение, если URL вебхука не определен

    # URL для вебхука
    WEBHOOK_URL_BASE = f"https://{WEBHOOK_HOST}:{WEBHOOK_PORT}"
    WEBHOOK_URL_PATH = f"/{API_TOKEN}/"

    # Настройка логирования для библиотеки telebot
    logger = telebot.logger
    telebot.logger.setLevel(logging.INFO)

    # Создание экземпляра бота
    bot = telebot.TeleBot(API_TOKEN)

    # Создание aiohttp приложения
    app = web.Application()

    # Обработчик запросов от Telegram
    async def handle(request):
        if request.match_info.get('token') == bot.token:
            request_body_dict = await request.json()
            print("Received request:", request_body_dict)  # Отладочная информация
            update = telebot.types.Update.de_json(request_body_dict)
            bot.process_new_updates([update])
            return web.Response()
        else:
            return web.Response(status=403)

    # Добавление маршрута для обработки запросов вебхука
    app.router.add_post('/{token}/', handle)

    # Вызов функции для настройки обработчиков сообщений
    setup_message_handlers(bot)

    # Удаление предыдущего вебхука (если был установлен)
    bot.remove_webhook()

    # Установка нового вебхука
    try:
        response = bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH)
        if response:
            print("Webhook set successfully")
        else:
            print("Webhook set failed")
    except Exception as e:
        print(f"Error setting webhook: {e}")

    # Создание SSL контекста
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV)

    # Запуск aiohttp сервера
    web.run_app(
        app,
        host=WEBHOOK_LISTEN,
        port=WEBHOOK_PORT,
        ssl_context=context,
    )

except Exception as e:
    print(f"An error occurred: {e}")
