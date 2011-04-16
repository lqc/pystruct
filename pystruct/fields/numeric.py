#!/usr/bin/env python
# -*- coding: utf-8
from __future__ import unicode_literals
import numbers

from pystruct.fields.base import CField
import pystruct.constraints as const

class NumericField(CField):

    KEYWORDS = dict(CField.KEYWORDS,
        ctype=lambda ctype_value: const.NumericBounds(ctype=ctype_value))

    def __init__(self, idx, default=0, **kwargs):
        CField.__init__(self, idx, default, **kwargs)
        self.add_constraint(const.ValueTypeConstraint(numbers.Real))
        self.__ctype = kwargs.get('ctype', 'int')

    FMT_STRING = {
        'int': 'i',
        'uint': 'I',
        'short': 'h',
        'ushort': 'H',
        'byte': 'b',
        'ubyte': 'B',
    }

    def _format_string(self, opts):
        return '<' + NumericField.FMT_STRING[self.__ctype]

    def _retrieve_value(self, opts):
         (v, offset) = CField._retrieve_value(self, opts)
         return (v[0], offset)

# some usefull shorthands
class IntField(NumericField):
    def __init__(self, idx, default=0, **kwargs):
        NumericField.__init__(self, idx, default, **dict(kwargs, ctype='int'))

class UIntField(NumericField):
    def __init__(self, idx, default=0, **kwargs):
        NumericField.__init__(self, idx, default, **dict(kwargs, ctype='uint'))

class ShortField(NumericField):
    def __init__(self, idx, default=0, **kwargs):
        NumericField.__init__(self, idx, default, **dict(kwargs, ctype='short'))

class UShortField(NumericField):
    def __init__(self, idx, default=0, **kwargs):
        NumericField.__init__(self, idx, default, **dict(kwargs, ctype='ushort'))

class ByteField(NumericField):
    def __init__(self, idx, default=0, **kwargs):
        NumericField.__init__(self, idx, default, **dict(kwargs, ctype='byte'))

class UByteField(NumericField):
    def __init__(self, idx, default=0, **kwargs):
        NumericField.__init__(self, idx, default, **dict(kwargs, ctype='ubyte'))
