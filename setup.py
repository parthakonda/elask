from distutils.core import setup
import os
from setuptools import setup, find_packages

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
  name = 'elask',
  packages=find_packages(),
  include_package_data=True,
  scripts=['elask/bin/elask-admin.py'],
  entry_points={'console_scripts': [
      'elask-admin = elask.core.management:execute_from_command_line',
  ]},
  install_requires=[
    'elasticsearch-dsl==6.0.1',
    'flasgger==0.8.0',
    'Flask==0.12.2',
    'Flask-Cors==3.0.3',
    'Flask-JWT==0.3.2',
    'Flask-RESTful==0.3.6',
    'marshmallow==2.15.0',
    'bcrypt==3.1.4',
    'pandas==0.23.0'],
  version = '3.9.4',
  description = 'elask rest framework',
  author = 'Partha Saradhi',
  author_email = 'parthasaradhi.konda@inmar.com',
  url = 'https://github.com/inmar/elask.git',
  download_url = 'https://github.com/inmar/elask.git',
  keywords = ['elasticsearch', 'rest', 'rest api', 'inmar'], # arbitrary keywords
  classifiers = [],
)
