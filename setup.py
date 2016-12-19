#!/usr/bin/env python
from setuptools import setup

setup(name='Djenerator',
      version='1.0',
      description='A simple app for generating test data for a given django models.',
      author='Mostafa M. Mohamed',
      author_email='mostafa.amin93@gmail.com',
      long_description=open('README.rst', 'r').read(),
      url='https://github.com/aelguindy/djenerator',
      download_url='https://nodeload.github.com/aelguindy/djenerator/zipball/master',
      license='MIT',
      packages=['djenerator', 'djenerator.management', 'djenerator.management.commands'],
      test_suite='runtests.runtests',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Web Environment',
          'Framework :: Django',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      )
