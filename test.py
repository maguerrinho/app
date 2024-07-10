import requests

API_TOKEN = '6033010096:AAF0wQmSWOgCsCWPFacUNNtrVyJ4cptBe90'
url = f"https://api.telegram.org/bot{API_TOKEN}/getWebhookInfo"

response = requests.get(url)
webhook_info = response.json()

print(webhook_info)

