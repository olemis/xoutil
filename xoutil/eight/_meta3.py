#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.eight._meta3
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise and Contributors
# Copyright (c) 2013, 2014 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 2013-04-29

'''Implements the meta() function using the Py3k syntax.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_imports)

from . import _py3
assert _py3, 'This module should be loaded in Py3k only'


def metaclass(meta, **kwargs):
    class base:
        pass

    if isinstance(meta, type) and issubclass(meta, type) and meta is not type:
        metabase = meta.__base__
    else:
        metabase = type

    class inner_meta(metabase):
        @classmethod
        def __prepare__(cls, name, bases, **kwargs):
            prepare = getattr(meta, '__prepare__', None)
            if prepare:
                return prepare(name, bases, **kwargs)
            else:
                return dict()

        def __new__(cls, name, bases, attrs, **kw):
            if name != '__inner__':
                bases = tuple(b for b in bases if not issubclass(b, base))
                if not bases:
                    bases = (object,)
                return meta(name, bases, attrs)
            else:
                return type.__new__(cls, name, bases, attrs)

        def __init__(self, name, bases, attrs, **kw):
            pass

    from ._types import new_class
    kwds = dict(kwargs, metaclass=inner_meta)
    return new_class('__inner__', (base, ), kwds=kwds)
