import subprocess
from setuptools import setup

setup(
    name='smviz',
    version='0.1',
    author='Robert Feldhans',
    packages=['smviz'],
    #license='LGPLv3', #Your call, Rober
    long_description=open('README.md').read(),
    url="https://github.com/Slothologist/Statemachine-Visualization",
    download_url="https://github.com/Slothologist/Statemachine-Visualization",
    install_requires=['graphviz']
)
