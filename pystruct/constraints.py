# -*- coding: utf-8

import abc

PRIO_OFFSET = 100
PRIO_PREFIX = 500
PRIO_TYPE = 600
PRIO_LENGTH = 700
PRIO_MAXLENGTH = 750
PRIO_NBOUNDS = 800

from pystruct.common import PackException


class Constraint(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, priority):
        self.priority = priority

    def __unicode__(self):
        return "<{0}: priority={1}>".format(type(self).__name__, self.priority)

    def before_unpack(self, opts):
        return True

    def pack(self, opts):
        return True

    def before_pack(self, opts):
        return True

    def on_value_set(self, opts):
        pass


class PrefixConstraint(Constraint):

    def __init__(self, param, priority=PRIO_PREFIX):
        super(PrefixConstraint, self).__init__(priority)

        if not isinstance(param, bytes):
            raise ValueError("Prefix constraints takes a byte array as an argument")
        self.prefix = param

    def match(self, data, pos):
        l = len(data)
        for char in self.prefix:
            if pos >= l:  # prefix exceeds the data
                return False

            if data[pos] != char:  # characters don't match
                return False
            pos += 1
        return True

    def before_unpack(self, opts):
        return self.match(opts['data'], opts['offset'])


class OffsetConstraint(Constraint):

    def __init__(self, param, priority=PRIO_OFFSET):
        super(OffsetConstraint, self).__init__(priority)

        if isinstance(param, str):
            self.before_upack = self.before_upack_field
        elif isinstance(param, int):
            self.before_upack = self.before_upack_number
        else:
            raise ValueError("Offset constraint must contain a number or a valid field name.")

        self.__offset = param

    def before_upack_number(self, options):
        if self.__offset != options['offset']:
            return False
        return True

    def before_upack_field(self, options):
        off_field = getattr(options['obj'], self.__offset)
        # TODO: this is a cyclic dependency... not good
        # if not isinstance(off_field, NumericField):
        #    raise ValueError("Field offset can only be attached \
        #            to a numeric field.")
        if getattr(options['obj'], self.__offset) != options['offset']:
            return False
        return True

    def before_pack(self, options):
        if isinstance(self.__offset, str):
            setattr(options['obj'], self.__offset, options['offset'])

    def pack(self, options):
        if isinstance(self.__offset, int) and (options['offset'] != self.__offset):
            raise PackException("Explicit offset of field %s was set, but position doesn't match" % \
                options['field'].name)


class ValueTypeConstraint(Constraint):

    def __init__(self, typeklass, priority=PRIO_TYPE):
        super(ValueTypeConstraint, self).__init__(priority)

        if not isinstance(typeklass, type):
            raise ValueError("This constraint must contain a type class.")
        self._klass = typeklass

    def on_value_set(self, opts):
        if not isinstance(opts['value'], self._klass):
            raise ValueError("Field {0} accepts only instances of {1} as value.".format(
                        opts['field'].name, self._klass.__name__))


class NumericBounds(Constraint):
    BOUND_FOR_CTYPE = {
        'int': (-(2 ** 31) + 1 , 2 ** 31),
        'uint': (0, 2 ** 32 - 1),
        'short': (-(2 ** 15) + 1, 2 ** 15),
        'ushort': (0, 2 ** 16 - 1),
        'byte': (-127, 128),
        'ubyte': (0, 255),
    }

    def __init__(self, lower_bound=None, upper_bound=None,
                        ctype=None, priority=PRIO_NBOUNDS):
        super(NumericBounds, self).__init__(priority)

        if ctype != None:
            self._lbound, self._ubound = self.BOUND_FOR_CTYPE[ctype]
        elif lower_bound == None or upper_bound == None:
            raise ValueError("You need to specify bounds or a ctype.")
        else:
            self._lbound = lower_bound
            self._ubound = upper_bound

    def on_value_set(self, opts):
        if not (self._lbound <= opts['value'] <= self._ubound):
            raise ValueError("Field %s - value %s out of bounds."\
                % (opts['field'].name, opts['value']))


class LengthConstraint(Constraint):
    def __init__(self, length, padding_func,
                 priority=PRIO_LENGTH, opt_name='length'):
        super(LengthConstraint, self).__init__(priority)

        if isinstance(length, property):
            self.before_unpack = self.before_unpack_prop
        elif isinstance(length, basestring):
            self.before_unpack = self.before_unpack_field
        elif isinstance(length, int):
            self.before_unpack = self.before_unpack_number
        else:
            raise ValueError("Length constraint must contain a number or a field name.")

        self._opt_name = opt_name
        self.__length = length
        self.__padding_func = padding_func

    def on_value_set(self, opts):
        L = len(opts['value'])
        if isinstance(self.__length, property):
            return self.__length.__set__(opts, L)
        if isinstance(self.__length, basestring):
            return setattr(opts['obj'], self.__length, L)
        if self.__length < 0:
            return # do nothing

        if L > self.__length:
            raise ValueError("Field %s has limited length of %d." % (opts['field'].name, self.__length))

        if self.__padding_func:
            opts['padding'] = (self.__length - L)
            self.__padding_func(opts)

    def before_pack(self, opts):
        # the value is about to be packed
        # nothing to do here, 'cause we ensure proper length in the trigger
        opts[self._opt_name] = len(opts['value'])

    def pack(self, opts):
        # value is being packed - add our property
        opts[self._opt_name] = len(opts['value'])

    def before_unpack_prop(self, opts):
        opts[self._opt_name] = self.__length.__get__(opts)
        return True

    def before_unpack_number(self, opts):
        opts[self._opt_name] = self.__length
        return True

    def before_unpack_field(self, opts):
        opts[self._opt_name] = getattr(opts['obj'], self.__length)
        return True


class MaxLengthConstraint(LengthConstraint):
    def __init__(self, length, priority=PRIO_MAXLENGTH):
        LengthConstraint.__init__(self, length, None, priority, opt_name='max_length')
