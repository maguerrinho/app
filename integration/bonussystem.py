from datetime import datetime
from database.db_utils import get_data_db
from log.logging import log

import hashlib
import json
import requests


def get_token_sul():
    try:
        db_res = get_data_db(2)
        print(f"Полученные данные из БД: {db_res}")
        if not db_res:
            log("Ошибка при вызове функции get_token_sul(2): Не удалось получить данные из базы данных.")
            return None

        # Проверяем, что db_res содержит ровно 4 значения
        if len(db_res) != 4:
            log("Ошибка данных: Ожидалось 4 значения.")
            return None

        # Распаковываем значения
        db_login, db_password, db_url, db_shop_id = db_res
        print(f"Данные для авторизации: login={db_login}, password={db_password}, url={db_url}, shop_id={db_shop_id}")

        password_sha1 = hashlib.sha1(db_password.encode('utf-8')).hexdigest()

        data_sul = {
            "login": db_login,
            "password": password_sha1,
            "role": "organization"
        }
        headers = {
            "Content-Type": "application/json"
        }
        url = f"{db_url.rstrip('/')}/sign_in"
        response = requests.post(url, headers=headers, data=json.dumps(data_sul))

        if response.status_code != 200:
            log(f"Ошибка HTTP: {response.status_code}")
            return None

        result = response.json()

        if result.get('code') != 0:
            response_text = (f"Ошибка в получении TOKEN в 1С-Рарус: Код: {result.get('code')} "
                             f"Сообщение {result.get('message')}")
            log(response_text)
            return None
        else:
            return {
                "token": result.get('token'),
                "url": db_url,
                "shop_id": db_shop_id 
            }

    except Exception as e:
        log(f"Произошла ошибка при выполнении запроса: {e}")
        return None


def get_user_sul(phone):
    try:
        result = get_token_sul()
        token = result.get('token')
        if not token:
            log('Не удалось получить TOKEN для взаимодействия с 1С-Рарус по API')
            return None
        url = f"{result.get('url')}/organization/user?phone={phone}&full_info=true"
        headers = {
            "Content-Type": "application/json",
            "token": token
        }

        response = requests.get(url, headers=headers)
        result = response.json()
        return result
    except Exception as e:
        log(f"Произошла ошибка при выполнении запроса: {e}")
        return None


def register_in_sul(login, name, phone, gender, birthdate, city_id):
    try:
        result = get_token_sul()
        token = result.get('token')
        if not token:
            log('Не удалось получить TOKEN для взаимодействия с 1С-Рарус по API')
            return None
        url = f"{result.get('url')}/organization/user/new"
        data = {
            "login": login,
            "name": name,
            "phone": phone,
            "gender": gender,
            "birthdate": birthdate,
            "activation_shop_id": result.get('shop_id'),
            "recieve_notifications": 0,
            "city_id": city_id,
            "app_client": "Telegram Bot",
            "confirmed": 1,
            "personal_data_agree": 1,
            "electronic_cheque": 0
        }
        headers = {
            "Content-Type": "application/json",
            "token": token
        }

        response = requests.post(url, headers=headers, data=json.dumps(data))
        result = response.json()  
        if result.get('code') != 0:
            response_text = (f"Ошибка в выполнении запроса к 1С-Рарус: Код: {result.get('code')} "
                            f"Сообщение {result.get('message')}")
            log(response_text)
            return None
        return result
    except Exception as e:
        log(f"Произошла ошибка при выполнении запроса: {e}")
        return None


# def get_card_sul(phone, view):
#     try:
#         result = get_token_sul()
#         token = result.get('token')
#         if not token:
#             log('Не удалось получить TOKEN для взаимодействия с 1С-Рарус по API')
#             return None

#         url = f"{result.get('url')}/organization/card?phone={phone}"
#         headers = {
#             "Content-Type": "application/json",
#             "token": token
#         }

#         response = requests.get(url, headers=headers)
#         result = response.json()

#         if result.get('code') != 0:
#             response_text = (f"Ошибка в выполнении запроса к 1С-Рарус: Код: {result.get('code')} "
#                             f"Сообщение {result.get('message')}")
#             log(response_text)
#             return None

#         card = result['cards'][0] if result['cards'] else None
#         if not card:
#             log('Не найдена карта пользователя в системе 1С-Рарус')
#             return None
#         if view == 1:
#             block_status = card.get('blocked_status')
#             if block_status == 0:
#                 active = 'Активна'
#             elif block_status == 1:
#                 active = 'Заблокирована'
#             elif block_status == 2:
#                 active = 'Временно заблокирована'
#             elif block_status == 3:
#                 active = 'Заблокирована для списания'
#             elif block_status == 4:
#                 active = 'Заблокирована, доступно начисление'
#             else:
#                 active = 'Неизвестный статус'

#             response_text = langmess['SUL']['Balancecard'].format(
#                 barcode=card.get('barcode'),
#                 active=active,
#                 balance=format_bonus(card.get('balance')),
#                 actual_balance=format_bonus(card.get('actual_balance')),
#                 name=card.get('name')
#             )
#             return response_text
#         elif view == 2:
#             return card.get('id')
#         else:
#             log('Функция get_balance_sul Некорректный тип запроса')
#             return None


# def format_sales_history_text(sales):
#     response_text = langmess['SUL']['HistorySale']
#     for sale in sales[:3]:
#         sale_text = langmess['SUL']['HistorySale1'].format(
#             date=convert_unix_to_readable_date(sale.get('date')),
#             sum=sale.get('summ'),
#             item='\n- '.join([item['item_name'] for item in sale.get('cheque_items_for_sales', [])]),
#             bonsum=format_bonus(sale.get('bonus_earned')),
#             minbonsum=format_bonus(sale.get('bonus_spent'))
#         )
#         response_text += sale_text + "\n\n"
#     print(response_text)
#     return response_text


# def format_sales_history_data(sales):
#     data_sales = []
#     for sale in sales:
#         sale_info = {
#             'date': sale.get('date'),
#             'summ': sale.get('summ'),
#             'summ_with_discount': sale.get('summ_with_discount'),
#             'bonus_earned': sale.get('bonus_earned'),
#             'bonus_spent': sale.get('bonus_spent'),
#             'cheque_items_for_sales': []
#         }
#         cheque_items = sale.get('cheque_items_for_sales', [])
#         for item in cheque_items:
#             sale_item = {
#                 'item_name': item.get('item_name')
#             }
#             sale_info['cheque_items_for_sales'].append(sale_item)
#         data_sales.append(sale_info)
#     return data_sales


# def get_sales_history_sul(phone, view):
#     token = get_token_sul()
#     if not token:
#         print('Функция get_sales_history_sul нет действующего TOKEN от 1С-Рарус')
#         return None

#     data = get_balance_sul(phone, 2)
#     print(data)
#     if not data:
#         print('Ошибка в получении ID карты пользователя из 1С-Рарус')
#         return None

#     headers = {
#         "Content-Type": "application/json",
#         "token": token
#     }

#     url = f"{SUL_URL.rstrip('/')}/organization/sale_info?card_id={data}"

#     response = requests.get(url, headers=headers)
#     result = response.json()

#     if result.get('code') == 114:
#         print('NoTransactions')
#         return {'status': 'NoTransactions'}
#     elif result.get('code') != 0:
#         print('Ошибка в получении истории покупок пользователя из 1С-Рарус')
#         return None
#     sales = result['sales'] if result['sales'] else None
#     if not sales:
#         print('Ошибка в получении истории покупок пользователя из 1С-Рарус/ История покупок пустая')
#         return None
#     if view == 1:
#         return format_sales_history_text(sales)
#     elif view == 2:
#         return format_sales_history_data(sales)
#     else:
#         print('Функция get_sales_history_sul Некорректный тип запроса')
#         return None

# def convert_unix_to_readable_date(unix_timestamp):
#     timestamp_seconds = unix_timestamp / 1000
#     readable_date = datetime.fromtimestamp(timestamp_seconds).strftime('%d.%m.%Y')
#     return readable_date


# def format_bonus(amount):
#     if amount is None:
#         return "0 бонусов"
#     if 11 <= amount % 100 <= 19:
#         return f"{amount} бонусов"
#     elif amount % 10 == 1:
#         return f"{amount} бонус"
#     elif 2 <= amount % 10 <= 4:
#         return f"{amount} бонуса"
#     else:
#         return f"{amount} бонусов"
