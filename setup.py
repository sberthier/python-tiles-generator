# encoding=UTF-8

# Copyright © 2015 Sébastien Berthier <sebastien.berthier@haumea.fr>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the “Software”), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

'''
an image tile generator accepting multiple scale level
'''

classifiers = '''
Development Status :: 4 - Beta
Intended Audience :: Developpers
License :: OSI Approved :: MIT License
Environment :: Console
Operating System :: POSIX
Programming Language :: Python
Programming Language :: Python :: 3
Programming Language :: Python :: 2
Topic :: Multimedia :: Graphics
'''.strip().splitlines()


from distutils.core import setup
from distutils.command.build_py import build_py

try:
    f = open('doc/changelog', encoding='UTF-8')
except TypeError:
    f = open('doc/changelog')

try:
    version = f.readline().split()[1].strip('()')
finally:
    f.close()

setup(
    name = 'python-tile-generator',
    version = version,
    license = 'MIT',
    description = 'an image tile genetator accepting multiple scale level',
    author = 'Sébastien Berthier',
    author_email = 'sebastien.berthier@haumea.fr',
    url = 'none',
    long_description = __doc__.strip(),
    classifiers = classifiers,
    cmdclass = dict(build_py=build_py),
    py_modules = ['tiles-generator'],
)

# vim:ts=4 sw=4 et
