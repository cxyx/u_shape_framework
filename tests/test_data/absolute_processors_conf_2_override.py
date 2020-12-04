# coding=utf-8
# email:  lihanqing@datagrand.com
# create: 2019-03-27-22:56
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

processor_conf_list = [
    {
        "name": "demo",
        "module": "demo",
        "args": {
            'test': 1
        },
    },
    {
        "name": "demo2",
        "module": "demo",
        "args": {
            'test': 2
        },
    },
]

workflow_conf_dict = {
    'demo': [
        'demo',
        'demo2',
    ],
}
