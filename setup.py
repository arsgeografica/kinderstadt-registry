#!/usr/bin/env python

from setuptools import setup, find_packages
import versioneer


setup(
    name="kinderstadt-registry",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    packages=find_packages(),
    install_requires=[
        'alembic==0.7.6',
        'click==4.0',
        'path.py==7.3',
        'pgcli==0.17.0',
        'Flask-Migrate==1.4.0',
        'Flask-SQLAlchemy==2.0',
        'Flask==0.10.1',
    ],
    extras_require={
        'devel': [
            'ansible',
            'autopep8',
            'flake8',
            'ipython',
        ],
    },
    entry_points={
        'console_scripts': [
            'registry=registry.cli:main'
        ]
    }
)
