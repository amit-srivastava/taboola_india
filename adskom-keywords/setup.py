#!/usr/bin/env python

from setuptools import setup

setup(name='adskom-keywords',
      version='0.0.2',
      description='Sync functionality for extracting data from the Log files',
      author='Amit Srivastava',
      email='s.amitsrivastava@gmail.com',
      classifiers=['Programming Language :: Python :: 3 :: Only'],
      py_modules=['adskom_keywords'],
      install_requires=[
          'singer-python==0.2.1',
          'backoff==1.3.2',
          'requests==2.12.4',
          'python-dateutil==2.6.0',
          'PyMySQL==0.7.11',
          'mysqlclient==1.3.12'
      ],
      entry_points='''
          [console_scripts]
          adskom-keywords=adskom_keywords:main
      ''',
      packages=['adskom_keywords']
)
