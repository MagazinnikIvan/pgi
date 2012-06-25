# Copyright 2012 Christoph Reiter
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from ctypes import byref

from gitypes import GType, GTypeFlags, GTypeFundamentalFlags, GIRepository
from gitypes import guint, gobject
from util import import_attribute

class PGType(object):
    __slots__ = ["_type"]

    def __init__(self, type_):
        self._type = type_

    def __get_gtype_list(self, function):
        length = guint()
        array = getattr(self._type, function)(byref(length))
        # copy the gtypes and free the array so we don't leak
        items = [PGType(GType(v.value)) for v in array[:length.value]]
        gobject.free(array)
        return items

    @property
    def children(self):
        return self.__get_gtype_list("children")

    @property
    def interfaces(self):
        return self.__get_gtype_list("interfaces")

    @classmethod
    def from_name(self, name):
        type_ = GType.from_name(name)
        if type_.value == 0:
            raise RuntimeError("unknown type name")
        return PGType(type_)

    @property
    def fundamental(self):
        return PGType(self._type.fundamental())

    def has_value_table(self):
        return bool(self._type.value_table_peek())

    def is_a(self, type_):
        return self._type.is_a(type_._type)

    def is_abstract(self):
        return self._type.test_flags(GTypeFlags.ABSTRACT)

    def is_classed(self):
        return self._type.test_flags(GTypeFundamentalFlags.CLASSED)

    def is_deep_derivable(self):
        return self._type.test_flags(GTypeFundamentalFlags.DEEP_DERIVABLE)

    def is_derivable(self):
        return self._type.test_flags(GTypeFundamentalFlags.DERIVABLE)

    def is_instantiatable(self):
        return self._type.test_flags(GTypeFundamentalFlags.INSTANTIATABLE)

    def is_interface(self):
        return self.fundamental._type.value == (2 << 2)

    def is_value_abstract(self):
        return self._type.test_flags(GTypeFlags.VALUE_ABSTRACT)

    def is_value_type(self):
        return self._type.check_is_value_type()

    @property
    def parent(self):
        return PGType(self._type.parent())

    @property
    def name(self):
        return self._type.name() or "invalid"

    @property
    def depth(self):
        return self._type.depth()

    @property
    def pytype(self):
        if self._type.value == 0:
            return None

        repo = GIRepository.get_default()
        base_info = repo.find_by_gtype(self._type)
        if not base_info:
            return None
        name = base_info.get_name()
        namespace = base_info.get_namespace()
        base_info.unref()

        return import_attribute(namespace, name)

    def __eq__(self, other):
        return self._type.value == other._type.value

    def __neq__(self, other):
        return not self == other

    def __repr__(self):
        return "<GType %s (%d)>" % (self.name, self._type.value)