# -*- coding: utf-8 -*-
import json
import os
from datetime import datetime

import requests
from flask import Flask, request, abort
from wechatpy import parse_message, create_reply
from wechatpy.exceptions import (
    InvalidSignatureException,
    InvalidAppIdException,
)
from wechatpy.utils import check_signature

# here to set your custom token, e.g.: abcd
TOKEN = os.getenv("WECHAT_TOKEN", "")
AES_KEY = os.getenv("WECHAT_AES_KEY", "")
APPID = os.getenv("WECHAT_APPID", "")

app = Flask(__name__)


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


def query(word: str) -> str:
    """
    query word meaning from api

    Args:
        word: word need be translated

    Returns:
        chinese meaning for words.
    """
    url = 'https://dict.youdao.com/jsonapi?q=%s' % word

    response: str = requests.get(url).text
    words: dict = json.loads(response)

    try:
        chinese: str = words.get(
            'web_trans', {}).get('web-translation', [])[0].get(
            'trans', [])[0].get('value', '')
    except IndexError:
        # Please input english word, for example: "translation hello"
        chinese: str = '请输入英文, 例如 "翻译 hello"'
    return chinese


def translation(words):
    if len(words.split()) == 2:
        word = words.split()[1]
        chinese = query(word)
        return chinese
    else:
        # Please input "translation hello"
        return '请输入 "翻译 hello"'


@app.route("/")
def index():
    return 'index'
    # host = request.url_root
    # return render_template("index.html", host=host)


@app.route("/wx", methods=["GET", "POST"])
def wechat():
    signature = request.args.get("signature", "")
    timestamp = request.args.get("timestamp", "")
    nonce = request.args.get("nonce", "")
    encrypt_type = request.args.get("encrypt_type", "raw")
    msg_signature = request.args.get("msg_signature", "")
    try:
        check_signature(TOKEN, signature, timestamp, nonce)
        print(TOKEN)
    except InvalidSignatureException:
        abort(403)
    if request.method == "GET":
        echo_str = request.args.get("echostr", "")
        return echo_str

    # POST request
    if encrypt_type == "raw":
        # plaintext mode
        msg = parse_message(request.data)
        if msg.type == "text":

            reply = replay_message(msg)

        else:
            reply = create_reply("Sorry, can not handle this for now", msg)
        return reply.render()
    else:
        # encryption mode
        from wechatpy.crypto import WeChatCrypto

        crypto = WeChatCrypto(TOKEN, AES_KEY, APPID)
        try:
            msg = crypto.decrypt_message(request.data, msg_signature, timestamp,
                                         nonce)
        except (InvalidSignatureException, InvalidAppIdException):
            abort(403)
        else:
            msg = parse_message(msg)
            if msg.type == "text":
                reply = create_reply(msg.content, msg)
            else:
                reply = create_reply("Sorry, can not handle this for now", msg)
            return crypto.encrypt_message(reply.render(), nonce, timestamp)


def calc(string):
    if len(string.split()) <= 1:
        # no expression
        return '没有表达式'

    expression = ' '.join(string.split()[1:])
    try:
        result = eval(expression)
    except (SyntaxError, TypeError):
        # expression has error
        result = '表达式不正确'
    return str(result)


def bingdwendwen():
    address = [
        # the address for python script which draw bingdwendwen
        '冰墩墩脚本代码下载地址',
        'https://idlepig.lanzouq.com/b030pptgj',
        # password:6u4g
        '密码:6u4g',
    ]
    return '\n'.join(address)


def replay_message(msg):
    if msg.content == '历史':  # history
        reply = create_reply(today_in_history(), msg)
    elif str(msg.content).startswith('翻译'):  # translation
        reply = create_reply(translation(msg.content), msg)
    elif str(msg.content).startswith('计算'):  # calculate
        reply = create_reply(calc(msg.content), msg)
    elif msg.content == '冰墩墩':  # bingdwendwen
        reply = create_reply(bingdwendwen(), msg)
    else:
        reply = create_reply('', msg)
    return reply


if __name__ == "__main__":
    app.run("0.0.0.0", 8081, debug=True)
