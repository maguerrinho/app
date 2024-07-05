from integration.bonussystem import register_in_sul, get_user_sul
from database.db_utils import register_user_db, data_cache, get_data_db
import time
from datetime import datetime, timezone
user_id = '56452132'
frist_name = 'Никита'
last_name = 'Писчасов'
full_name = 'Никита Писчасов'
phone = '799946076791'
user_sul_id = 'fsdf32fdscv2_3f32f_2f1fc32'
user_sul_gender = 'male'
card_id = '1dd7e910-14c1-44e0-ba79-5d2cdc88886a'
date_str = '11.12.1997'
date_obj = datetime.strptime(date_str, '%d.%m.%Y').replace(tzinfo=timezone.utc)
birthdate = int(date_obj.timestamp() * 1000)
data = {
    'user_id': user_id,
    'first_name': frist_name,
    'last_name': last_name,
    'full_name': full_name,
    'phone': phone,
    'user_sul_id': user_sul_id,
    'user_sul_gender': user_sul_gender,
    'birthdate': birthdate,
    'card_id': card_id,
    'active': 1
}
result = register_user_db(data)
print('Получает пользователя и mysql')
res = get_data_db(4, phone)
print(res)
