#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.modules.modulet
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise Autrement
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# Created on 2015-02-17

'''A modulet automatically isolate imports done in non-root greenlets.

.. note:: Only works if `greenlets` are installed.

.. note:: Modules not isolated.

   Neither xoutil's packages and modules are isolated by greenlet.  Also
   standard library's are always


Usage::

   # Global import: shared by all greenlets and threads
   from some.module import something


   def greenlet_program():
       # Greenlet isolated import.  If this code is run in different greenlets
       # at different times, you may have updates the `some.module` module,
       # the greenlets will use different code.
       from some.module import something_else

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

import imp
import os
import sys
import sysconfig
import pdb
import logging

from xoutil.string import cut_any_suffix, cut_prefix
from xoutil import logger, Unset

from six import exec_

try:
    import greenlet
except ImportError:
    def _bootstrap(ignores=None, debug=False):
        if debug:
            debug.error('Greenlets are not available. I cannot work without '
                        'them.')
else:
    # TODO: PEP 451 find_spec, etc...
    class _ModuletManager(object):
        def __init__(self, ignores=None, debug=False):
            self.ignores = _ignores = self._get_stdlib()
            _ignores.extend([
                # TODO: How to include these?
                '_multiprocessing',
                '_hashlib',
                '_strptime',

                # Not stdlib but also non-isolable because of core-features
                'greenlet',
                'gevent',
                'xoutil',
            ])
            _ignores.extend(ignores or [])
            self.debug = debug

        @staticmethod
        def _get_stdlib():
            names = {'stdlib', 'platstdlib'} & set(sysconfig.get_path_names())
            dirs = set(sysconfig.get_path(name) for name in names)
            result = set()
            for dirname in dirs:
                for name in os.listdir(dirname):
                    mod = cut_any_suffix(name, '.py', '.pyo', '.pyc')
                    if '.' not in mod:
                        result.add(mod)
            return list(result)

        def _get_ns(self):
            gl = greenlet.getcurrent()
            try:
                if gl.parent:
                    while gl.parent:
                        # Grab a direct child of the root greenlet to build
                        # the ns.  All greenlets from the same branch will
                        # share.
                        ns = str(gl) + '.'
                        gl = gl.parent
                else:
                    # The same module can be imported at a global-level.
                    # We'll share all greenlet roots modules, so different
                    # threads share the same code.  But since `import x` will
                    # cache it and won't call us again if imported in a
                    # greenlet we change the name.  This, of course, only
                    # works for modules imported after the bootstrapping of
                    # modulet.
                    ns = '<root>.'
                return ns
            finally:
                del gl

        def _get_real_modulename(self, fn):
            ns = self._get_ns()
            return cut_prefix(fn, ns)

        def _get_pkg_mod(self, fn):
            pkg, _, name = fn.rpartition('.')
            return pkg or None, name

        def find_module(self, fn, path=None):
            fn = self._get_real_modulename(fn)
            if imp.is_builtin(fn) or imp.is_frozen(fn):
                return None
            ok = lambda i: fn != i and not fn.startswith('%s.' % i)
            isolable = all(ok(ignore) for ignore in self.ignores)
            if isolable:
                try:
                    if path:
                        name = self._get_pkg_mod(fn)[-1]
                    else:
                        name = fn
                    self._get_spec(name, path=path[0] if path else None)
                    # TODO: check the desc for C_EXTENSIONS, etc...
                except ImportError:
                    # If the _get_spec fails it means a sub-module is
                    # importing another one implicitly relatively and its
                    # probably an absolute import.
                    return None
                else:
                    return self
            else:
                return None

        def load_module(self, fn):
            ns = self._get_ns()
            fn = self._get_real_modulename(fn)
            target_module_name = '%s%s' % (ns, fn)
            if self.debug:
                logger.debug(
                    'Isolating %r as %r', fn, target_module_name
                )
            res = sys.modules.setdefault(
                target_module_name, imp.new_module(target_module_name)
            )
            if getattr(res, '__loader__', Unset) is self:
                # XXX: Circularity?  Don't reevaluate the code.
                return res
            res.__loader__ = self
            try:
                name, _, origin, paths, (fp, desc) = self._get_spec(fn)[:5]
                if desc[-1] == imp.PKG_DIRECTORY:
                    res.__path__ = [origin]
                    fp, origin, desc = imp.find_module('__init__', paths)
                    res.__package__ = target_module_name
                else:
                    res.__package__ = self._get_pkg_mod(target_module_name)[0]
                res.__file__ = origin
                try:
                    if desc[-1] == imp.PY_SOURCE:
                        exec_(fp, res.__dict__)
                    else:
                        raise ImportError('Unloadable %s' % fn)
                finally:
                    fp.close()
            except:
                if self.debug:
                    logger.exception('Exception while loading %s', fn)
                res = None
                del sys.modules[target_module_name]
            else:
                delattr(res, '__loader__')
                return res

        def _get_spec(self, fullname, path=None):
            loader = self
            pkg, _, name = fullname.rpartition('.')
            parts = pkg.split('.') if pkg else []
            fp = None
            while not fp and parts:
                mod = parts.pop(0)
                fp, path, desc = imp.find_module(
                    mod,
                    [path] if path else None
                )
                if fp:
                    fp.close()
            fp, path, desc = imp.find_module(name, [path] if path else None)
            return (
                name,
                loader,
                path,
                [path] if not fp else None,
                (fp, desc),
                None,
                pkg or None,
                False
            )

    def _bootstrap(ignores=None, debug=False):
        manager = next((hook
                        for hook in sys.meta_path
                        if isinstance(hook, _ModuletManager)),
                       None)
        if not manager:
            sys.meta_path.insert(
                0,
                _ModuletManager(ignores=ignores, debug=debug)
            )
        elif ignores:
            manager.ignores.extend(ignores)
        if debug:
            logger.addHandler(logging.StreamHandler())
            logger.setLevel(logging.DEBUG)
