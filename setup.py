from setuptools import setup, find_packages
from setuptools.command.install import install
import os
import codecs
from os.path import join, exists, abspath
import json

with codecs.open('README.md', 'r', 'utf-8') as f:
    # cut the badges from the description and also the TOC which is currently not working on PyPi
    long_description = ''.join(f.readlines()[2:])

setup(
    name='kogniserver',
    version='0.3.1',
    maintainer='Alexander Neumann',
    url='http://github.com/kognihome/kogniserver',
    description="Interface server of the KogniHome project",
    long_description=long_description,
    long_description_content_type="text/markdown",
    platforms=['Any'],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    tests_require=['nose>=1.3', 'coverage'],
    # pyasn and following are some requirements of autobahn
    install_requires=['six', 'crossbar <=18.4.1', 'trollius', 'rsb-python', 'Twisted>=17.5.0', 'attrs>=17.4.0'],
    entry_points={
        "console_scripts": [
            "kogniserver = kogniserver.adm:main_entry",
            "kogniclient = kogniserver.client:maint_entry"
        ]
    },
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Environment :: Console',
        'Environment :: No Input/Output (Daemon)',
        'Topic :: Communications',
        'Topic :: Home Automation',
        'Topic :: Internet',
        'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
        'Topic :: System :: Distributed Computing',
        'Topic :: System :: Networking'
    ],
)
