#!/usr/bin/env python

import os
import sys
from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


_install_requires = [
    "mammoth>=0.1.5,<0.2",
    "watchdog>=0.6.0,<0.7.0",
]

if sys.version_info[:2] <= (2, 6):
    _install_requires.append("argparse==1.2.1")

setup(
    name='mammoth-viewer',
    version='0.1.0',
    description='Convert Word documents to simple and clean HTML in (nearly) real-time with a GUI',
    long_description=read("README"),
    author='Michael Williamson',
    author_email='mike@zwobble.org',
    url='http://github.com/mwilliamson/python-mammoth-viewer',
    packages=['mammothviewer'],
    scripts=["scripts/mammoth-viewer"],
    keywords="docx word office clean html gui",
    install_requires=_install_requires,
)

