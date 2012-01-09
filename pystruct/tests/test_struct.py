from pystruct.utils import unittest
from pystruct import CStruct, CField

class Dummy(CStruct):
    field = CField(0)

class StructTest(unittest.TestCase):

    @unittest.expectedFailure
    def test_missing_argument(self):
        self.assertRaises(ValueError, Dummy)

    def test_unresolved_argument(self):
        self.assertRaises(ValueError, Dummy, field="F", extra="E")
