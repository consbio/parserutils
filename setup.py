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


with open('README.md') as readme:
    long_description = readme.read()


setup(
    name='parserutils',
    description='A collection of performant parsing utilities',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='parser,parsing,utils,utilities,collections,dates,elements,numbers,strings,url,xml',
    version='1.1.2',
    packages=[
        'parserutils', 'parserutils.tests'
    ],
    install_requires=[
        'defusedxml>=0.4.1', 'python-dateutil>=2.4.2', 'six>=1.9.0'
    ],
    tests_require=['mock'],
    url='https://github.com/consbio/parserutils',
    license='BSD',
    cmdclass={'test': RunTests}
)
