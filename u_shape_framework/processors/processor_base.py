# coding=utf-8
# email:  xgao85@gmail.com
# create: 2016年12月14日-下午4:21
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import abc
import threading
from typing import Dict, Text


class ProcessorBase(object):
    '''
    processor base class
    '''
    __metaclass__ = abc.ABCMeta

    def __init__(self, name, processor_args, comment='', user_manager=None, enable=True):
        self._name = name
        self._comment = comment
        self._user_manager = user_manager
        self._thread_local = threading.local()
        self._enable = enable
        self.load(processor_args)

    @property
    def name(self):
        return self._name

    @property
    def comment(self):
        return self._comment

    @abc.abstractmethod
    def load(self, processor_args):
        pass

    @abc.abstractmethod
    def up(self, tmp_result, output, request_property):
        # type: (Dict, Dict, Dict) -> None
        pass

    @abc.abstractmethod
    def down(self, tmp_result, output, request_property):
        # type: (Dict, Dict, Dict) -> None
        pass

    def process(self, tmp_result, output, request_property):
        # type: (Dict, Dict, Dict) -> Text
        if self._user_manager:
            self._thread_local.user_id = request_property['user_id']
            self._thread_local.user_args = self._get_user_args()
        else:
            self._thread_local.user_args = {}
            self._thread_local.user_id = 'default'
        direction = self.direction_controller(tmp_result, output, request_property)
        if direction == 'up':
            self.up(tmp_result, output, request_property)
        elif direction == 'down':
            self.down(tmp_result, output, request_property)
        else:
            raise RuntimeError('direction error, please check your code, direction is {}.'.format(direction))
        hook_direction = self.direction_hook(tmp_result, output, request_property)
        if hook_direction:
            direction = hook_direction
        return direction

    def direction_hook(self, tmp_result, output, request_property):
        return ''

    def direction_controller(self, tmp_result, output, request_property):
        # type: (Dict, Dict, Dict) -> Text
        if self.run_info:
            self.run_info = False
            return 'up'
        else:
            self.run_info = True
            return 'down'

    def _get_user_args(self):
        return self._user_manager.get_user_conf(self.user_id, 'processor_args', self.name)

    @property
    def user_args(self):
        return self._thread_local.user_args

    @property
    def user_id(self):
        return self._thread_local.user_id

    @property
    def run_info(self):
        return self._thread_local.run_info if hasattr(self._thread_local, 'run_info') else False

    @run_info.setter
    def run_info(self, value):
        self._thread_local.run_info = value

    @property
    def user_manager(self):
        return self._user_manager

    @property
    def enable(self):
        return self._enable
