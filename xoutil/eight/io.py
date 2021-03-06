# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# xoutil.eight.io
# ----------------------------------------------------------------------
# Copyright (c) 2015 Merchise and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 2015-07-13

'''Extensions to Python's ``io`` module.

You may use it as drop-in replacement of ``io``.  Although we don't document
all items here.  Refer to :mod:`io <io>` documentation.

In Python 2, buil-int :func:`open` is different from :func:`io.open`; in
Python 3 are the same function.

So, generated files with the built-in funtion in Python 2, can not be
processed using *abc* types, for example::

  f = open('test.rst')
  assert isinstance(f, io.IOBase)

will fail in Python 2 and not in Python 3.

Another incompatibilities:

- `file` type doesn't exists in Python 3.

- Python 2 instances created with `io.StringIO`:class`, or with
  `io.open`:func: using text mode, don't accept `str` values, so it will be
  better to use any of the standards classes (`StringIO.StringIO`:class:,
  `cStringIO.StringIO`:class: or `open`:func: built-in).

.. versionadded:: 1.7.0

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _absolute_import)

# TODO: This is the initial state for a in-progress module.

from io import *    # noqa

# Next three members are not included in ``__all__`` definition

from io import (DEFAULT_BUFFER_SIZE, IncrementalNewlineDecoder,    # noqa
                OpenWrapper)


def is_file_like(obj):
    '''Return if `obj` is a valid file type or not.'''
    from xoutil.eight import _py2, callable
    types = (file, IOBase) if _py2 else (IOBase, )
    if isinstance(obj, types):
        return True
    else:
        methods = ('close', 'write', 'read')
        return all(callable(getattr(obj, name, None)) for name in methods)
