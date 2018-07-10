from setuptools import setup, find_packages
from setuptools.command.install import install
import os
from os.path import join, exists, abspath
import json

setup(
    name='kogniserver',
    version='0.2.4',
    maintainer='Alexander Neumann',
    maintainer_email='aleneum@gmail.com',
    url='http://github.com/aleneum/kogniserver',
    description="Interface server of the KogniHome project",
    platforms=['Any'],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    tests_require=['nose>=1.3', 'coverage'],
    # pyasn and following are some requirements of autobahn
    install_requires=['crossbar >=16, <17', 'autobahn >=0.16, <0.17',
                      'trollius', 'rsb-python', 'pyasn1 <0.5.0, >=0.4.1',
                      'idna <2.7, >=2.5', 'numpy','scipy'],
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
