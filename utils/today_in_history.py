import json
import os
from datetime import datetime

import requests


def format_data(data: dict) -> str:
    """
    join each title by `\\n`

    Args:
        data: json data

    Returns:
        formatted text
    """
    events = []
    for i in data.get('result', []):
        date = i.get('date', '')
        title = i.get('title', '')
        events.append(', '.join([date, title]))

    return '\n'.join([
        # date, event
        '日期, 事件',
        *events
    ])


def get_data() -> dict:
    """
    data source, use requests get data

    Returns:
        python dict from api
    """
    url = 'https://api.oick.cn/lishi/api.php'
    response = requests.get(url).text
    response = json.loads(response)
    return response


def gen_today_file_name() -> str:
    """
    generate today json filename

    Returns:
        today_in_history-*.json
    """
    now = datetime.now().strftime('%m-%d')
    file_today: str = 'today_in_history-%s.json' % now
    return file_today


def is_today_file_exist(file_today: str) -> bool:
    """
    check whether today_in_history-*.json file exist.

    Args:
        file_today: today json filename

    Returns:
        whether file exist
    """
    return os.path.exists(file_today)


def write_local_file(file_today: str, data: dict) -> None:
    """
    store data to local file
    Args:
        file_today: today json filename
        data: json data
    """
    json.dump(data, open(file_today, 'w', encoding='utf-8'))


def today_in_history():
    file_today = gen_today_file_name()
    today_file_exist = is_today_file_exist(file_today)

    if today_file_exist:
        print('local file exist, get data from local file: %s' % file_today)
        data = read_local_file(file_today)
    else:
        print('local file not exist, get data from api')
        data = get_data()
        write_local_file(file_today, data)

    data = format_data(data)
    return data


def read_local_file(file_today: str) -> dict:
    """
    only get data once every day, read data after get data from api

    Args:
        file_today: local json filename

    Returns:
        python dict for json data
    """
    data = json.load(open(file_today, encoding='utf-8'))
    return data


if __name__ == '__main__':
    result = today_in_history()
    print(result)
