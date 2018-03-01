#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import tornado.web
from tornado.options import options
from wechatpy import parse_message, create_reply
from wechatpy.crypto import WeChatCrypto
from wechatpy.exceptions import InvalidSignatureException, InvalidAppIdException
from wechatpy.utils import check_signature

from libs.commands import get_mongodb_db


async def handle_wechat_message(message):
    record_id = 'lxlikelq'
    collection = get_mongodb_db()['counter']
    lx_count = 0
    lq_count = 0
    if message.startswith('lx'):
        lx_count = int(message.lstrip('lx').strip()) or 0
    if message.startswith('lq'):
        lq_count = int(message.lstrip('lq').strip()) or 0
    record = await collection.find_one({'_id': record_id})
    if record:
        lx_count += record.get('lx_count')
        lq_count += record.get('lq_count')
    await collection.update_one(
        {
            '_id': record_id
        },
        {
            '$set': {
                'lx_count': lx_count,
                'lq_count': lq_count
            }
        }, upsert=True

    )
    reply_content = '清你的次数已经累计到{}次\nkaka你的次数已经累计到{}次\nwatch your language!!!'.format(
        lq_count, lx_count)
    return reply_content


class CounterReplyHandler(tornado.web.RequestHandler):
    async def get(self, *args, **kwargs):
        signature = self.get_argument('signature', '')
        timestamp = self.get_argument('timestamp', '')
        nonce = self.get_argument('nonce', '')
        msg_signature = self.get_argument('msg_signature', '')
        echostr = self.get_argument('echostr', '')

        try:
            check_signature(options.TOKEN, signature, timestamp, nonce)
            self.finish(echostr)
        except InvalidSignatureException:
            self.write_error(status_code=403)

    async def post(self, *args, **kwargs):
        signature = self.get_argument('signature', '')
        timestamp = self.get_argument('timestamp', '')
        nonce = self.get_argument('nonce', '')
        encrypt_type = self.get_argument('encrypt_type', 'raw')
        msg_signature = self.get_argument('msg_signature', '')

        try:
            check_signature(options.TOKEN, signature, timestamp, nonce)
        except InvalidSignatureException:
            self.write_error(status_code=403)
        if encrypt_type == 'raw':
            msg = parse_message(self.request.body)
            if msg.type == 'text':
                reply_content = await handle_wechat_message(msg.content)
                reply = create_reply(reply_content, msg, render=True)
            else:
                reply = create_reply('暂时不支持该消息类型', msg, render=True)
            self.finish(reply)
        else:
            crypto = WeChatCrypto(options.TOKEN, options.AES_KEY, options.APPID)
            try:
                msg = crypto.decrypt_message(
                    self.request.body,
                    msg_signature,
                    timestamp,
                    nonce
                )
                if msg.type == 'text':
                    reply_content = await handle_wechat_message(msg.content)
                    reply = create_reply(reply_content, msg, render=True)
                else:
                    reply = create_reply('暂时不支持该消息类型', msg, render=True)
                self.finish(crypto.encrypt_message(reply, nonce, timestamp))
            except (InvalidSignatureException, InvalidAppIdException):
                self.write_error(status_code=403)
