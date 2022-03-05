# -*- coding: utf-8 -*-
import os

import xmltodict
from flask import Flask, request, abort
from wechatpy import parse_message, create_reply
from wechatpy.replies import ImageReply
from wechatpy.exceptions import (
    InvalidSignatureException,
    InvalidAppIdException,
)
from wechatpy.utils import check_signature, to_text

from utils.bingdwendwen import bingdwendwen
from utils.calculate import calc
from utils.news_60s import get_news_60s
from utils.today_in_history import today_in_history
from utils.translate import translate
from utils.logger import logger
from utils.first_message import first_message

# here to set your custom token, e.g.: abcde
TOKEN = os.getenv("WECHAT_TOKEN", "")
AES_KEY = os.getenv("WECHAT_AES_KEY", "")
APPID = os.getenv("WECHAT_APPID", "")

app = Flask(__name__)


@app.route("/")
def index():
    return 'index'
    # host = request.url_root
    # return render_template("index.html", host=host)


@app.route("/wx", methods=["GET", "POST"])
def wechat():
    logger.info('request: ' + str(request))
    signature = request.args.get("signature", "")
    timestamp = request.args.get("timestamp", "")
    nonce = request.args.get("nonce", "")
    encrypt_type = request.args.get("encrypt_type", "raw")
    msg_signature = request.args.get("msg_signature", "")

    try:
        check_signature(TOKEN, signature, timestamp, nonce)
        logger.info('token: ' + TOKEN)
    except InvalidSignatureException:
        abort(403)

    if request.method == "GET":
        echo_str = request.args.get("echostr", "")
        return echo_str

    # POST request
    elif encrypt_type == "raw":
        # plaintext mode
        logger.info('request.data')
        logger.info('request.data type: ' + str(type(request.data)))
        logger.info('request.data content: ' + str(request.data))

        from_user_name, message, message_type, msg = extract_field_from_request_data()

        # if someone subscribes, send init message
        subscribe = is_subscribe(message, message_type)
        if subscribe:
            reply = create_reply(first_message(), msg)
            return reply.render()

        if msg.type == "text":
            reply = replay_message(msg, from_user_name)
        else:
            reply = create_reply("Sorry, can not handle this for now.", msg)
        return reply.render()
    else:
        # encryption mode
        from wechatpy.crypto import WeChatCrypto

        crypto = WeChatCrypto(TOKEN, AES_KEY, APPID)
        try:
            msg = crypto.decrypt_message(request.data, msg_signature, timestamp, nonce)
        except (InvalidSignatureException, InvalidAppIdException):
            abort(403)
        else:
            msg = parse_message(msg)
            if msg.type == "text":
                reply = create_reply(msg.content, msg)
            else:
                reply = create_reply("Sorry, can not handle this for now", msg)
            return crypto.encrypt_message(reply.render(), nonce, timestamp)


def extract_field_from_request_data():
    message = xmltodict.parse(to_text(request.data))['xml']
    from_user_name = message['FromUserName']
    logger.info('FromUserName: ' + str(from_user_name))

    message_type = message['MsgType'].lower()
    logger.info('MsgType: ' + str(message_type))

    msg = parse_message(request.data)
    logger.info('msg')
    logger.info('msg type: ' + str(type(msg)))
    logger.info('msg content: ', msg)

    return from_user_name, message, message_type, msg


def is_subscribe(message, message_type):
    if message_type == 'event' or message_type.startswith('device_'):
        if 'Event' in message:
            logger.info('event in message')
            event_type = message['Event'].lower()
        else:
            event_type = ''

        if event_type == 'subscribe':
            return True
        else:
            return False


def replay_message(msg, user):
    content: str = msg.content.strip()
    logger.info('in replay message')
    logger.info('content type: ' + str(type(content)))
    logger.info('content: ' + content)
    result = map_keyword_to_func(content, user)
    reply = create_reply(result, msg)
    return reply


def map_keyword_to_func(content, user):
    if not content:
        return ''

    keyword = content.split()[0]

    keyword_action_dict = {
        '历史': {'func': today_in_history, 'param': ''},
        'history': {'func': today_in_history, 'param': ''},
        '冰墩墩': {'func': bingdwendwen, 'param': ''},
        '新闻': {'func': get_news_60s, 'param': ''},
        '翻译': {'func': translate, 'param': (content,)},
        'translate': {'func': translate, 'param': (content,)},
        '计算': {'func': calc, 'param': (content, user)},
        'calc': {'func': calc, 'param': (content, user)},
    }
    func = keyword_action_dict.get(keyword, {}).get('func', '')
    param = keyword_action_dict.get(keyword, {}).get('param', '')
    logger.info('execute function: ' + str(func))
    logger.info('params: ' + str(param))

    if not func:
        return ''

    if param:
        result = func(*param)
    else:
        result = func()
    result = str(result)
    logger.info('result')
    logger.info('result type: ' + str(type(result)))
    logger.info('result content: ' + result)
    return result


if __name__ == "__main__":
    app.run("0.0.0.0", 8081, debug=True)
