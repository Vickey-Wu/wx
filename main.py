# -*- coding: utf-8 -*-
import os

from flask import Flask, request, abort
from wechatpy import parse_message, create_reply
from wechatpy.exceptions import (
    InvalidSignatureException,
    InvalidAppIdException,
)
from wechatpy.utils import check_signature

from utils.bingdwendwen import bingdwendwen
from utils.calculate import calc
from utils.today_in_history import today_in_history
from utils.translate import translate
from utils.logger import logger

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
    signature = request.args.get("signature", "")
    timestamp = request.args.get("timestamp", "")
    nonce = request.args.get("nonce", "")
    encrypt_type = request.args.get("encrypt_type", "raw")
    msg_signature = request.args.get("msg_signature", "")

    try:
        check_signature(TOKEN, signature, timestamp, nonce)
        logger.info(TOKEN)
    except InvalidSignatureException:
        abort(403)

    if request.method == "GET":
        echo_str = request.args.get("echostr", "")
        return echo_str

    # POST request
    elif encrypt_type == "raw":
        # plaintext mode
        msg = parse_message(request.data)
        logger.info(msg)
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


def replay_message(msg):
    content: str = msg.content.strip()
    logger.info('in replay message')
    logger.info(content)
    logger.info(str(type(content)))
    result = map_keyword_to_func(content)
    reply = create_reply(result, msg)
    return reply


def map_keyword_to_func(content):
    if not content:
        return ''

    keyword = content.split()[0]

    keyword_action_dict = {
        '历史': {'func': today_in_history, 'param': ''},
        'history': {'func': today_in_history, 'param': ''},
        '冰墩墩': {'func': bingdwendwen, 'param': ''},
        '翻译': {'func': translate, 'param': content},
        'translate': {'func': translate, 'param': content},
        '计算': {'func': calc, 'param': content},
        'calc': {'func': calc, 'param': content},
    }
    func = keyword_action_dict.get(keyword, {}).get('func', '')
    param = keyword_action_dict.get(keyword, {}).get('param', '')
    logger.info(str(func))
    logger.info(str(param))

    if not func:
        return ''

    if param:
        result = func(param)
    else:
        result = func()
    result = str(result)
    logger.info('result')
    logger.info(result)
    return result


if __name__ == "__main__":
    app.run("0.0.0.0", 8081, debug=True)
