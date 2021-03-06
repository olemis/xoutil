#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.tests.test_values
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-07-19


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_import)


import unittest


class TestValues(unittest.TestCase):
    def test_basic_coercers(self):
        from xoutil.eight import string_types
        from xoutil.values import (identity_coerce, void_coerce, coercer,
                                   coercer_name, check, valid, int_coerce,
                                   float_coerce, create_int_range_coerce,
                                   istype, typecast, iterable, mapping,
                                   create_unique_member_coerce, Invalid)
        d = {'1': 2, 3.0: '4', 5.0+0j: 7.3+0j, 1: '2'}
        s = {1, '2', 3.0, '1'}
        l = [1, '2', 3.0, '1', 'x10']
        mc = mapping(int_coerce, float_coerce)
        uint_coerce = create_unique_member_coerce(int_coerce, d)
        mcu = mapping(uint_coerce, float_coerce)
        ic = iterable(int_coerce)
        age_coerce = create_int_range_coerce(0, 100)
        text_coerce = coercer(string_types)
        isnumber = istype((int, float, complex))
        numbercast = typecast((int, float, complex))
        self.assertEqual(all(isinstance(c, coercer)
                             for c in (mc, mcu, uint_coerce, ic,
                                       age_coerce, text_coerce,
                                       identity_coerce, void_coerce,
                                       int_coerce, float_coerce)), True)
        self.assertEqual(mc(dict(d)), {1: 2.0, 3: 4.0, 5: 7.3})
        self.assertIs(mcu(d), Invalid)
        self.assertEqual(mcu.scope, ({'1': 2}, uint_coerce))
        self.assertEqual(ic(s), {1, 2, 3})
        self.assertIs(ic(l), Invalid)
        self.assertIs(ic.scope, l[-1])
        self.assertEqual(l, [1, 2, 3, 1, 'x10'])
        self.assertIs(age_coerce(80), 80)
        self.assertFalse(valid(age_coerce(120)))
        self.assertIs(check(age_coerce, 80), 80)
        with self.assertRaises(TypeError):
            check(age_coerce, 120)
        self.assertIs(isnumber(5), 5)
        self.assertIs(isnumber(5.1), 5.1)
        with self.assertRaises(TypeError):
            check(isnumber, '5.1')
        self.assertIs(numbercast(5), 5)
        self.assertIs(numbercast(5.1), 5.1)
        self.assertEqual(numbercast('5.1'), 5.1)
        self.assertIs(numbercast.scope, float)

    def test_compound_coercers(self):
        from xoutil.eight import string_types
        from xoutil.values import (coercer, compose, some, combo, iterable,
                                   check, valid, typecast, int_coerce,
                                   float_coerce, identifier_coerce, Invalid)
        isstr = coercer(string_types)
        strcast = typecast(string_types)
        toint = compose(isstr, int_coerce)
        isint = some(isstr, int_coerce)
        hyphenjoin = coercer(lambda arg: '-'.join(arg))
        intjoin = compose(iterable(strcast), hyphenjoin)
        cb = combo(strcast, int_coerce, float_coerce)
        self.assertEqual(toint('10'), 10)
        self.assertIs(toint(10), Invalid)
        self.assertEqual(toint.scope, (10, isstr))
        self.assertEqual(isint('10'), '10')
        self.assertEqual(isint.scope, isstr)
        self.assertEqual(isint(10), 10)
        self.assertEqual(isint.scope, int_coerce)
        self.assertEqual(intjoin(2*i + 1 for i in range(5)), '1-3-5-7-9')
        self.assertEqual(cb([1, '2.0', 3, 4]), ['1', 2, 3.0])
