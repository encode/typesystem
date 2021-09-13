#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys

from setuptools import setup

sys.dont_write_bytecode = True


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


def get_packages(package):
    """
    Return root package and all sub-packages.
    """
    return [dirpath
            for dirpath, dirnames, filenames in os.walk(package)
            if os.path.exists(os.path.join(dirpath, '__init__.py'))]


version = get_version('typesystem')


setup(
    name='typesystem',
    version=version,
    url='https://github.com/encode/typesystem',
    license='BSD',
    description='A type system library for Python',
    author='Tom Christie',
    author_email='tom@tomchristie.com',
    packages=get_packages('typesystem'),
    package_data={'typesystem': ['py.typed', 'templates/forms/*.html']},
    install_requires=[],
    extras_require={
        "jinja2": ["jinja2"],
        "pyyaml": ["pyyaml"],
    },
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    zip_safe=False
)
