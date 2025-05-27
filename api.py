# api.py

import requests
import os
import json
from datetime import datetime

api_user = os.environ.get('API_USER')
api_password = os.environ.get('API_PASSWORD')

if not api_user:
    api_user = input('Введите api_user: ')
if not api_password:
    import getpass
    api_password = getpass.getpass('api_password: ')

def get_metric(hosts, metrics, end_time=int(datetime.now().timestamp()), step=30, delta=None):
    """
    Функция принимает список инстансов хостов, список метрик, время и интервал.
    Возвращает словарь.
    """
    HEADERS = { 'Content-Type': 'application/json' }
    URL = 'https://api.example.com/metrics'
    AUTH = (api_user, api_password)
    VALID_DATA = {
        'source': 'node_exporter',
        'host': hosts,
        'metric': metrics,
        'start_time': end_time - step,
        'end_time': end_time
    }
    if delta:
        VALID_DATA['delta'] = delta
    try:
        response = requests.post(URL, auth=AUTH, json=VALID_DATA, headers=HEADERS)
    except Exception as e:
        print('Не удалось получить ответ от API!', e)
        return None
    try:
        return json.loads(response.text)
    except Exception:
        print('Не получилось распарсить результат полученный от API:', str(datetime.fromtimestamp(end_time)), hosts)
        print(response.text)
        return None
