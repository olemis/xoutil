import os
import shutil
import sys
import tempfile
import greenlet
import logging

from xoutil.modules.modulet import _bootstrap as _b
_b(debug=True)

from xoutil import logger
logger.addHandler(logging.StreamHandler())


MODULE = '''
def get_magic():
    return {magic}
'''


def write_module(where, magic):
    code = MODULE.format(magic=magic)
    with open(os.path.join(where, 'magic_module.py'), 'w') as fp:
        fp.write(code)


def prog(magic):
    from magic_module import get_magic
    root.switch()
    res = get_magic()
    assert res == magic, "Expected %d but got %d." % (magic, res)
    print('Passed. I have the right magic number %d' % magic)


def rootprog(n):
    where = tempfile.mkdtemp()
    print('Beginning with %d in %s' % (n, where))
    try:
        sys.path.insert(0, where)
        greenies = [greenlet.greenlet(run=prog) for _ in range(n)]
        for i, g in enumerate(greenies):
            magic = 1000 + i
            # Update the module before each switch to a greenlet.
            write_module(where, magic)
            g.switch(magic)
        greenies = [g for g in greenies if not g.dead]
        while greenies:
            try:
                g.switch()
            except AssertionError:
                logger.exception('Wrong magic number')
            greenies = [g for g in greenies if not g.dead]
    finally:
        shutil.rmtree(where)

root = greenlet.getcurrent()
rootprog(3)
