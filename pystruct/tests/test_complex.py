#!/usr/bin/env python
# -*- coding: utf-8

from pystruct.utils import unittest
import struct

from pystruct import CStruct
from pystruct.fields.complex import ArrayField, StructField
from pystruct.fields.numeric import IntField, UIntField
from pystruct.fields.text import NullStringField


class ArrayFieldTest(unittest.TestCase):

    def setUp(self):
        self.svalue = [1, 1, 2, 3, 5, 8]
        self.slen = len(self.svalue)
        self.sdata = struct.pack("<" + str(self.slen) + "i", *self.svalue)
        # self.sdata_ext = struct.pack("<I", self.slen) + self.sdata

    def testArrayPack(self):
        class TestStruct(CStruct):
            array = ArrayField(0, length=self.slen, subfield=IntField(0))

        s = TestStruct(array=self.svalue)
        with self.assertRaisesRegexp(ValueError, "'ala ma kota' is not a valid value"):
            s.array[1] = 'ala ma kota'
        self.assertEqual(s.array, self.svalue)
        self.assertEqual(s.pack(), self.sdata)

    def testArrayUnpack(self):
        class TestStruct(CStruct):
            array = ArrayField(0, length=self.slen, subfield=IntField(0))
        s, offset = TestStruct.unpack(self.sdata)
        self.assertEqual(s.array, self.svalue)
        for i in range(0, self.slen):
            self.assertEqual(s.array[i], self.svalue[i])


class StructFieldTest(unittest.TestCase):

    def setUp(self):
        class InnerStruct(CStruct):
            one = IntField(0, default=13)
            two = IntField(1, default=42)

        class OuterStruct(CStruct):
            pad = NullStringField(0, default=b'KOT\0')
            inner = StructField(1, struct=InnerStruct)
            post = UIntField(2, default=0xbebafeca)

        self.OuterStruct = OuterStruct
        self.InnerStruct = InnerStruct

        self.inner = InnerStruct()
        self.inner_data = self.inner.pack()

    def testAccess(self):
        s = self.OuterStruct(inner=self.inner)
        self.assertEqual(s.pad, b'KOT\0')
        self.assertEqual(s.post, 0xbebafeca)
        self.assertEqual(s.inner, self.inner)

    def testPack(self):
        s = self.OuterStruct(inner=self.inner)
        data = s.pack()
        self.assertEqual(data[4:-4], self.inner_data)
