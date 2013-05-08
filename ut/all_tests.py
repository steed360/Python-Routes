
# source: http://stackoverflow.com/questions/1896918/running-unittest-with-typical-test-directory-structure

import glob
import unittest

def create_test_suite():

    test_file_strings = glob.glob('ut/test_*.py')
    module_strings = ['ut.'+str[3:len(str)-3] for str in test_file_strings]
#    print module_strings
    suites = [unittest.defaultTestLoader.loadTestsFromName(name) for name in module_strings]
    testSuite = unittest.TestSuite(suites)
    return testSuite

