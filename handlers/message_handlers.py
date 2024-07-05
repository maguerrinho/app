from telebot import types

from auxiliary_handlers import format_phone
from database.db_utils import get_data_db, update_user_db, read_template
from integration.bonussystem import get_user_sul
from log.logging import log
import datetime
from datetime import datetime

time_cash_user = {}


def replykeyboardmenu(type_menu):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if type_menu == 1:  # Кнопка авторизации
        button = types.KeyboardButton('Поделиться номером телефона', request_contact=True)
        markup.add(button)
    if type_menu == 2:  # Кнопки выбора бренда
        button_gv = types.KeyboardButton('GoodVape')
        button_bv = types.KeyboardButton('BroadVape')
        markup.add(button_bv, button_gv)
    if type_menu == 3:  # Кнопки основного меню
        button_site = types.KeyboardButton('Сайт')
        button_social = types.KeyboardButton('Социальные сети')
        button_loaylsystem = types.KeyboardButton('Система лояльности')
        button_ask = types.KeyboardButton('Задать вопрос')
        button_addresses = types.KeyboardButton('Адреса магазинов')
        button_brand = types.KeyboardButton('Выбрать другой бренд')
        markup.add(button_site, button_social, button_loaylsystem, button_ask, button_addresses, button_brand)


def inlinekeyboardmenu(type_menu):
    markup = types.InlineKeyboardMarkup()
    if type_menu == 1:
        button_register = types.InlineKeyboardButton(text='Зарегестрироваться', callback_data='register')
        button_noregister = types.InlineKeyboardButton(text='Отказаться', callback_data='noregister')
        markup.add(button_register, button_noregister)


def calculate_age(birthdate):
    today = datetime.datetime.now()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return age


def setup_message_handlers(bot):
    # Настраивает обработчики сообщений для бота.
    # Аргументы:
    # - bot: экземпляр TeleBot
    @bot.message_handler(commands=['start'])
    def handle_start(message):
        user_id = message.from_user.id
        user_data = get_data_db(data_type=4, user_id=user_id)
        if user_data and user_data[4] == 1:
            try:
                bot.reply_to(message, read_template('100').format(name=user_data[1]), reply_markup=replykeyboardmenu(2))
            except Exception as e:
                log(f"Ошибка при форматировании текста шаблона: {e}")
        else:
            try:
                bot.reply_to(message, read_template('101'), reply_markup=replykeyboardmenu(1))
            except Exception as e:
                log(f"Ошибка при форматировании текста шаблона: {e}")

    @bot.message_handler(content_types=['contact'])
    def handle_contact(message):
        user_id = message.from_user.id
        frist_name = message.from_user.frist_name
        last_name = message.from_user.last_name
        full_name = frist_name + " " + last_name
        phone = format_phone(message.contact.phone_number)
        user_data = get_data_db(data_type=4, user_id=user_id)
        send_message = bot.reply_to(message, 'Происходит процесс авторизации. Пожалуйста, подождите...')
        if user_data:
            try:
                update_user_db(user_id, phone=None, name=None, birth_date=None, active=1, id_card=None)
            except Exception as e:
                log(f"Ошибка при обновлении данных пользователя: {e}")
            bot.edit_message_text('Авторизация произошла успешно!', chat_id=send_message.chat.id,
                                  message_id=send_message.message_id)
            try:
                bot.reply_to(message, read_template('102'), reply_markup=replykeyboardmenu(2))
            except Exception as e:
                log(f"Ошибка при форматировании текста шаблона: {e}")
        else:
            time_cash_user[user_id] = {
                'frist_name': frist_name,
                'last_name': last_name,
                'full_name': full_name,
                'phone': phone

            }
            bot.reply_to(message, read_template('103'), reply_markup=inlinekeyboardmenu(1))

    @bot.callback_query_handler(func=lambda call: True)
    def callback_handler(call):
        user_id = call.from_user.id
        if call.data == 'noregister':
            if user_id in time_cash_user:
                del time_cash_user[user_id]
            bot.answer_callback_query(call.id, read_template('101'))
            bot.send_message(call.message.chat.id, 'Меню',
                             reply_markup=replykeyboardmenu(1))  # Редактируем для отправки клавиатуры
        elif call.data == 'register':
            bot.answer_callback_query(call.id, read_template('104'))
            user_sul = get_user_sul(time_cash_user[user_id]['phone'])
            if user_sul.get('code') == 0:
                users = user_sul.get('users', [])
                for user in users:
                    user_sul_id = user.get('id')
                    cards = user.get('cards', [])
                    for card in cards:
                        card_id = card.get('id')
            elif user_sul.get('code') == 114:
                pass
            else:
                pass

    def request_birth_year(message):
        bot.reply_to(message, "Введите ваш год рождения (например, 1990):")
        bot.register_next_step_handler(message, process_birth_year)

    def process_birth_year(message):
        user_id = message.from_user.id
        try:
            year = int(message.text)
            current_year = datetime.datetime.now().year
            if year < 1900 or year > current_year:
                bot.reply_to(message, "Некорректный год. Пожалуйста, введите год рождения заново (например, 1990):")
                bot.register_next_step_handler(message, process_birth_year)
            else:
                if user_id not in time_cash_user:
                    time_cash_user[user_id]['year'] = year
                    bot.reply_to(message, "Введите ваш месяц рождения (1-12):")
                    bot.register_next_step_handler(message, process_birth_month)
        except ValueError:
            bot.reply_to(message, "Некорректный формат. Пожалуйста, введите год рождения заново (например, 1990):")
            bot.register_next_step_handler(message, process_birth_year)

    def process_birth_month(message):
        user_id = message.from_user.id
        try:
            month = int(message.text)
            if month < 1 or month > 12:
                bot.reply_to(message, "Некорректный месяц. Пожалуйста, введите месяц рождения заново (1-12):")
                bot.register_next_step_handler(message, process_birth_month)
            else:
                time_cash_user[user_id]['month'] = month
                bot.reply_to(message, "Введите ваш день рождения (1-31):")
                bot.register_next_step_handler(message, process_birth_day)
        except ValueError:
            bot.reply_to(message, "Некорректный формат. Пожалуйста, введите месяц рождения заново (1-12):")
            bot.register_next_step_handler(message, process_birth_month)

    def process_birth_day(message):
        user_id = message.from_user.id
        try:
            day = int(message.text)
            if day < 1 or day > 31:
                bot.reply_to(message, "Некорректный день. Пожалуйста, введите день рождения заново (1-31):")
                bot.register_next_step_handler(message, process_birth_day)
            else:
                year = time_cash_user[user_id]['year']
                month = time_cash_user[user_id]['month']
                birthdate = datetime(year, month, day)
                age = calculate_age(birthdate)
                if age < 18:
                    bot.reply_to(message, "Вам должно быть не менее 18 лет.")
                    return
                time_cash_user[user_id]['day'] = day
                time_cash_user[user_id]['birthdate'] = birthdate.strftime('%d.%m.%Y')
                bot.reply_to(message, f"Дата рождения сохранена: {time_cash_user[user_id]['birthdate']}")
                # Далее можно продолжать выполнение других функций
        except ValueError:
            bot.reply_to(message, "Некорректный формат. Пожалуйста, введите день рождения заново (1-31):")
            bot.register_next_step_handler(message, process_birth_day)
        except Exception as e:
            print(f"Произошла ошибка: {e}")  # Логируем ошибку
            bot.reply_to(message, "Произошла ошибка при обработке даты рождения. Пожалуйста, введите данные заново.")
            bot.register_next_step_handler(message, process_birth_year)

    def process_last_name(message):
        user_id = message.from_user.id
        last_name = message.text
        time_cash_user[user_id] = {
            'name': last_name
        }

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='Мужской', callback_data='male'),
                     types.InlineKeyboardButton(text='Женский', callback_data='female'))
        bot.reply_to(message, "Выберите ваш пол:", reply_markup=keyboard)
