import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest
import coverage


class CoverageResult(unittest._TextTestResult):

    def startTestRun(self):
        self._coverage = coverage.coverage(config_file='coverage.cfg')
        self._coverage.start()

    def stopTestRun(self):
        self._coverage.stop()
        self._coverage.report()

class CoverageRunner(unittest.TextTestRunner):
    resultclass = CoverageResult


if __name__ == "__main__":
    unittest.main(module='pystruct.tests', testRunner=CoverageRunner)
