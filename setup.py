from setuptools import setup, find_packages
import sys, os

version = '1.0'

setup(name='inferdtd',
      version=version,
      description="Implements the iDTD algorithm",
      long_description=open('README', 'r').read()+'\n',
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='DTD inference',
      author='Manuel V\xc3\xa1zquez Acosta',
      author_email='mva.led@gmail.com',
      url='http://manuelonsoftware.wordpress.com/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      # idtd=inferdtd.idtd:main
      """,
      )
