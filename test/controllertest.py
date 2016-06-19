import unittest

import controller

class Test(unittest.TestCase):

    def setUp(self):
        pass

    def testRandomizer(self):
        params = {
            'actions':  3,
            'seed':     0}
        randomizer = controller.Randomizer(params)
        
        ob = {} # dummy observation
        self.assertEqual(randomizer.action(ob), 2)
        self.assertEqual(randomizer.action(ob), 2)
        self.assertEqual(randomizer.action(ob), 1)
        self.assertEqual(randomizer.action(ob), 0)
        self.assertEqual(randomizer.action(ob), 1)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()