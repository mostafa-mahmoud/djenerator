#!/usr/bin/env python
from setuptools import setup

VERSION = __import__('djenerator').__version__

install_requires = [
    'django>=1.10',
]

setup(name='djenerator',
      version=VERSION,
      description='A simple app for generating test data for a given django models description.',
      author='Mostafa M. Mohamed',
      author_email='mostafa.amin93@gmail.com',
      long_description=('\n%s' % open('README.rst', 'r').read()),
      url='https://github.com/mostafa-mahmoud/djenerator',
      download_url='https://github.com/mostafa-mahmoud/djenerator/archive/v1.0.1.tar.gz',
      license='MIT',
      packages=['djenerator', 'djenerator.management', 'djenerator.management.commands'],
      test_suite='runtests',
      install_requires=install_requires,
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Web Environment',
          'Framework :: Django :: 1.10',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.7',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      )
