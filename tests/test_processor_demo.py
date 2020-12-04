# coding=utf-8
# email: lihanqing@datagrand.com
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import sys

sys.path.append("../")

import unittest
from u_shape_framework.processors.processor_demo import ProcessorDemo


class TestProcessorDemo(unittest.TestCase):

    def test_down_method(self):
        processor_args = {}
        processor = ProcessorDemo('demo', processor_args)

        tmp_result = {}
        output = {}
        request_property = {}
        processor.down(tmp_result, output, request_property)
        result = output['demo_result']
        self.assertEqual(result, 'demo')

    def test_up_method(self):
        processor_args = {}
        processor = ProcessorDemo('demo', processor_args)

        tmp_result = {}
        output = {'demo_result': 'demo'}
        request_property = {}
        processor.up(tmp_result, output, request_property)
        result = output['demo_result']
        self.assertEqual(result, 'demo')


if __name__ == '__main__':
    unittest.main()
