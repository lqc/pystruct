# -*- coding: utf-8

from __future__ import unicode_literals
import struct
from pystruct.constraints import OffsetConstraint, PrefixConstraint
from pystruct.common import UnpackException


class CField(object):
    KEYWORDS = {
        'offset': OffsetConstraint,
        'prefix': PrefixConstraint,
    }

    def __init__(self, idx, default=None, **kwargs):
        self.idx = idx
        self.default = default
        self.constraints = []
        self.ommit = []

        for (key, value) in kwargs.items():
            if key.endswith('__ommit'):
                key = key[:-7]
                self.ommit.append(key)
            constr = self.KEYWORDS[key](value)
            constr.keyword = key
            self.add_constraint(constr)

        self.nullable = bool(self.ommit)

    def add_constraint(self, constr):
        """
        Add a new constraint to the field.
        """
        index = 0
        length = len(self.constraints)
        while index < length \
          and self.constraints[index].priority <= constr.priority:
            index += 1
        self.constraints.insert(index, constr)

    def _before_unpack(self, opts):
        """Prepare the data for unpacking."""
        for c in self.constraints:
            if not c.before_unpack(opts):
                if c.keyword in self.ommit:
                    opts['__ommit'] = True
                    break
                raise UnpackException("Constraint {0} failed.".format(c), c)

    def before_pack(self, obj, offset, **opts):
        """
        Pack dry-run, so that the field can update dependencies.
        """
        value = getattr(obj, self.name)
        opts.update({'field': self,
                     'obj': obj,
                     'value': value,
                     'offset': offset})
        if (value == None) and self.nullable:
            return 0  # field is omitted
        for c in reversed(self.constraints):
            c.before_pack(opts)
        format = self._format_string(opts)
        return struct.calcsize(str(format))

    def pack(self, obj, offset, **opts):
        """
        Pack the field into a byte array.
        """
        value = getattr(obj, self.name)

        if (value == None) and self.nullable:
            return b''  # field is omitted

        opts.update({'field': self,
                     'obj': obj,
                     'value': value,
                     'offset': offset})
        for c in reversed(self.constraints):
            c.pack(opts)

        return struct.pack(self._format_string(opts), value)

    def unpack(self, obj, data, pos):
        """
        Unpack the given byte buffer into this field, starting at `pos`.
        """
        # before we unpack we need to check things like:
        #  * is the field at given offset ? (yes, this always comes first)
        #  * does the field prefix match ?
        #  * any other stuff the user wants to check
        opts = {'obj': obj, 'data': data, 'offset': pos}
        self._before_unpack(opts)

        if not opts.get('__ommit', False):
            return self._retrieve_value(opts)
        else:
            return (None, pos)

    def _format_string(self, opts):
        """The format string for the default retrieval method"""
        return ''

    def _retrieve_value(self, opts):
        fmt = self._format_string(opts)
        fmt_len = struct.calcsize(fmt)
        v = struct.unpack_from(fmt, opts['data'], opts['offset'])
        return (v, opts['offset'] + fmt_len)

    def get_value(self, obj, current_value):
        """
        Fetch value of this field from given object.
        """
        return current_value

    def set_value(self, obj, new_value):
        """
        Set value of this field in given object.
        """
        # enable clearing the field
        if (new_value == None) and self.nullable:
            return None

        # the new value is not yet set on the object
        opts = {'field': self, 'obj': obj, 'value': new_value}

        # trigger constraints
        for constr in self.constraints:
            constr.on_value_set(opts)

        return opts['value']

    def __unicode__(self):
        return u"<Field: {0.name}".format(self)
