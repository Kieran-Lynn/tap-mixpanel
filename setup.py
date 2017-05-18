#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='tap-mixpanel',
      version='0.0.4',
      description='Singer.io tap for extracting data from the Mixpanel API',
      author='Kieran Lynn',
      author_email='Kieran.J.Lynn@gmail.com',
      url='https://github.com/Kierchon/tap-mixpanel',
      classifiers=['Programming Language :: Python :: 3 :: Only'],
      py_modules=['tap_mixpanel'],
      install_requires=['singer-python==1.5.0',
                        'requests>=2.12.4'],
      entry_points='''
          [console_scripts]
          tap-mixpanel=tap_mixpanel:main
      ''',
      packages=['tap_mixpanel'],
      package_data={
          'tap_mixpanel/schemas': [
              'events.json'
              ]
          },
      include_package_data=True,
)
