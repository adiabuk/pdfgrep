#!/usr/bin/env python

"""
Setup script for pdfgrep - a pdf grepping utility
"""

from setuptools import setup

with open('requirements.txt', 'r') as reqs_file:
    REQS = reqs_file.readlines()
VER = '0.10'

setup(
    name='pdfgrep',
    packages=['pdfgrep'],
    version=VER,
    description='a grep tool for pdf files',
    author='Amro Diab',
    author_email='adiab@linuxmail.org',
    url='https://github.com/adiabuk/pdfgrep',
    download_url=('https://github.com/adiabuk/pdfgrep/archive/{0}.tar.gz'
                  .format(VER)),
    keywords=['pdf', 'grep'],
    install_requires=REQS,
    entry_points={'console_scripts':['pdfgrep=pdfgrep.pdfgrep:main']},
    test_suite='tests.test_pdfgrep',
    classifiers=[],
)
