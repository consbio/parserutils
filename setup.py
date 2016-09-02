import subprocess
import sys

from setuptools import Command, setup


class RunTests(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        errno = subprocess.call([sys.executable, '-m', 'unittest', 'parserutils.tests.tests'])
        raise SystemExit(errno)


setup(
    name='parserutils',
    description='A collection of performant parsing utilities',
    keywords='parser,parsing,utils,utilities,collections,dates,elements,numbers,strings,url,xml',
    version='0.1.0',
    packages=[
        'parserutils', 'parserutils.tests'
    ],
    install_requires=[
        'defusedxml', 'python-dateutil', 'six'
    ],
    url='https://github.com/consbio/parserutils',
    license='BSD',
    cmdclass={'test': RunTests}
)
