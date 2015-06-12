#!/usr/bin/env python

from setuptools import setup, find_packages
import versioneer


setup(
    name="kinderstadt-registry",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    packages=find_packages(),
    install_requires=[
    ],
    extras_require={
        'devel': [
            'ansible',
            'autopep8',
            'flake8',
            'ipython',
        ],
    },
)
