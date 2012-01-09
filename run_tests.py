import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest
import xmlrunner


if __name__ == "__main__":
    unittest.main(module='pystruct.tests', testRunner=xmlrunner.XMLTestRunner(output='_unittests'))
