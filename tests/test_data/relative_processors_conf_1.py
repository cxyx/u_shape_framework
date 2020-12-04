# coding=utf-8
# email:  lihanqing@datagrand.com
# create: 2019-03-27-22:56
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from u_shape_framework.build_in_processors import DEMO

relative_path_to_processor = 'test_data'

processor_conf_list = [
    DEMO,
]

workflow_conf_dict = {
    'demo': ['demo'],
}
