#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

install_requires = open("requirements.txt").read().split('\n')
with open("README.md", 'rb') as f:
    readme_content = f.read().decode('utf-8')

setup(
    name='pyinsales',
    version='1.4.0',
    description='InSales e-commerce platform API bindings',
    long_description=readme_content,
    long_description_content_type="text/markdown",
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
