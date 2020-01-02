from setuptools import setup

setup(
    name='xml-c14n',
    version='0.1.0',
    author='Nikita Ryabinin',
    license='Apache 2',
    install_requires=['lxml'],
    description='Canonical XML Version 1.0',
    url='https://github.com/WoolenSweater/xml-c14n',
    packages=['c14n']
)
