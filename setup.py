from setuptools import setup, find_packages, Command
from setuptools.command.install import install
import os
import stat
import os.path
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
        self.prefix = os.path.abspath(self.prefix)
        self.protopath = os.path.abspath(self.protopath) if self.protopath else False
        conf_path = os.path.join(self.prefix, 'etc/crossbar')
        if os.path.exists(conf_path) is False:
             os.makedirs(conf_path)

        conf_file = os.path.join(conf_path, 'config.json')
        if os.path.exists(conf_file) is False or self.overwrite_config:
            protopath = self.protopath if self.protopath else os.path.join(self.prefix, 'share/rst0.12/proto')
            with open(conf_file, 'w') as target:
                with open('config.json.in') as template:
                    j = json.load(template)
                    paths = j['workers'][0]['transports'][0]['paths']
                    paths['/']['directory'] = os.path.join(self.prefix, paths['/']['directory'])
                    paths['proto']['directory'] = protopath
                    json.dump(j, target, indent=4)

        bin_path = os.path.join(self.prefix, 'bin')
        if os.path.exists(bin_path) is False:
            os.makedirs(bin_path)
        bin_file = os.path.join(bin_path, 'run_displayserver.sh')
        with open('run_displayserver.sh.in', 'r') as template:
            with open(bin_file, 'w') as target:
                tmp = template.read().format(prefix=self.prefix)
                target.write(tmp)
        st = os.stat(bin_file)
        os.chmod(bin_file, st.st_mode | stat.S_IEXEC)


setup(
    name='Display Server',
    version='0.0.9',
    description="Display Server WAMP Component",
    platforms=['Any'],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    setup_requires=['nose>=1.3', 'coverage'],
    install_requires=['txaio','pyasn1','autobahn<0.13.0','crossbar<0.13.0','trollius'],
    entry_points = {
        "console_scripts": [
            "asyncio-rsb-bridge = rsb_wamp_brige.asyncio:main_entry",
        ]
    },
    cmdclass={
        'install': Install
    }
)
