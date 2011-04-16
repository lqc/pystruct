# -*- coding: utf-8
import sys

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest


class ItemWrapper(object):
    """
    Wraps the given object (usually a `dict` or a `list`) with
    accessor methods that turn attribute calls to index calls.
    Also provides a handy way, to attach set/get triggers.
    """
    def __init__(self, obj):
        self._object = obj

    def __getattribute__(self, name):
        # play nice with names starting with '_'
        if name.startswith('_'):
            try:
                return object.__getattribute__(self, name)
            except AttributeError:
                return object.__getattribute__(self._object, name[1:])

        return self._get_action(self, name, self._object[name])

    def __setattr__(self, name, value):
        # play nice :)
        if name.startswith('_'):
            return object.__setattr__(self, name, value)

        self._object[name] = self._set_action(self, name, value)

    def __getitem__(self, name):
        return self._get_action(self, name, self._object[name])

    def __setitem__(self, name, value):
        self._object[name] = self._set_action(self, name, value)

    def __len__(self):
        return self._object.__len__()

    def _set_action(self, me, name, value):
        return value

    def _get_action(self, me, name, value):
        return value

    def __str__(self):
        return str(self._object)

    def __eq__(self, other):
        return self._object.__eq__(other)


class ListItemWrapper(ItemWrapper):

    def __getattribute__(self, name):
        try:
            key = int(name)
            return self._get_action(self, name, self._object[key])
        except ValueError:
            return ItemWrapper.__getattribute__(self, name)

    def __setattr__(self, name, value):
        try:
            key = int(name)
            self._object[key] = self._set_action(self, name, value)
        except ValueError:
            return ItemWrapper.__setattr__(self, name, value)
