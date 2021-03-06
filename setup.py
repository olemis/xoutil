#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import os
import sys
from setuptools import setup, find_packages

try:
    execfile = execfile
except NameError:
    def execfile(filename):
        'To run in Python 3'
        import builtins
        exec_ = getattr(builtins, 'exec')
        with open(filename, "r") as f:
            code = compile(f.read(), filename, 'exec')
            return exec_(code, globals())


# Import the version from the release module
project_name = 'xoutil'
_current_dir = os.path.dirname(os.path.abspath(__file__))
release = os.path.join(_current_dir, project_name, 'release.py')
execfile(release)
version = VERSION  # noqa

if RELEASE_TAG != '':   # noqa
    dev_classifier = 'Development Status :: 4 - Beta'
else:
    dev_classifier = 'Development Status :: 5 - Production/Stable'

from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

setup(
    name=project_name,
    version=version,
    description=("Collection of usefull algorithms and other very "
                 "disparate stuff"),
    long_description=open(
        os.path.join(_current_dir, 'docs', 'readme.txt')).read(),
    classifiers=[
        # Get from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        dev_classifier,
        'Intended Audience :: Developers',
        ('License :: OSI Approved :: '
         'GNU General Public License v3 or later (GPLv3+)'),
        'Operating System :: POSIX :: Linux',  # This is where we are
                                               # testing. Don't promise
                                               # anything else.
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='',
    author='Merchise',
    # TODO: [taqchi] create these accounts
    author_email='project+xoutil@merchise.com',
    # TODO: Negotiate with Maykel Moya to obtain plain "Merchise" folder at
    #       "https://github.com"
    # TODO: [taqchi] manage these accounts
    url='https://github.com/merchise/xoutil/',
    license='GPLv3+',
    tests_require=['pytest'],
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # TODO: 'six>=1.5.0,<2', removed
    ],
    extras_require={
        'extra': ['python-dateutil', ],
    },
    cmdclass={'test': PyTest},
)
