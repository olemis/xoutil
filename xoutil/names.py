#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.names
#----------------------------------------------------------------------
# Copyright (c) 2013 Merchise Autrement
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License (GPL) as published by the
# Free Software Foundation;  either version 2  of  the  License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.
#
# Created on 15 avr. 2013

'''A protocol to obtain or manage object names.'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_import)

__docstring_format__ = 'rst'
__author__ = 'med'


def nameof(target, depth=1, inner=False, typed=False):
    '''Gets the name of an object.

    The name of an object is normally the variable name in the calling stack::

        >>> from collections import OrderedDict as sorted_dict
        >>> nameof(sorted_dict)
        'sorted_dict'

    If the `inner` flag is true, then the name is found by introspection
    first::

        >>> nameof(sorted_dict, inner=True)
        'OrderedDict'

    If the `typed` flag is true, is name of the type unless `target` is already
    a type (all objects with "__name__" attribute are considered valid types)::

        >>> sd = sorted_dict(x=1, y=2)
        >>> nameof(sd)
        'sd'
        >>> nameof(sd, typed=True)
        'sorted_dict'
        >>> nameof(sd, inner=True, typed=True)
        'OrderedDict'

    If `target` is an instance of a simple type (strings or numbers) and
    `inner` is true, then the name is the standard representation of `target`::

        >>> s = 'foobar'
        >>> nameof(s)
        's'
        >>> nameof(s, inner=True)
        'foobar'
        >>> i = 1
        >>> nameof(i)
        'i'
        >>> nameof(i, inner=True)
        '1'
        >>> nameof(i, typed=True)
        'int'

    If `target` isn't an instance of a simple type (strings or numbers) and
    `inner` is true, then the id of the object is used::

        >>> str(id(sd)) in nameof(sd, inner=True)
        True

    - :param:`depth`: level of stack frames to look up, if needed.

    '''
    from numbers import Number
    from xoutil.compat import str_base
    TYPED_NAME = '__name__'
    if typed and not hasattr(target, TYPED_NAME):
        target = type(target)
    if inner:
        res = getattr(target, TYPED_NAME, False)
        if res:
            return str(res)
        elif isinstance(target, (str_base, Number)):
            return str(target)
        else:
            return str('id(%s)' % id(target))
    else:
        import sys
        from xoutil.collections import dict_key_for_value as search
        sf = sys._getframe(depth)
        try:
            res = False
            i, LIMIT = 0, 5   # Limit number of stack to recurse
            while not res and sf and (i < LIMIT):
                l = sf.f_locals
                key = search(l, target)
                if not key:
                    g = sf.f_globals
                    if l is not g:
                        key = search(g, target)
                if key:
                    res = key
                else:
                    sf = sf.f_back
                    i =+ 1
        finally:
            del sf
        if res:
            return str(res)
        else:
            return nameof(target, depth=depth+1, inner=True)


class namelist(list):
    '''Similar to list, but only intended for storing object names.

    Constructors:
        * namelist() -> new empty list
        * namelist(collection) -> new list initialized from collection's items
        * namelist(item, ...) -> new list initialized from severals items

    Instances can be used as decorator to store names of module items
    (functions or classes)::
        >>> __all__ = namelist()
        >>> @__all__
        ... def foobar(*args, **kwargs):
        ...     'Automatically added to this module "__all__" names.'

    '''
    def __init__(self, *args):
        if len(args) == 1:
            from types import GeneratorType as gtype
            if isinstance(args[0], (tuple, list, set, frozenset, gtype)):
                args = args[0]
        super(namelist, self).__init__((nameof(arg, depth=2) for arg in args))

    def __add__(self, other):
        other = [nameof(item, depth=2) for item in other]
        return super(namelist, self).__add__(other)
    __iadd__ = __add__

    def __contains__(self, target):
        return super(namelist, self).__contains__(nameof(target, depth=2))

    def append(self, value):
        '''l.append(value) -- append a name object to end'''
        super(namelist, self).append(nameof(value, depth=2))
        return value    # What allow to use its instances as a decorator
    __call__ = append

    def extend(self, items):
        '''l.extend(items) -- extend list by appending items from the iterable
        '''
        items = (nameof(item, depth=2) for item in items)
        return super(namelist, self).extend(items)

    def index(self, value, *args):
        '''l.index(value, [start, [stop]]) -> int -- return first index of name

        Raises ValueError if the name is not present.

        '''
        return super(namelist, self).index(nameof(value, depth=2), *args)

    def insert(self, index, value):
        '''l.insert(index, value) -- insert object before index
        '''
        return super(namelist, self).insert(index, nameof(value, depth=2))

    def remove(self, value):
        '''l.remove(value) -- remove first occurrence of value

        Raises ValueError if the value is not present.

        '''
        return list.remove(self, nameof(value, depth=2))


__all__ = namelist(nameof, namelist)
