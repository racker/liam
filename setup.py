#!/usr/bin/env python

# Copyright 2015 Rackspace US, Inc.

"""Janus Python client packaging and installation."""

import os
import subprocess

import setuptools

SRC_DIR = os.path.dirname(os.path.realpath(__file__))


ABOUT = {}
with open(os.path.join(SRC_DIR, 'liam', '__about__.py'), 'r') as abt:
    exec(abt.read(), {'__builtins__': {}}, ABOUT)  # pylint: disable=exec-used


def _sha1_keyword(about, src_dir):
    """Try to find the current commit and append to package keywords."""
    try:
        current_commit = subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'],
            cwd=src_dir, universal_newlines=True).strip()
    except (OSError, subprocess.CalledProcessError):
        pass
    else:
        if current_commit and len(current_commit) == 40:
            about['__keywords__'].append(current_commit[:8])


_sha1_keyword(ABOUT, SRC_DIR)


INSTALL_REQUIRES = [
    'boto3<1.5.0',
    'botocore<1.6.0',
]


STYLE_REQUIRES = [
    'flake8>=2.5.4',
    'pylint>=1.5.5',
]


TEST_REQUIRES = [
    'coverage>=4.0.3',
    'moto>=0.4.31',
    'pytest>=2.9.1',
]


EXTRAS_REQUIRE = {
    'test': TEST_REQUIRES,
    'style': STYLE_REQUIRES,
    # alias
    'lint': STYLE_REQUIRES,
    'test-requirements': TEST_REQUIRES + STYLE_REQUIRES,
}

CLASSIFIERS = [
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.5',
]


setuptools.setup(**{
    'author': ABOUT['__author__'],
    'author_email': ABOUT['__email__'],
    'classifiers': CLASSIFIERS,
    'name': ABOUT['__title__'],
    'description': ABOUT['__summary__'],
    'extras_require': EXTRAS_REQUIRE,
    'install_requires': INSTALL_REQUIRES,
    'keywords': ' '.join(ABOUT['__keywords__']),
    'packages': setuptools.find_packages(exclude=['tests']),
    'test_suite': 'tests',
    'tests_require': TEST_REQUIRES + STYLE_REQUIRES,
    'url': ABOUT['__url__'],
    'version': ABOUT['__version__'],
})
