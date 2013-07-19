from setuptools import setup

setup(
    name='pbdeploy',
    description='a port-based deployment framework for practicing continuous deployment',
    version='1.1',
    packages=['pbdeploy'],
    scripts=['bin/pbdeploy'],
    license='The MIT License',
    author='Michael Rooney',
    author_email='mrooney.pbdeploy@rowk.com',
    url='https://github.com/mrooney/pbdeploy',
    install_requires=['psutil'],
)
