#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

install_requires = open("requirements.txt").read().split('\n')
readme_content = open("README.md").read()

setup(
    name='pyinsales',
    version='0.6.4',
    description='InSales e-commerce platform API bindings',
    long_description=readme_content,
    author='Victor Nakoryakov',
    author_email='nail.xx@gmail.com',
    license='MIT',
    keywords="insales API bindings",
    url='https://github.com/nailxx/pyinsales',
    packages=['insales'],
    install_requires=install_requires,
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Natural Language :: Russian",
        "Topic :: Utilities",
    ],
)
