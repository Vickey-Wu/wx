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

# here to set your custom token, e.g.: abcde
from utils.bingdwendwen import bingdwendwen
from utils.calculate import calc
from utils.today_in_history import today_in_history
from utils.translation import translation

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
            reply = str(reply)
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
