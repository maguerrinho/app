from integration.bonussystem import register_in_sul
from datetime import datetime
phone = '79994607678'
login = '+79994607678'

date_str = '11.12.1997'
date_obj = datetime.strptime(date_str, '%d.%m.%Y')
birthdate = int(date_obj.timestamp() * 1000)

city = '1dd7e910-14c1-44e0-ba79-5d2cdc88886a'
gender = 'male'
name = 'Никита'
result = register_in_sul(login, name, phone, gender, birthdate, city)
print(result)