# -*- coding: utf-8 -*-

import unittest

import common
from definition import test
from src import aglab, util

class Test(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        util.dict_merge(test.contexts, common.contexts)
        self.state = aglab.State(test)
        print
        
    def testTurn_start_1(self):
        """turn_start: 手番順(turn_order)をセットする場合
        """
        args = ['1,2,3']
        common.turn_start(self.state, args)
        
        self.assertEqual(self.state.get_context('$turn-no'), 1)
        self.assertEqual(self.state.get_context('$turn-player'), 1)
        self.assertEqual(self.state.get_context('$next-player')[0], 2)
        self.assertEqual(self.state.get_context('$next-player')[1], 3)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
