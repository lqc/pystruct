# -*- coding: utf-8
from pystruct.fields.base import CField
from pystruct.utils import ItemWrapper


class StructMetaclass(type):

    def __new__(cls, name, bases, cdict):
        fields = []
        ndict = {}

        for (field_name, field_value) in cdict.items():
            if isinstance(field_value, CField):
                field_value.name = field_name
                fields.append(field_value)
                ndict[field_name] = property(cls.getter_for(field_value),
                                             cls.setter_for(field_value))
            else:
                ndict[field_name] = field_value

        klass = type.__new__(cls, str(name), bases, ndict)
        fields.sort(key=lambda item: item.idx)

        order = getattr(klass, '_field_order', [])
        order = order + fields
        setattr(klass, '_field_order', order)
        return klass

    @staticmethod
    def getter_for(field):
        def getter(self):
            return field.get_value(self, getattr(self, '_' + field.name))
        return getter

    @staticmethod
    def setter_for(field):
        def setter(self, v):
            return setattr(self, '_' + field.name, field.set_value(self, v))
        return setter


CStructBase = StructMetaclass('CStructBase', (object,), {})


class CStruct(CStructBase):

    def __init__(self, **kwargs):
        for field in self._field_order:
            setattr(self, field.name, kwargs.pop(field.name, field.default))
        if kwargs:
            raise ValueError("Unresolved fields: {0!r}".format(kwargs.keys()))

    def _before_pack(self, offset=0):
        for field in self._field_order:
            offset += field.before_pack(self, offset)
        return offset

    def _pack(self, off=0):
        s = b''
        for field in self._field_order:
            data = field.pack(self, off)
            off += len(data)
            s += data
        return s

    def pack(self, offset=0):
        self._before_pack(offset)
        return self._pack(offset)

    @classmethod
    def unpack(cls, data, offset=0):
        dict = {}
        dp = ItemWrapper(dict)

        for field in cls._field_order:
            value, next_offset = field.unpack(dp, data, offset)
            dict[field.name] = value
            offset = next_offset

        instance = cls(**dict)
        return instance, offset

    def __field_value(self, field, default=None):
        return field.get_value(self, getattr(self, '_' + field.name, default))

    def __unicode__(self):
        buf = "CStruct("
        buf += ','.join("%s = %r" % (field.name, self.__field_value(field)) \
            for field in self._field_order)
        buf += ")"
        return buf
