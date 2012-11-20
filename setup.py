#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:       Alisue
# Last Change:  13-Nov-2012.
#
from setuptools import setup, find_packages

version = "2.35.0" # Now uses codemirror-Version + sub-version for django-c..-m..
codemirror_version = "2.35"

def read(filename):
    import os.path
    return open(os.path.join(os.path.dirname(__file__), filename)).read()
setup(
    name="django-codemirror-widget",
    version=version,
    description = "django-codemirror-widget is Django form widget library for using CodeMirror on textarea",
    long_description=read('README.rst'),
    classifiers = [
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ],
    keywords = "django widget textarea codemirror",
    author = "Alisue,Phaiax",
    author_email = "lambdalisue@hashnote.net,phaiax@invisibletower.de",
    url=r"https://github.com/lambdalisue/django-codemirror-widget",
    download_url = r"https://github.com/lambdalisue/django-codemirror-widget/tarball/master",
    license = 'BSD',
    packages = find_packages(),
    include_package_data = True,
    zip_safe = False,
    install_requires=['setuptools'],
)
