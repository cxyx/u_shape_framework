# coding=utf-8
# email:  lihanqing@datagrand.com
# create: 2019-05-15-11:55
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import sys
import importlib
import os
from .conf_merger import ConfMerger
from . import get_logger


class UserManager(object):

    def __init__(self, conf_path, user_conf_folder='user_conf', default_user_name='default'):
        self._user_management_path = os.path.abspath(conf_path)
        self._user_conf_path = os.path.join(self._user_management_path, user_conf_folder)
        self._default_user_name = default_user_name
        sys.path.insert(0, self._user_management_path)
        sys.path.insert(0, self._user_conf_path)

    def get_user_conf(self, user_id, module_name, variance_name):
        try:
            user_module = importlib.import_module(user_id)
            if sys.version > '3':
                importlib.reload(user_module)
            else:
                reload(user_module)
            conf_module = importlib.import_module(user_id + '.' + module_name)
            if sys.version > '3':
                importlib.reload(conf_module)
            else:
                reload(conf_module)
            variance = getattr(conf_module, variance_name)
            if isinstance(variance, dict):
                default_variance = self.get_default_conf(module_name, variance_name)
                ConfMerger.merge_dict(default_variance, variance)
                variance = default_variance
        except Exception as e:
            variance = self.get_default_conf(module_name, variance_name)
        return variance

    def get_default_conf(self, module_name, variance_name):
        conf_module = importlib.import_module(self._default_user_name + '.' + module_name)
        variance = getattr(conf_module, variance_name)
        return variance

    def get_user_conf_path(self, user_id):
        return os.path.join(self._user_conf_path, user_id)

    def get_user_id_list(self):
        user_id_list = []
        if os.path.exists(self._user_conf_path):
            for user_id in os.listdir(self._user_conf_path):
                user_path = os.path.join(self._user_conf_path, user_id)
                if os.path.isdir(user_path):
                    user_id_list.append(user_id)
        return user_id_list
