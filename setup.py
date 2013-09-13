# -*- encoding: utf-8 -*-
# Copyright (c) 2010-2013 by Yaco Sistemas <ant30tx@gmail.com> or <goinnn@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this programe.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages
import os


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.5.0'

long_description = (
    read('README.rst')
    + '\n' +
    'Contributors\n'
    '************\n'
    + '\n' +
    read('CONTRIBUTORS.rst')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' +
    read('CHANGES.rst')
    + '\n' +
    'Download\n'
    '********\n')


setup(name='django-inlinetrans',
      version=version,
      description="Is a django application that allows the translation of django templtes from the rendered html in the browser",
      long_description=long_description,
      classifiers=[
            'Development Status :: 4 - Beta',
            'Framework :: Django',
            'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 3',
      ],
      keywords='django translation,django,translation,inline',
      author='Antonio Pérez-Aranda Alcaide',
      author_email='ant30tx@gmail.com',
      url='https://github.com/Yaco-Sistemas/django-inlinetrans',
      license='LGPL 3',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      install_requires=['polib==1.0.3'])
