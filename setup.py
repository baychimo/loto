#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE.md') as f:
    license = f.read()

setup(
    name='loto',
    version='0.1.0',
    description='Having fun with lottery numbers',
    long_description=readme,
    author='Jonathan Guitton',
    author_email='jonathan.guitton@gmail.com',
    url='https://github.com/baychimo/loto',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    py_modules=['loto.core'],
    install_requires=[
        'Click',
        'colorama',
        'fbprophet',
        'JPype1',
        'matplotlib',
        'numpy',
        'pandas',
        'pyfiglet',
        'pystan',
        'python-dateutil',
        'requests',
        'scipy',
        'tqdm'
    ],
    entry_points='''
        [console_scripts]
        loto=loto.core:cli
    ''',
)
