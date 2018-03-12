# -*- coding: utf-8 -*-
#
# Handler
import json

import tornado.web
from tornado.options import options

from libs.commands import get_mongodb_db


async def return_400_error(self: tornado.web.RequestHandler, message):
    self.set_status(400)
    self.finish(json.dumps({'message': message}, ensure_ascii=False))


class KakaCounter(tornado.web.RequestHandler):
    record_id = 'lxlikelq'
    collection = get_mongodb_db()['counter']

    async def post(self, *args, **kwargs):
        body = tornado.escape.json_decode(self.request.body)
        lx_count = body.get('lx_count', 0)
        lq_count = body.get('lq_count', 0)
        record = await self.collection.find_one({'_id': self.record_id})
        if record:
            lx_count += record.get('lx_count')
            lq_count += record.get('lq_count')
        await self.collection.update_one(
            {
                '_id': self.record_id
            },
            {
                '$set': {
                    'lx_count': lx_count,
                    'lq_count': lq_count
                }
            }, upsert=True

        )

    async def get(self, *args, **kwargs):
        record = await self.collection.find_one({'_id': self.record_id})
        self.finish(json.dumps(record, ensure_ascii=False))


class DebugHandler(tornado.web.RequestHandler):
    async def get(self, *args, **kwargs):
        data = {
            'APPID': options.APPID,
            'TOKEN': options.TOKEN,
            'author': 'lxkaka',
        }
        self.finish(json.dumps(data, ensure_ascii=False))
