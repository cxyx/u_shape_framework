# coding=utf-8
# email: lihanqing@datagrand.com
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from .processor_base import ProcessorBase
from .. import get_logger


class ProcessorDemo(ProcessorBase):

    def load(self, processor_args):
        pass

    def up(self, tmp_result, output, request_property):
        pass

    def down(self, tmp_result, output, request_property):
        get_logger().info('start to output demo')
        output.update({
            'demo_result': 'demo',
        })
