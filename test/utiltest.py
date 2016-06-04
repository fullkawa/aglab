# -*- coding: utf-8 -*-

import unittest

import util

class UtilTestCase(unittest.TestCase):
        
    def setUp(self):
        unittest.TestCase.setUp(self)
    
    def test_build_urlpath_case1(self):
        lst = ['path', 'to', 'hoge']
        path = util.build_urlpath(lst)
        
        self.assertEqual(path, 'path/to/hoge')
    
    def test_build_urlpath_case2(self):
        lst = ['example', ('key1', 'value1'), ('key2', 'value2')]
        path = util.build_urlpath(lst)
        
        self.assertEqual(path, 'example/key1:value1/key2:value2')
        
    def test_build_urlqs(self):
        lst = [('key1', 'value1'), ('key2', 'value2')]
        qs = util.build_urlqs(lst)
        
        self.assertEqual(qs, 'key1=value1&key2=value2')
