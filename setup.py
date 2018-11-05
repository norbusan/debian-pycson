#!/usr/bin/env python
# coding: utf-8

from setuptools import setup

setup(
    name='cson',
    version='0.7',

    description='A parser for Coffeescript Object Notation (CSON)',
    author='Martin Vejnár',
    author_email='vejnar.martin@gmail.com',
    url='https://github.com/avakar/pycson',
    license='MIT',

    packages=['cson'],
    install_requires=['speg'],
    )
