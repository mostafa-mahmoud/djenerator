#!/usr/bin/env python3
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
      long_description=open('README.md', 'r').read(),
      url='https://github.com/mostafa-mahmoud/djenerator',
      download_url='https://github.com/mostafa-mahmoud/djenerator/archive/v1.1.tar.gz',
      license='MIT',
      packages=['djenerator', 'djenerator.core', 'djenerator.management', 'djenerator.management.commands'],
      install_requires=install_requires,
      long_description_content_type="text/markdown",
      classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: Web Environment',
            'Framework :: Django :: 1.10',
            'Framework :: Django :: 1.11',
            'Framework :: Django :: 2',
            'Framework :: Django :: 2.0',
            'Framework :: Django :: 2.1',
            'Framework :: Django :: 2.2',
            'Framework :: Django :: 3',
            'Framework :: Django :: 3.0',
            'Framework :: Django :: 3.1',
            'Framework :: Django :: 3.2',
            'Framework :: Django :: 4',
            'Framework :: Django :: 4.0',
            'Framework :: Django :: 4.1',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3 :: Only',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'Topic :: Software Development :: Libraries :: Python Modules',
      ],
  )
