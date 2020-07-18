#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from geopayment import __version__


def read(filename):
    with open(filename, encoding='utf-8') as fd:
        return fd.read()


setup(
    name='geopayment',
    version=__version__,
    author='Lasha Gogua',
    author_email='gogualasha@gmail.com',
    description='Python SDK for Georgian Payment Providers',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/Lh4cKg/geopayment',
    license='MIT',
    keywords=['python', 'geopayment', 'payments', 'sdk', 'merchant'],
    platforms=['OS Independent'],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 3.7',
    ],
    install_requires=[
        'cryptography>=2.9.2',
        'pyOpenSSL>=19.1.0',
        'requests>=2.24.0',
    ],
    packages=find_packages(exclude=['example', 'docs']),
    include_package_data=True,
    zip_safe=False,
)
