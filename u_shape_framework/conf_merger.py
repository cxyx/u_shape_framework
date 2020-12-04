# coding=utf-8
# email:  lihanqing@datagrand.com
# create: 2019-05-17-13:57
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from . import get_logger
from dictdiffer import diff
from typing import Dict, List
import operator


class ConfMerger(object):

    @staticmethod
    def merge_processor_conf_lists(processor_conf_list, override_processor_conf_list):
        # type: (List, List) -> None
        for override_processor_conf in override_processor_conf_list:
            correspond_processor_conf =\
                ConfMerger._find_correspond_processor_conf(override_processor_conf, processor_conf_list)

            if correspond_processor_conf:
                try:
                    args = correspond_processor_conf['args']
                    override_args = override_processor_conf['args']
                    ConfMerger.merge_dict(args, override_args)
                except Exception as e:
                    get_logger().warn('processor {} merge not success.'.format(correspond_processor_conf['name']))
                    get_logger().warn('message {}.'.format(e))

    @staticmethod
    def merge_dict(default_dict, override_dict):
        """
        merge override_dict into default_dict
        :param default_dict:
        :param override_dict:
        """
        for difference in diff(default_dict, override_dict):
            diff_type, key, value = difference
            if diff_type == 'change':
                target_conf = default_dict
                key_path = key.split('.')
                for sub_key in key_path[:-1]:
                    target_conf = target_conf[sub_key]
                target_conf.update({key_path[-1]: value[1]})

    @staticmethod
    def find_difference_in_processor_conf_lists(old_processor_conf_list, new_processor_conf_list):
        # type: (List, List) -> List
        different_processor_conf_list = []
        for new_processor_conf in new_processor_conf_list:
            correspond_old_processor_conf = ConfMerger._find_correspond_processor_conf(
                new_processor_conf, old_processor_conf_list)
            if list(diff(new_processor_conf, correspond_old_processor_conf)):
                different_processor_conf_list.append(new_processor_conf)
        return different_processor_conf_list

    @staticmethod
    def merge_workflow_conf_dicts(workflow_conf_dict, override_workflow_conf_dict):
        # type: (Dict, Dict) -> None
        for override_workflow_name, override_processor_name_list in override_workflow_conf_dict.items():
            if override_workflow_name in workflow_conf_dict:
                correspond_processor_name_list = workflow_conf_dict[override_workflow_name]
            else:
                raise RuntimeError('override conf error, workflow {} not exist'.format(override_workflow_name))
            if not operator.eq(correspond_processor_name_list, override_processor_name_list):
                workflow_conf_dict[override_workflow_name] = override_processor_name_list

    @staticmethod
    def find_difference_in_workflow_conf_dicts(old_workflow_conf_dict, new_workflow_conf_dict):
        # type: (Dict, Dict) -> Dict
        update_workflow_conf_dict = {}
        for new_workflow_name, new_processor_name_list in new_workflow_conf_dict.items():
            if new_workflow_name in old_workflow_conf_dict:
                correspond_old_processor_name_list = old_workflow_conf_dict[new_workflow_name]
            else:
                raise RuntimeError('override conf error, workflow {} not exist'.format(new_workflow_name))
            if not operator.eq(correspond_old_processor_name_list, new_processor_name_list):
                update_workflow_conf_dict[new_workflow_name] = new_processor_name_list
        return update_workflow_conf_dict

    @staticmethod
    def _find_correspond_processor_conf(target_processor_conf, processor_conf_list):
        # type: (Dict, List) -> Dict
        for processor_conf in processor_conf_list:
            if target_processor_conf['name'] == processor_conf['name']:
                return processor_conf
