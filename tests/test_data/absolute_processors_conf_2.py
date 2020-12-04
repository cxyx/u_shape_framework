# coding=utf-8
# email:  lihanqing@datagrand.com
# create: 2019-03-27-22:56
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from u_shape_framework.build_in_processors import DEMO

import os
file_path = os.path.abspath(__file__)
absolute_path_to_processor = os.path.dirname(file_path)

processor_conf_list = [
    DEMO,
    {
        "name": "demo2",
        "module": "demo",
        "args": {},
        "type": "build_in",
        "comment": "This is a demo processor",
    },
    {
        "name": "demo3",
        "module": "demo",
        "args": {},
        "type": "build_in",
        "comment": "This is a demo processor",
    },
]

workflow_conf_dict = {
    'demo': [
        'demo',
        'workflow_demo3',
    ],
    'demo2': [
        'demo2',
    ],
    'demo3': [
        'demo3',
    ],
}
