# -*- coding: utf-8

__author__="lreqc"
__date__ ="$2009-07-19 08:05:30$"

import unittest
import test_numeric
import test_strings
import test_complex

test_cases = [
    test_numeric,
    test_strings,
    test_complex, 
]

if __name__ == "__main__":
    loader = unittest.TestLoader()

    for name in test_cases:
        suite = loader.loadTestsFromModule(name)
        unittest.TextTestRunner(verbosity=3).run(suite)
