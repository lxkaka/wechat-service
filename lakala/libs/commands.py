#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 通用的一些方法类

import motor
import pytz
import redis
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.tornado import TornadoScheduler

_mongodb_db = None
_redis_client = None
_scheduler = None


def get_redis_client():
    global _redis_client
    _redis_client = _redis_client or redis.StrictRedis(host='redis')
    return _redis_client


def get_mongodb_db():
    global _mongodb_db
    _mongodb_db = _mongodb_db or motor.motor_tornado.MotorClient(host='mongo')['lakala']
    return _mongodb_db


def get_scheduler():
    global _scheduler
    _scheduler = _scheduler or TornadoScheduler(
        jobstores={'redis': RedisJobStore(host='redis')}, timezone=pytz.timezone('Asia/Shanghai'))
    return _scheduler
