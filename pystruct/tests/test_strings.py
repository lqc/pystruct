#!/usr/bin/env python
# -*- coding: utf-8
from __future__ import unicode_literals

from pystruct.utils import unittest
import struct

from pystruct import CStruct
from pystruct.fields.text import StringField, NullStringField
from pystruct.fields.numeric import IntField

class StringFieldTest(unittest.TestCase):

    def setUp(self):
        self.svalue = b"Hello World!"
        self.slen = len(self.svalue)
        self.sdata = struct.pack(bytes("<{0}s".format(self.slen)), self.svalue)
        self.sdata_ext = struct.pack(b"<I", self.slen) + self.sdata

    def testNegativeLength(self):
        class TestStruct(CStruct):
            text = StringField(0, length= -1)

        s, offset = TestStruct.unpack(self.sdata)
        self.assertEqual(s.text, self.svalue)
        self.assertEqual(offset, self.slen)

    def test0PackWithPadding(self):
        class TestStruct(CStruct):
            text = StringField(0, length=32)

        s = TestStruct(text=self.svalue)
        self.assertTrue(self.slen < 32)
        self.assertEqual(s.text, self.svalue + (32 - self.slen) * b'\x00')
        self.assertEqual(s.pack(), s.text)

    def test0Pack(self):
        class TestStruct(CStruct):
            text = StringField(0, length=self.slen)

        s = TestStruct(text=self.svalue)
        self.assertEqual(s.text, self.svalue)
        self.assertEqual(s.pack(), self.sdata)

    def test0Unpack(self):
        class TestStruct(CStruct):
            text = StringField(0, length=self.slen)

        s, offset = TestStruct.unpack(self.sdata)
        self.assertEqual(offset, self.slen)
        self.assertEqual(s.text, self.svalue)

    def testLengthAsField(self):
        class TestStruct(CStruct):
            tlen = IntField(0)
            text = StringField(1, length='tlen')

        s = TestStruct(text=self.svalue)
        self.assertEqual(s.text, self.svalue)
        self.assertEqual(s.tlen, self.slen)
        self.assertEqual(s.pack(), self.sdata_ext)

        s, offset = TestStruct.unpack(self.sdata_ext)
        self.assertEqual(s.text, self.svalue)
        self.assertEqual(s.tlen, self.slen)

    def test0PackNullString(self):
        class TestStruct(CStruct):
            text = NullStringField(0)
            checksum = IntField(1, default=0x7afebabe)

        s = TestStruct(text=b'Ala ma kota\0')
        self.assertEqual(s.pack(), b'Ala ma kota\0' + struct.pack(b"<i", 0x7afebabe))
