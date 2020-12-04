# coding=utf-8
# email:  lihanqing@datagrand.com
# create: 2018/5/11-下午2:16
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import logging

_logger = logging.getLogger('root')


def set_logger(target_logger):
    global _logger
    _logger = target_logger


def get_logger():
    return _logger
