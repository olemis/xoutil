#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.eight._meta2
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise and Contributors
# Copyright (c) 2013, 2014 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 2013-04-29

'''Implements the metaclass() function using the Py3k syntax.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_imports)

from . import _py3
assert not _py3, 'This module should not be loaded in Py3k'


METACLASS_ATTR = '__metaclass__'


def metaclass(meta, **kwargs):
    prepare = getattr(meta, '__prepare__', None)
    if prepare:
        import warnings
        warnings.warn('Python 2.7 does not have the __prepare__ stuff and '
                      'the metaclass "%s" seems to needs it.' % meta,
                      stacklevel=2)

    class base(object):
        pass

    if isinstance(meta, type) and issubclass(meta, type) and meta is not type:
        metabase = meta.__base__
    else:
        metabase = type

    class inner_meta(metabase):
        def __new__(cls, name, bases, attrs):
            from copy import copy
            if name != '__inner__':
                bases = tuple(b for b in bases if not issubclass(b, base))
                if not bases:
                    bases = (object,)
                from ._types import prepare_class
                kwds = dict(kwargs, metaclass=meta)
                basemeta, _ns, kwds = prepare_class(name, bases, kwds=kwds)
                ns = copy(_ns)
                update = getattr(ns, 'update', None)
                if update:
                    update(attrs)
                else:
                    for attr, val in attrs.items():
                        ns[attr] = val
                if METACLASS_ATTR not in attrs:
                    attrs[METACLASS_ATTR] = meta
                return basemeta(name, bases, ns)
            else:
                return type.__new__(cls, name, bases, attrs)

    from ._types import new_class
    kwds = dict(kwargs, metaclass=inner_meta)

    def exec_body(ns):
        return ns

    return new_class('__inner__', (base, ), kwds=kwds, exec_body=exec_body)
