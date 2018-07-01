#!/usr/bin/env python

from setuptools import setup

setup(name='adskom-outbrain',
      version='0.0.1',
      description='Sync functioanlity for extracting data from the Outbrain API',
      author='Amit Srivastava',
      email='s.amitsrivastava@gmail.com',
      classifiers=['Programming Language :: Python :: 3 :: Only'],
      py_modules=['adskom_outbrain'],
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
          adskom-outbrain=adskom_outbrain:main
      ''',
      packages=['adskom_outbrain']
)
