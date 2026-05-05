from setuptools import find_packages
from setuptools import setup

setup(
    name='phantomx_package',
    version='0.0.0',
    packages=find_packages(
        include=('phantomx_package', 'phantomx_package.*')),
)
