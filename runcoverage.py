import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest
import coverage

_cov = coverage.coverage(config_file='coverage.cfg')

class CoverageResult(unittest._TextTestResult):

    def stopTestRun(self):
        _cov.stop()
        print "Coverage report:"
        _cov.report()
        _cov.html_report()


class CoverageRunner(unittest.TextTestRunner):
    resultclass = CoverageResult


if __name__ == "__main__":
    _cov.start()
    unittest.main(module='pystruct.tests', testRunner=CoverageRunner)
