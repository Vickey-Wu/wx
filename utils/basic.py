import json
import os
from datetime import datetime


def get_real_name(user_id):
    id_name_dict = {
        'oJo_v0-jh_eTVXjBbYJ83mNFQOI0': {
            'chinese': '全震',
            'pinyin': 'quanzhen'
        },
        'oJo_v0xuujTgX7lhNIw28Ff_Qhuc': {
            'chinese': '超胖子',
            'pinyin': 'chaopangzi'
        },
        'oJo_v06K5xUTXXGoKSCpBVHrHKmM': {
            'chinese': '周新铮',
            'pinyin': 'zhouxinzheng'
        },
        'oJo_v057WiIXxBIwz_5mV4IXQy1Y': {
            'chinese': '吴键鸿',
            'pinyin': 'wujianhong'
        },
        'oJo_v05AVVhvwEk-Y7dC_EbLTyc4': {
            'chinese': '吴伟机',
            'pinyin': 'wuweiji'
        },
        'oJo_v02zMPy6gesgPc1fEhAJCWs0': {
            'chinese': '卢盘灿',
            'pinyin': 'lupancan'
        },
    }
    chinese = id_name_dict.get(user_id, {}).get('chinese', '')
    pinyin = id_name_dict.get(user_id, {}).get('pinyin', '')
    return '  mmmmm  '.join([str(i) for i in [user_id, chinese, pinyin]])


def read_local_file(file_today: str) -> dict:
    """
    only get data once every day, read data after get data from api

    Args:
        file_today: local json filename

    Returns:
        python dict for json data
    """
    if file_today.endswith('json'):
        data = json.load(open(file_today, encoding='utf-8'))
    if file_today.endswith('txt'):
        data = open(file_today, encoding='utf-8').read()
    return data


def write_local_file(file_today: str, data) -> None:
    """
    store data to local file
    Args:
        file_today: today json filename
        data: json data
    """
    if file_today.endswith('json'):
        json.dump(data, open(file_today, 'w', encoding='utf-8'))

    if file_today.endswith('txt'):
        with open(file_today, 'w', encoding='utf-8') as f:
            f.write(data)


def is_today_file_exist(file_today: str) -> bool:
    """
    check whether today_in_history-*.json file exist.

    Args:
        file_today: today json filename

    Returns:
        whether file exist
    """
    return os.path.exists(file_today)


def gen_today_file_name(template) -> str:
    """
    generate today json filename

    Returns:
        today_in_history-*.json
    """
    now = datetime.now().strftime('%m-%d')
    file_today: str = template % now
    return file_today
