#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime

from libs.commands import get_mongodb_db


async def record_info(msg):
    """
    记录每条文本信息
    msg.source: openid
    msg.content: 消息体
    """

    collection = get_mongodb_db()['record']
    record_id = datetime.datetime.now().strftime('%Y%m%d')
    # await collection.delete_one({'_id': record_id})
    record = await collection.find_one({'_id': record_id})
    if record:
        content = '{}\n{}'.format(record.get(msg.source), msg.content)
    else:
        content = msg.content
    await collection.update_one(
        {
            '_id': record_id
        },
        {
            '$set': {
                msg.source: content,
            }
        }, upsert=True
    )


async def get_record(msg):
    """根据日期查询日记"""
    collection = get_mongodb_db()['record']
    record = await collection.find_one({'_id': msg.content})
    return record.get(msg.source) if record else None


