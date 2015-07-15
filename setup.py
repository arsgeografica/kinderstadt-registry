#!/usr/bin/env python

import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import versioneer


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ''

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.pytest_args + ' test')
        sys.exit(errno)

cmd_classes = versioneer.get_cmdclass()
cmd_classes['test'] = PyTest


setup(
    name="kinderstadt-registry",
    version=versioneer.get_version(),
    cmdclass=cmd_classes,
    packages=find_packages(),
    install_requires=[
        'alembic==0.7.6',
        'click==4.0',
        'fake-factory==0.5.2',
        'Flask-Migrate==1.4.0',
        'Flask-SQLAlchemy==2.0',
        'Flask-WTF==0.11',
        'Flask==0.10.1',
        'path.py==7.3',
        'pgcli==0.17.0',
        'python-stdnum==1.1',
    ],
    extras_require={
        'devel': [
            'ansible',
            'autopep8',
            'flake8',
            'ipython',
        ],
    },
    tests_require=[
        'pytest',
        'testing.postgresql'
    ],
    entry_points={
        'console_scripts': [
            'registry=registry.cli:main'
        ]
    }
)
