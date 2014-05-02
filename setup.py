# new version to pypi => python setup.py sdist upload
from setuptools import setup

setup(
    name='pbdeploy',
    description='pbdeploy (port-based deploy) is a script that handles starting, reloading and stopping your server processes, without requiring a daemon or pidfiles. It also supports running scripts before and after certain services are loaded, such as installing requirements, performing database migrations, and running tests, to make continuous deployment a breeze.',
    version='1.8',
    packages=['pbdeploy'],
    scripts=['bin/pbdeploy'],
    license='The MIT License',
    author='Michael Rooney',
    author_email='mrooney.pbdeploy@rowk.com',
    url='https://github.com/mrooney/pbdeploy',
    install_requires=['psutil==2.1.0'],
)
