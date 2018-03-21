#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# lakala's Server

import tornado.httpserver
import tornado.ioloop
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options

from handler import DebugHandler, KakaCounter
from wechat.wechat_handler import CounterReplyHandler

define('port', default=8888, help='run on the given port', type=int)
define('APPID', type=str)
define('TOKEN', type=str)
define('AES_KEY', type=str)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/counter/', KakaCounter),
            (r'/wechat_counter/', CounterReplyHandler),
            # 下面这个测试用的
            (r'/debug/', DebugHandler),
        ]
        settings = dict(
            blog_title='lakala',
            xsrf_cookies=False,
            cookie_secret='',
            login_url='/auth/login',
            debug=True,
        )
        super(Application, self).__init__(handlers, **settings)


def main():
    tornado.options.parse_config_file('server.conf')
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    # scheduler = get_scheduler()
    # scheduler.start()
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
