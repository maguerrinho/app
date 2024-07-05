from flask import Flask, request
from telebot import TeleBot, types

from database.db_utils import get_data_db  # Импорт функции для работы с базой данных
from handlers.message_handlers import setup_message_handlers  # Импорт функции для настройки обработчиков сообщений
from log.logging import log  # Импорт функции для логирования ошибок

app = Flask(__name__)  # Создаем экземпляр Flask приложения

try:
    TOKEN, URL = get_data_db(1)  # Получение токена бота и URL вебхука из базы данных

    if not TOKEN:
        log("Bot token is not defined")  # Логируем ошибку, если токен бота не определен
        raise ValueError("Bot token is not defined")  # Вызываем исключение, если токен бота не определен

    if not URL:
        log("Webhook URL is not defined")  # Логируем ошибку, если URL вебхука не определен
        raise ValueError("Webhook URL is not defined")  # Вызываем исключение, если URL вебхука не определен

    bot = TeleBot(TOKEN)  # Создаем экземпляр Telegram бота с использованием полученного токена
    setup_message_handlers(bot)  # Вызов функции для настройки обработчиков сообщений


    @app.route('/webhook', methods=['POST'])
    def webhook():
        """
        Обрабатывает входящие POST запросы на /webhook.
        
        Входные данные:
        - request: объект запроса Flask
        
        Возвращает:
        - str: ответное сообщение или описание ошибки, если она возникла
        - int: HTTP статус код ответа (200 или 400)
        """
        try:
            json_str = request.get_data().decode('UTF-8')  # Получаем данные POST запроса
            update = types.Update.de_json(json_str)  # Преобразуем данные в объект Update
            bot.process_new_updates([update])  # Обрабатываем новые обновления от Telegram
            return '!', 200  # Возвращаем успешный HTTP код

        except Exception as e:
            error_message = f"Error processing webhook: {e}"  # Формируем сообщение об ошибке
            log(error_message)  # Логируем ошибку
            return error_message, 400  # Возвращаем HTTP код ошибки


    if __name__ == '__main__':
        try:
            bot.remove_webhook()  # Удаляем предыдущий вебхук (если есть)
            bot.set_webhook(url=URL)  # Устанавливаем новый вебхук с использованием URL
            app.run(host='127.0.0.1', port=8443)  # Запускаем Flask приложение

        except Exception as e:
            log(f"An error occurred: {e}")  # Логируем ошибку запуска приложения

except ValueError as ve:
    log(f"ValueError: {ve}")  # Логируем исключение ValueError

except Exception as e:
    log(f"An unexpected error occurred: {e}")  # Логируем неожиданное исключение
