# coding=utf-8
# email:  lihanqing@datagrand.com
# create: 2018/7/3-下午12:57
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import sys

import os

sys.path.append(os.path.abspath('../../'))

import unittest
from HTMLTestRunner_cn import HTMLTestRunner


def run_all_test_cases():
    status = 0
    cur_path = os.path.abspath(os.path.dirname(__file__))
    ori_path = os.getcwd()
    os.chdir(os.path.join(cur_path, '../'))
    suite = unittest.TestSuite()
    suite.addTests(unittest.TestLoader().discover('.'))
    with open('TestReport.html', 'w') as f:
        runner = HTMLTestRunner(stream=f, title='Test Report', verbosity=2)
        result = runner.run(suite)
        if result.failure_count or result.error_count:
            status = 1

    os.chdir(ori_path)
    return status


if __name__ == '__main__':
    if run_all_test_cases():
        sys.exit(1)
