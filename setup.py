# -*- coding: utf-8 -*-
import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

try:
    from distutils.command.build_py import build_py_2to3 as build_py
except ImportError:
    from distutils.command.build_py import build_py

# Don't import sendhub module here, since deps may not be installed
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'sendhub'))
import version

path, script = os.path.split(sys.argv[0])
os.chdir(os.path.abspath(path))

setup(
    name='sendhub',
    cmdclass = {'build_py': build_py},
    version=version.VERSION,
    description='SendHub python bindings',
    author='SendHub',
    author_email='support@sendhub.com',
    url='https://sendhub.com/',
    packages=['sendhub'],
    package_data={'sendhub' : ['../VERSION']},
    install_requires=[
        'requests>=0.8.8',
        'simplejson>=3.3.0',
    ],
)

