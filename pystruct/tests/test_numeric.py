#!/usr/bin/env python
# -*- coding: utf-8

import struct
from pystruct.utils import unittest

from pystruct import CStruct, UnpackException
from pystruct.constraints import PrefixConstraint
from pystruct.fields.numeric import (NumericField,
                    ByteField, UByteField,
                    ShortField, UShortField,
                    IntField, UIntField)
from pystruct.common import PackException


class NumericFieldTest(unittest.TestCase):

    def setUp(self):
        self.ivalue = 42
        self.idata = struct.pack('<i', self.ivalue)

    def test0Pack(self):
        class TestStruct(CStruct):
            intField = NumericField(0, ctype='int')
        s = TestStruct(intField=self.ivalue)
        self.assertEqual(s.intField, self.ivalue)
        self.assertEqual(s.pack(), self.idata)

    def test0Unpack(self):
        class TestStruct(CStruct):
            intField = NumericField(0, ctype='int')
        s, offset = TestStruct.unpack(self.idata)
        self.assertEqual(s.intField, self.ivalue)

    def testPrefixMatch(self):
        class TestStruct(CStruct):
            intField = NumericField(0, ctype='int', prefix=self.idata[0:2])
        v, offset = TestStruct.unpack(self.idata)
        self.assertEqual(v.intField, self.ivalue)

    def testPrefixMismatch(self):
        class TestStruct(CStruct):
            intField = NumericField(0, ctype='int', prefix=b'abc')
        with self.assertRaises(UnpackException) as cm:
            TestStruct.unpack(self.idata)
        self.assertIsInstance(cm.exception.args[1], PrefixConstraint)

    def testPrefixTooLong(self):
        class TestStruct(CStruct):
            intField = NumericField(0, ctype='int', prefix=(self.idata + b'\x00'))
        with self.assertRaises(UnpackException) as cm:
            TestStruct.unpack(self.idata)
        self.assertIsInstance(cm.exception.args[1], PrefixConstraint)

    def testPrefixEmpty(self):
        class TestStruct(CStruct):
            intField = NumericField(0, ctype='int', prefix=b'')
        v, offset = TestStruct.unpack(self.idata)
        self.assertEqual(v.intField, self.ivalue)

    def testByteAndShort(self):
        class TestStruct(CStruct):
            byteField = ByteField(0)
            shortField = ShortField(1)
            intField = IntField(2)

        s = TestStruct(byteField=42, shortField= -30000, intField=4000000)
        s2, offset = TestStruct.unpack(s.pack())
        self.assertEqual(s2.intField, s.intField)
        self.assertEqual(s2.byteField, s.byteField)
        self.assertEqual(s2.shortField, s.shortField)

    def testOffset(self):
        class TestStruct(CStruct):
            f1 = IntField(0, offset=0)
            f2 = IntField(1, offset=4)

        # some random data
        data = b''.join([chr(x) for x in range(64) ])
        data = data[:16] + self.idata + data[20:]

        v, offset = TestStruct.unpack(data, 16)
        self.assertEqual(v.f1, self.ivalue)

    def testOmmitUnpack(self):
        class TestStruct(CStruct):
            f1 = UIntField(0, prefix__ommit=b'\x00')
            f2 = UIntField(1)
            f3 = IntField(2)

        d = struct.pack("<Ii", 0xcafebabe, 2)
        v, offset = TestStruct.unpack(d)
        self.assertEqual(offset, 8)
        self.assertEqual(v.f1, None)
        self.assertEqual(v.f2, 0xcafebabe)
        self.assertEqual(v.f3, 2)

    def testOmmitPack(self):
        class TestStruct(CStruct):
            f1 = UIntField(0, prefix__ommit=b'\x00')
            f2 = UIntField(1)
            f3 = IntField(2)

        s = TestStruct(f1=None, f2=2, f3=3)
        self.assertEqual(s.f2, 2)
        self.assertEqual(s.f3, 3)
        self.assertEqual(s.pack(), b'\x02\x00\x00\x00\x03\x00\x00\x00')

    def testOmmitPackWithOffset(self):
        class TestStruct(CStruct):
            offset_field = UIntField(0)
            not_important = IntField(1, prefix__ommit=b'\x02')
            data = IntField(2, offset='offset_field')

        s = TestStruct(not_important=None, data=0xcafe)
        s.pack()
        self.assertEqual(s.offset_field, 4)

    def testBoundViolation(self):
        class A(CStruct):
            f = ByteField(0)
        class B(CStruct):
            f = ShortField(1)
        class C(CStruct):
            f = UIntField(2)

        with self.assertRaisesRegexp(ValueError, "out of bounds"):
            A(f=5442)
        with self.assertRaisesRegexp(ValueError, "out of bounds"):
            B(f=5645442)
        with self.assertRaisesRegexp(ValueError, "out of bounds"):
            C(f= -1)
