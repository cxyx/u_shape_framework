# coding=utf-8
# email: lihanqing@datagrand.com
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import sys

sys.path.append("../")
from u_shape_framework.engine import initialize_engine, get_current_engine, Status
from tests.test_data import relative_processors_conf_1, absolute_processors_conf_2
import unittest
import os
from time import sleep


class TestWorkflow(unittest.TestCase):

    def test_relative(self):
        status = initialize_engine(relative_processors_conf_1, relative_processors_conf_1)
        assert status == Status.Success, 'status is {}'.format(status)

        engine = get_current_engine()
        workflow = engine.get_workflow('demo')

        request_property = {}
        output = workflow.run(request_property)

        result = output['demo_result']
        self.assertEqual(result, 'demo')

    def test_absolute(self):
        override_conf_module_path = os.path.join(
            os.path.dirname(__file__), 'test_data/absolute_processors_conf_2_override')
        status = initialize_engine(absolute_processors_conf_2, override_conf_module_path)
        assert status == Status.Success, 'status is {}'.format(status)

        engine = get_current_engine()
        workflow = engine.get_workflow('demo')

        request_property = {}
        output = workflow.run(request_property)

        result = output['demo_result']
        self.assertEqual(result, 'demo')


if __name__ == '__main__':
    unittest.main()
