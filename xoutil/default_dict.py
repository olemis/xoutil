#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.default_dict
#----------------------------------------------------------------------
# Copyright (c) 2012 Medardo Rodríguez
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
# Created on Jan 9, 2012

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode)

from xoutil import collections
from xoutil.deprecation import inject_deprecated

__docstring_format__ = 'rst'
__author__ = 'manu'


__all__ = (b'defaultdict',)
inject_deprecated(__all__, collections)
