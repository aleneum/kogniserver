from setuptools import setup, find_packages
from setuptools.command.install import install
import os
from os.path import join, exists, abspath
import json


class Install(install):
    user_options = install.user_options + [
            ('protopath=', None, 'path to protocol files'),
            ('overwrite-config', None, 'overwrite previously installed crossbar config')
        ]

    def initialize_options(self):
        install.initialize_options(self)
        self.protopath = False
        self.overwrite_config = False

    def run(self):
        install.run(self)
        install.do_egg_install(self)
        self.prefix = abspath(self.prefix)
        self.protopath = abspath(self.protopath) if self.protopath else False
        conf_path = join(self.prefix, 'etc/crossbar')
        if exists(conf_path) is False:
             os.makedirs(conf_path)

        conf_file = join(conf_path, 'config.json')
        if exists(conf_file) is False or self.overwrite_config:
            protopath = self.protopath if self.protopath else join(self.prefix, 'share/rst0.12/proto')
            with open(conf_file, 'w') as target:
                try:
                    with open('config.json.in') as template:
                        j = json.load(template)
                        paths = j['workers'][0]['transports'][0]['paths']
                        paths['/']['directory'] = join(self.prefix, paths['/']['directory'])
                        paths['proto']['directory'] = protopath
                        json.dump(j, target, indent=4)
                except Exception as e:
                    raise Exception(abspath('config.json.in'))

setup(
    name='kogniserver',
    version='0.1.0',
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
    install_requires=['txaio', 'pyasn1', 'autobahn<0.13.0', 'crossbar<0.13.0', 'trollius', 'rsb-python<0.13.0'],
    entry_points={
        "console_scripts": [
            "kogniserver = kogniserver.async:main_entry",
        ]
    },
    cmdclass={
        'install': Install
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
