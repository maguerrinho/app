# -------------------------------------------------------------------------
# Используемые публичные функции из этого файла:
# - update_user_db(user_id, phone=None, name=None, birth_date=None, active=None, id_card=None):
#   Обновляет данные пользователя в таблице bot_Users.
#   Параметры:
#   - user_id: int - идентификатор пользователя.
#   - phone: str - новый номер телефона пользователя (опционально).
#   - name: str - новое имя пользователя (опционально).
#   - birth_date: str - новая дата рождения пользователя в формате 'YYYY-MM-DD' (опционально).
#   - active: bool - новый статус активности пользователя (опционально).
#   - id_card: str - новый идентификационный номер пользователя (опционально).
#   Возвращает: None.

# - get_data_db(data_type, phone=None, user_id=None):
#   Получает данные из базы данных в зависимости от указанного типа.
#   Параметры:
#   - data_type: int - тип данных для запроса:
#       1 - настройки бота (Token, Url),
#       2 - настройки Сула (Login, Password, URL),
#       3 - список администраторов бота (User_id),
#       4 - информация о пользователе (phone - номер телефона пользователя, user_id - id пользователя).
#   - phone: str - номер телефона пользователя для запроса типа 4 (опционально).
#   - user_id: int - id пользователя для запроса типа 4 (опционально).
#   Возвращает: кортеж или список с данными из базы данных или None в случае ошибки.

# Запросы на создание таблиц в базе данных:

# CREATE TABLE IF NOT EXISTS Bot_Settings (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     Token VARCHAR(255) NOT NULL,
#     Url VARCHAR(255) NOT NULL
# );

# CREATE TABLE IF NOT EXISTS SUL_Settings (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     Login VARCHAR(100) NOT NULL,
#     Password VARCHAR(100) NOT NULL,
#     URL VARCHAR(255) NOT NULL
# );

# CREATE TABLE IF NOT EXISTS Administrators_List (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     User_id INT NOT NULL
# );

# CREATE TABLE IF NOT EXISTS bot_Users (
#    id INT AUTO_INCREMENT PRIMARY KEY,
#    user_id INT NOT NULL,
#    first_name VARCHAR(255),
#    last_name VARCHAR(255),
#    full_name VARCHAR(255),
#    birthdate DATE,
#    phone VARCHAR(20) NOT NULL,
#    user_sul_id INT,
#    gender VARCHAR(10),
#    card_id VARCHAR(100),
#    active BOOLEAN DEFAULT FALSE
# );
# -------------------------------------------------------------------------


import mysql.connector

from log.logging import log
from datetime import datetime, timezone

# Кэши для шаблонов сообщений и данных пользователей/администраторов
template_cache = {}
data_cache = {
    'admin_list': [],  # Инициализация пустым списком
    'users': {}        # Кэш для данных пользователей по user_id
}


# Функция для установки соединения с базой данных
def connect_to_db():
    """
    Устанавливает соединение с базой данных MySQL.
    Возвращает: объект подключения или None, если возникла ошибка.
    """
    try:
        connection = mysql.connector.connect(
            host='triniti.ru-hoster.com',
            user='adminN9A',
            password='8P07wftI6s',
            database='adminN9A',
            charset='utf8mb4'
        )
        return connection
    except mysql.connector.Error as err:
        log(f"Ошибка подключения к базе данных: {err}")
        return None


# Функция для выполнения запросов на получение данных из базы данных
def get_data_db(data_type, phone=None, user_id=None):
    """
    Получает данные из базы данных в зависимости от указанного типа.
    Параметры:
    - data_type: int - тип данных для запроса:
        1 - настройки бота (Token, Url),
        2 - настройки Сула (Login, Password, URL),
        3 - список администраторов бота (User_id),
        4 - информация о пользователе (phone - номер телефона пользователя, user_id - id пользователя).
    - phone: str - номер телефона пользователя для запроса типа 4 (опционально).
    - user_id: int - id пользователя для запроса типа 4 (опционально).
    Возвращает: кортеж или список с данными из базы данных или None в случае ошибки.
    """
    # Проверка кэша для данных типа 3 (список администраторов)
    if data_type == 3:
        if data_cache['admin_list']:
            return data_cache['admin_list']

    # Проверка кэша для данных типа 4 (информация о пользователе)
    if data_type == 4:
        if user_id is not None and user_id in data_cache['users']:
            return data_cache['users'][user_id]
        if phone is not None:
            for cached_user in data_cache['users'].values():
                if cached_user['phone'] == phone:
                    print("Данные из кеша")
                    return cached_user

    connection = connect_to_db()

    if connection:
        try:
            with connection.cursor() as cursor:
                if data_type == 1:
                    query = "SELECT Token, Url FROM Bot_Settings"
                    cursor.execute(query)
                    data = cursor.fetchone()
                elif data_type == 2:
                    query = "SELECT Login, Password, URL, shop_id FROM SUL_Settings"
                    cursor.execute(query)
                    data = cursor.fetchone()
                elif data_type == 3:
                    query = "SELECT User_id FROM Administrators_List"
                    cursor.execute(query)
                    data = cursor.fetchall()
                    if len(data) > 0:
                        data_cache['admin_list'] = [row[0] for row in data]  # Кэширование списка администраторов
                    else:
                        data_cache['admin_list'] = []  # Или другое значение по умолчанию, если нет данных
                elif data_type == 4:
                    if phone is not None and user_id is None:
                        query = "SELECT * FROM bot_Users WHERE phone = %s"
                        cursor.execute(query, (phone,))
                        data = cursor.fetchone()
                    elif user_id is not None and phone is None:
                        query = "SELECT * FROM bot_Users WHERE User_id = %s"
                        cursor.execute(query, (user_id,))
                        data = cursor.fetchone()
                    if data:
                        data_cache['users'][data['User_id']] = {
                            'user_id': data['User_id'],
                            'first_name': data['first_name'],
                            'last_name': data['last_name'],
                            'full_name': data['full_name'],
                            'birthdate': data['birthdate'],
                            'phone': data['phone'],
                            'user_sul_id': data['user_sul_id'],
                            'user_sul_gender': data['user_sul_gender'],
                            'card_id': data['card_id'],
                            'active': data['active']
                        }  # Кэширование данных пользователя
                        print(data_cache)
                        print(data_cache)
                    else:
                        log("Ошибка при вызове функции get_data_db с параметрами phone или user_id, "
                            "необходимо указать одно из двух значений.")
                        return None
                else:
                    log("Ошибка при вызове функции get_data_db передан некорректный тип данных.")
                    return None

            return data

        except mysql.connector.Error as err:
            log(f"Ошибка при выполнении запроса в get_data_db: {err}")
            return None

        finally:
            connection.close()

    else:
        log("Не удалось подключиться к базе данных.")
        return None


# Функция для обновления данных пользователя
def update_user_db(user_id, phone=None, name=None, birth_date=None, active=None, id_card=None):
    """
    Обновляет данные пользователя в таблице bot_Users.
    Параметры:
    - user_id: int - идентификатор пользователя.
    - phone: str - новый номер телефона пользователя (опционально).
    - name: str - новое имя пользователя (опционально).
    - birth_date: str - новая дата рождения пользователя в формате 'YYYY-MM-DD' (опционально).
    - active: bool - новый статус активности пользователя (опционально).
    - id_card: str - новый идентификационный номер пользователя (опционально).
    Возвращает: None.
    """
    connection = connect_to_db()

    if connection:
        try:
            with connection.cursor() as cursor:
                update_query = "UPDATE bot_Users SET "
                update_data = []

                if phone is not None:
                    update_data.append("phone = %s")
                if name is not None:
                    update_data.append("name = %s")
                if birth_date is not None:
                    update_data.append("birth_date = %s")
                if active is not None:
                    update_data.append("Active = %s")
                if id_card is not None:
                    update_data.append("id_card = %s")

                update_query += ", ".join(update_data)
                update_query += " WHERE User_id = %s"

                update_values = []
                if phone is not None:
                    update_values.append(phone)
                if name is not None:
                    update_values.append(name)
                if birth_date is not None:
                    update_values.append(birth_date)
                if active is not None:
                    update_values.append(active)
                if id_card is not None:
                    update_values.append(id_card)
                update_values.append(user_id)

                cursor.execute(update_query, update_values)
                connection.commit()

                log(f"Данные пользователя с User_id {user_id} успешно обновлены.")
                data_cache['users'][user_id] = (user_id, phone, name, birth_date, active, id_card)  # Обновление кэша

        except mysql.connector.Error as err:
            log(f"Ошибка при выполнении запроса в update_user_db: {err}")

        finally:
            connection.close()

    else:
        log("Невозможно установить соединение с базой данных.")


def register_user_db(data):
    """
    Регистрирует нового пользователя в базе данных.
    Параметры:
    - data: dict - словарь с данными пользователя.
        user_id = user_id (MySQL)
        frist_name = frist_name (MySQL)
        last_name = last_name (MySQL)
        full_name = full_name (MySQL)
        birthdate = birthdate (MySQL)
        phone = phone (MySQL)
        user_sul_id = user_sul_id (MySQL)
        user_sul_gender = gender (MySQL)
        card_id = card_id (MySQL)
    Возвращает: None.
    """
    connection = connect_to_db()

    if connection:
        try:
            with connection.cursor() as cursor:
                birthdate_unix = data['birthdate'] // 1000
                birthdate = datetime.fromtimestamp(birthdate_unix, tz=timezone.utc).strftime('%d.%m.%Y')
                insert_query = """
                INSERT INTO bot_Users (user_id, first_name, last_name, full_name, birthdate, 
                phone, user_sul_id, gender, card_id, active)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_query, (
                    data['user_id'],
                    data['first_name'],
                    data['last_name'],
                    data['full_name'],
                    birthdate,
                    data['phone'],
                    data['user_sul_id'],
                    data['user_sul_gender'],
                    data['card_id'],
                    data['active']

                ))
                connection.commit()

                log(f"Пользователь с User_id {data['user_id']} успешно зарегистрирован.")
                data_cache['users'][data['user_id']] = {
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'full_name': data['full_name'],
                    'birthdate': data['birthdate'],
                    'phone': data['phone'],
                    'user_sul_id': data['user_sul_id'],
                    'user_sul_gender': data['user_sul_gender'],
                    'card_id': data['card_id'],
                    'active': data['active']
                }
                print(data_cache)
        except mysql.connector.Error as err:
            log(f"Ошибка при выполнении запроса в register_user_db: {err}")

        finally:
            connection.close()

    else:
        log("Невозможно установить соединение с базой данных.")


# Функция для чтения шаблона из базы данных или кэша
def read_template(template_id):
    """
    Возвращает текст шаблона из базы данных или кэша по его идентификатору.
    """
    if template_id in template_cache:
        return template_cache[template_id]
    
    connection = connect_to_db()
    if connection:
        try:
            cursor = connection.cursor()
            query = "SELECT template_text FROM MessageTemplates WHERE template_id = %s"
            cursor.execute(query, (template_id,))
            result = cursor.fetchone()
            if result:
                template_cache[template_id] = result[0]
                return result[0]
            else:
                return None
        except mysql.connector.Error as err:
            log(f"Ошибка при чтении шаблона: {err}")
            return None
        finally:
            connection.close()


# Функция для обновления шаблона в базе данных и кэше
def update_template(template_id, template_text):
    """
    Обновляет текст шаблона в базе данных и кэше по его идентификатору.
    """
    connection = connect_to_db()
    if connection:
        try:
            cursor = connection.cursor()
            query = "UPDATE MessageTemplates SET template_text = %s WHERE template_id = %s"
            cursor.execute(query, (template_text, template_id))
            connection.commit()
            log(f"Шаблон с ID '{template_id}' успешно обновлен.")
            template_cache[template_id] = template_text
        except mysql.connector.Error as err:
            log(f"Ошибка при обновлении шаблона: {err}")
        finally:
            connection.close()
