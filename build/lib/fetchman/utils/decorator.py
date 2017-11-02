#!/usr/bin/env python
# -*- coding: utf-8 -*-

import functools
from fetchman.utils import logger
import traceback
import types
import time
import uuid


def check(func):
    @functools.wraps(func)
    def wrapper(self, response):
        if not response.m_response:
            response.request.meta['retry'] += 1
            # 最多重试3次
            if response.request.meta['retry'] < 4:
                retry_str = '\nrequest has been push to queue again! try time:' + str(response.request.meta['retry'])
                yield response.request
            else:
                retry_str = '\nrequest has been try max times! will not push again! try time:' + str(response.request.meta['retry'])

            if response.m_response is None:
                logger.error('response.m_response is None'
                             + '\nURL : ' + response.request.url
                             + retry_str)
            else:
                # 记录返回数据
                log_name = 'log/' + str(uuid.uuid1()) + '_log.txt'
                with open(log_name, 'wb') as f:
                    f.write(response.m_response.content)

                logger.error('response.m_response is failed 【' + str(response.m_response.status_code) + '】'
                             + '\nURL : ' + response.request.url
                             + '\nresponse: ' + log_name
                             + retry_str)
        else:
            try:
                process = func(self, response)
                if isinstance(process, types.GeneratorType):
                    for callback in process:
                        yield callback
            except Exception:
                # 记录返回数据
                log_name = 'log/' + str(uuid.uuid1()) + '_log.txt'
                with open(log_name, 'wb') as f:
                    f.write(response.m_response.content)

                logger.error('process error: ' + response.request.url
                             + '\nresponse: ' + log_name
                             + '\n' + traceback.format_exc())

    return wrapper


def timeit(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.clock()
        ret = func(*args, **kwargs)
        logger.info(func.__name__ + ' run time: ' + '{:.9f}'.format(time.clock() - start))
        return ret

    return wrapper


def timeit_generator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        rets = func(*args, **kwargs)
        start = time.clock()
        for ret in rets:
            yield ret
        logger.info(func.__name__ + ' run time: ' + '{:.9f}'.format(time.clock() - start))

    return wrapper


def tryCatch(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            ret = func(*args, **kwargs)
            return ret
        except Exception:
            logger.info('【%s】error:%s' % (func.__name__, traceback.format_exc()))

    return wrapper


def tryCatch_generator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            rets = func(*args, **kwargs)
            for ret in rets:
                yield ret
        except Exception:
            logger.info('【%s】error:%s' % (func.__name__, traceback.format_exc()))

    return wrapper
