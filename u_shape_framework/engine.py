# coding: utf-8
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import copy
import importlib
import os
import sys
import threading
import traceback
from time import sleep
from . import get_logger
from .workflow import Workflow
from typing import Dict, Text, List, Any
from .conf_merger import ConfMerger
from .user_manager import UserManager

_engine = None


class Status(object):
    NotInitialized = 'not_initialized'
    Initializing = 'initializing'
    Success = 'success'
    Failed = 'failed'


_status = Status.NotInitialized


def get_status():
    # type: () -> Text
    return _status


def get_current_engine():
    # type: () -> Engine
    if _status == Status.NotInitialized:
        raise RuntimeError('Engine is not initialized')
    elif _status == Status.Initializing:
        raise RuntimeError('Engine is initializing')
    elif _status == Status.Failed:
        raise RuntimeError('Engine is failed to initialize')
    else:
        return _engine


def initialize_engine(conf_module, override_conf_module_path=None, monitor_mode='auto', user_management_path=None):
    global _status
    _status = Status.Initializing
    try:
        global _engine
        _engine = Engine(conf_module, override_conf_module_path, monitor_mode, user_management_path)
        _status = Status.Success
    except Exception as e:
        get_logger().exception(e)
        _status = Status.Failed
    return _status


class Engine(object):

    def __init__(self, conf_module, override_conf_module_path=None, monitor_mode='auto', user_management_path=None):
        # type: (Any, Any, Text, Text) -> Engine
        self._conf_module = conf_module
        if user_management_path:
            self._user_manager = UserManager(user_management_path)
            self._merge_default_args(conf_module.processor_conf_list)
        else:
            self._user_manager = None

        self._override_conf_module_path = override_conf_module_path

        self._processor_conf_list, self._workflow_conf_dict, self._relative_import_base_package = self._parse_conf()

        self._processor_instance_dict = {}
        self._workflow_instance_dict = {}
        self._load_processors()
        self._load_workflows()
        if self._override_conf_module_path and monitor_mode == 'auto':
            self._auto_monitor_override_module()

    def _merge_default_args(self, processor_conf_list):
        for processor_conf in processor_conf_list:
            processor_name = processor_conf['name']
            default_args = self._user_manager.get_default_conf('processor_args', processor_name)
            processor_conf.update({"args": default_args})

    def get_user_manager(self):
        return self._user_manager

    def get_workflow(self, workflow_name):
        # type: (Text) -> Workflow
        return self._workflow_instance_dict[workflow_name]

    def update(self):
        modified_processor_conf_list, modified_workflow_conf_dict, _ = self._parse_conf()

        different_processor_conf_list = ConfMerger.find_difference_in_processor_conf_lists(
            self._processor_conf_list, modified_processor_conf_list)
        if different_processor_conf_list:
            self._load_processors(different_processor_conf_list)
            self._processor_conf_list = modified_processor_conf_list
            self._load_workflows(self._workflow_conf_dict)

        different_workflow_conf_dict = ConfMerger.find_difference_in_workflow_conf_dicts(
            self._workflow_conf_dict, modified_workflow_conf_dict)
        if different_workflow_conf_dict:
            self._load_workflows(different_workflow_conf_dict)
            self._workflow_conf_dict = modified_workflow_conf_dict

    def _auto_monitor_override_module(self):
        self._check_update_thread = CheckUpdateThread(self)
        self._check_update_thread.setDaemon(True)
        self._check_update_thread.start()

    def _parse_conf(self):
        processor_conf_list = copy.deepcopy(self._conf_module.processor_conf_list)
        workflow_conf_dict = copy.deepcopy(self._conf_module.workflow_conf_dict)
        if self._override_conf_module_path:
            try:
                override_conf_module_path = os.path.dirname(self._override_conf_module_path)
                if override_conf_module_path not in sys.path:
                    sys.path.append(os.path.dirname(self._override_conf_module_path))
                override_conf_module = importlib.import_module(os.path.basename(self._override_conf_module_path))
                if sys.version > '3':
                    importlib.reload(override_conf_module)
                else:
                    reload(override_conf_module)
                ConfMerger.merge_processor_conf_lists(processor_conf_list, override_conf_module.processor_conf_list)
                ConfMerger.merge_workflow_conf_dicts(workflow_conf_dict, override_conf_module.workflow_conf_dict)
            except Exception as e:
                get_logger().debug('cannot load override conf module, message {}'.format(e))

        if hasattr(self._conf_module, 'absolute_path_to_processor'):
            path_to_processor = self._conf_module.absolute_path_to_processor
            if path_to_processor not in sys.path:
                sys.path.append(path_to_processor)
            relative_import_base_package = None
        else:
            if hasattr(self._conf_module, 'relative_path_to_processor'):
                path_to_processor = self._conf_module.relative_path_to_processor
            else:
                path_to_processor = '..app.processors'
            relative_import_base_module = importlib.import_module(path_to_processor, self._conf_module.__package__)
            relative_import_base_package = relative_import_base_module.__name__
        return processor_conf_list, workflow_conf_dict, relative_import_base_package

    def _load_processors(self, processor_conf_list=None):
        # type: (List) -> None
        if processor_conf_list:
            load_processor_conf_list = processor_conf_list
        else:
            load_processor_conf_list = self._processor_conf_list
        for processor_conf in load_processor_conf_list:
            processor_name = processor_conf['name']
            processor_instance = self._load_processor(copy.deepcopy(processor_conf))
            self._processor_instance_dict[processor_name] = processor_instance
        get_logger().info('load processors success.')

    def _load_processor(self, processor_conf):
        # type: (Dict) -> Processor
        processor_name = processor_conf['name']
        processor_module = processor_conf['module']
        processor_args = processor_conf['args']
        processor_enable = processor_args.pop('enable') if 'enable' in processor_args else True
        processor_type = processor_conf.get('type', 'custom')
        processor_comment = processor_conf.get('comment', '')
        get_logger().info('load processor: {}, type: {}'.format(processor_name, processor_type))
        try:
            if '.' in processor_module:
                sub_package, short_module_name = processor_module.rsplit('.', 1)
                module_name = 'processor_' + short_module_name
                full_module_name = sub_package + '.' + module_name
            else:
                module_name = 'processor_' + processor_module
                full_module_name = module_name
            class_name = ''.join([c.capitalize() for c in module_name.split('_')])

            if processor_type == 'custom':
                relative_import_base_package = self._relative_import_base_package
            elif processor_type == 'build_in':
                relative_import_base_package = __package__ + '.processors'
            else:
                raise RuntimeError('type {} not support'.format(processor_type))

            if relative_import_base_package:
                full_module_name = '.' + full_module_name
                module = importlib.import_module(full_module_name, relative_import_base_package)
            else:
                module = importlib.import_module(full_module_name)
            processor_class = getattr(module, class_name)
            return processor_class(
                name=processor_name,
                processor_args=processor_args,
                comment=processor_comment,
                user_manager=self._user_manager,
                enable=processor_enable)
        except Exception as e:
            get_logger().error('load processor_{} error, exit. error info: {}'.format(processor_name, str(e)))
            get_logger().error(traceback.format_exc())
            exit(-1)

    def _load_workflows(self, workflow_dict=None):
        # type: (Dict) -> None
        if workflow_dict:
            load_workflow_conf_dict = workflow_dict
        else:
            load_workflow_conf_dict = self._workflow_conf_dict
        workflow_name_list = self._topological_sort(load_workflow_conf_dict)

        for workflow_name in workflow_name_list:
            self._workflow_instance_dict[workflow_name] = self._load_workflow(workflow_name,
                                                                              load_workflow_conf_dict[workflow_name])

    def _load_workflow(self, workflow_name, processor_name_list):
        # type: (Text, List) -> Workflow
        return Workflow(workflow_name, processor_name_list, self._processor_instance_dict, self._workflow_instance_dict)

    def _topological_sort(self, workflow_conf):
        graph = {}
        for k, v in workflow_conf.items():
            graph[k] = [n[len('workflow_'):] for n in v if n.startswith('workflow_')]
        in_degrees = dict((u, 0) for u in graph)
        vertex_num = len(in_degrees)
        for u in graph:
            for v in graph[u]:
                in_degrees[v] += 1
        q = [u for u in in_degrees if in_degrees[u] == 0]
        workflow_list = []
        while q:
            u = q.pop(0)
            workflow_list.append(u)
            for v in graph[u]:
                in_degrees[v] -= 1
                if in_degrees[v] == 0:
                    q.append(v)
        if len(workflow_list) != vertex_num:
            raise RuntimeError("there's a circle in workflow conf.")
        workflow_list.reverse()
        return workflow_list


class CheckUpdateThread(threading.Thread):

    def __init__(self, engine, interval=1):
        # type: (Engine, float) -> CheckUpdateThread
        super(CheckUpdateThread, self).__init__()
        self._engine = engine
        self._interval = interval

    def run(self):
        while True:
            sleep(self._interval)
            self._engine.update()
