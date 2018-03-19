#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import re

import requests
import tornado.web
from tornado.options import options
from wechatpy import create_reply, parse_message
from wechatpy.crypto import WeChatCrypto
from wechatpy.exceptions import InvalidAppIdException, InvalidSignatureException
from wechatpy.utils import check_signature

from libs.commands import get_mongodb_db
from wechat.commands import record_info, get_record


def get_history_weather(location, date):
    """历史天气"""
    url = 'https://free-api.heweather.com/s6/weather/historical'
    data = {
        'location': location,
        'date': date,
        'key': 'a17b5bfc80d04f38b13f242b43ce8bb0',
    }
    response = requests.get(url ,data)
    if response.status_code != 200:
        return None
    else:
        res = json.loads(response.content)
    return res


def get_life_style(data):
    """生活指数"""
    url = 'https://free-api.heweather.com/s6/weather/lifestyle'
    response = requests.get(url, data)
    if response.status_code != 200:
        return None
    else:
        res = json.loads(response.content)
        life_style = res.get('HeWeather6')[0].get('lifestyle')
        for style in life_style:
            if style['type'] == 'comf':
                return style['txt']
    return None


def get_weather_report(location=None):
    location = location if location else '徐汇,上海'
    data = {
        'location': location,
        'key': 'a17b5bfc80d04f38b13f242b43ce8bb0',
    }
    url = 'https://free-api.heweather.com/s6/weather/forecast'
    response = requests.get(url, data)
    if response.status_code != 200:
        content = '请求异常'
    else:
        res = json.loads(response.content)
        location_info = res.get('HeWeather6')[0].get('basic')
        weather_info = res.get('HeWeather6')[0].get('daily_forecast')
        life_style = get_life_style(data)
        content = '{}{}天气:\n 今天白天{}，晚上{}\n 气温{}-{}摄氏度\n 明天白天{}，晚上{}\n 气温{}-{}摄氏度\n舒适指数:\n {}'.format(
            location_info.get('parent_city'), location_info.get('location'),
            weather_info[0].get('cond_txt_d'), weather_info[0].get('cond_txt_n'), weather_info[0].get('tmp_min'),
            weather_info[0].get('tmp_max'),
            weather_info[1].get('cond_txt_d'), weather_info[1].get('cond_txt_n'), weather_info[1].get('tmp_min'),
            weather_info[1].get('tmp_max'), life_style
        )
    return content


async def handle_wechat_message(message):
    content = message.content
    record_id = 'lxlikelq'
    collection = get_mongodb_db()['counter']
    lx_count = 0
    lq_count = 0
    if content.startswith('lx'):
        lx_count = int(content.lstrip('lx').strip()) or 0
    if content.startswith('lq'):
        lq_count = int(content.lstrip('lq').strip()) or 0
    elif content.startswith('weather'):
        location = content.lstrip('weather').strip()
        return get_weather_report(location)
    elif content.startswith('天气'):
        location = content.lstrip('天气').strip()
        return get_weather_report(location)
    elif re.match(r'^\d{8}$', content):
        return await get_record(message)
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
                await record_info(msg)
                reply_content = await handle_wechat_message(msg)
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
                    reply_content = await handle_wechat_message(msg)
                    reply = create_reply(reply_content, msg, render=True)
                else:
                    reply = create_reply('暂时不支持该消息类型', msg, render=True)
                self.finish(crypto.encrypt_message(reply, nonce, timestamp))
            except (InvalidSignatureException, InvalidAppIdException):
                self.write_error(status_code=403)
