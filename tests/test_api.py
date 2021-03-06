#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.tests.test_api
#----------------------------------------------------------------------
# Copyright (c) 2015 Merchise and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 2015-10-23

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_imports)


from xoutil.eight.abc import ABC
from xoutil import api


def test_api_errors():
    class MyError(ABC, Exception):
        pass

    d, x = {}, 0

    try:
        x = d['x']
        assert False, 'Never executed.'
    except MyError:
        assert False, 'Never executed.'
    except Exception:
        x = 1
        assert True, 'Executed, but OK.'

    assert x == 1

    @api.error
    class MyNewError(ABC, Exception):
        pass

    assert MyNewError.adopt(KeyError) == KeyError
    try:
        x = d['x']
        assert False, 'Never executed.'
    except api.error.MyNewError:
        x = 2
        assert True, 'Executed, but OK.'
    except Exception:
        assert False, 'Never executed.'

    assert x == 2
