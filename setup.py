import os
from distutils.core import setup

from setuptools import find_packages


def requirements(fname):
    return [line.strip()
            for line in open(os.path.join(os.path.dirname(__file__), fname))]

setup(
    name='mwdiffs',
    version="0.0.2", # See also mwdiffs/__init__.py
    author='Aaron Halfaker',
    author_email='aaron.halfaker@gmail.com',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'mwdiffs=mwdiffs.mwdiffs:main'
        ],
    },
    scripts=[],
    url='http://pypi.python.org/pypi/mwdiffs',
    license=open('LICENSE').read(),
    description='A set of utilities for processing revision diffs from ' +
                'MediaWiki data.',
    long_description=open('README.md').read(),
    install_requires=requirements("requirements.txt"),
    test_suite='nose.collector',
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: General",
        "Topic :: Utilities",
        "Topic :: Scientific/Engineering"
    ],
)
