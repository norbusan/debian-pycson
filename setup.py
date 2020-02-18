#!/usr/bin/env python
# coding: utf-8

from setuptools import setup

with open('README.md', 'r') as fin:
    _long_description = fin.read()

setup(
    name='cson',
    version='0.8',

    description='A parser for Coffeescript Object Notation (CSON)',
    long_description=_long_description,
    long_description_content_type='text/markdown',

    author='Martin Vejnár',
    author_email='vejnar.martin@gmail.com',
    url='https://github.com/avakar/pycson',
    license='MIT',

    packages=['cson'],
    install_requires=['speg'],

    classifiers=[
        # Supported python versions
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',

        # License
        'License :: OSI Approved :: MIT License',

        # Topics
        'Topic :: Software Development :: Libraries',
        ]
    )
