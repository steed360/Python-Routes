
import unittest
import ut.all_tests
import logging

#logging.basicConfig(filename='test.log',level=logging.DEBUG)
logging.basicConfig(filename='test.log',level=logging.WARNING)

logging.debug('This message should go to the log file')
logging.info('So should this')
logging.warning('And this, too')


testSuite = ut.all_tests.create_test_suite()
text_runner = unittest.TextTestRunner().run(testSuite)

