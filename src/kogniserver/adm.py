import argparse
from os import makedirs
from os.path import abspath, exists, join, dirname, expanduser
import re
import subprocess
import time
import json
import threading
import socket
import sys


def run_crossbar(config_path, keep_alive):
    ret = subprocess.call(['crossbar', 'status'])
    if ret == 0 and not keep_alive:
        subprocess.call(['crossbar', 'stop'])

    if ret != 0 or not keep_alive:
        cmd = ['crossbar', 'start', '--config=%s' % config_path]
        subprocess.call(cmd)


def main_entry(args=None):

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--force', help='overwrite config file if it already exists', action='store_true')
    parser.add_argument('-k', '--keep-alive', help='use existing crossbar instance', action='store_true')
    parser.add_argument('-c', '--config', help='location of the config file')
    parser.add_argument('-g', '--generate', help='only generate config file (with default options)', action='store_true')
    args = sys.argv[1:] if args is None else args
    args = parser.parse_args(args)

    pwd = abspath(__file__)
    elems = re.compile('[\\\\/]+').split(pwd)
    if 'site-packages' in elems:
        idx = elems.index('site-packages')
        elems = elems[:idx-2]
    else:
        elems = elems[:-1]
    prefix = join("/", *elems)
    serve_path = join(prefix, "var/www/kogniserver")
    config_path = join(prefix, 'etc/crossbar/config.json') if not args.config else args.config

    choice = 'n'

    if exists(config_path) is False:
        input_valid = False if not args.generate else True
        while not input_valid:
            choice = raw_input("config.json for crossbar does not exists. Should a default one be created "
                               "at %s? [y]/n:" % config_path) or 'y'
            if choice not in ['y', 'n']:
                print("please enter 'y' or 'n'.")
            else:
                input_valid = True

    if choice in 'y' or args.force:
        input_valid = False if not args.generate else True
        while not input_valid:
            serve_path = raw_input("Please enter the directory from which "
                                   "files should be served [%s]:" % serve_path) or serve_path
            serve_path = expanduser(serve_path)
            if not exists(serve_path):
                choice = raw_input("%s does not exist. Should it be created? [y]/n: " % serve_path) or 'y'
                if choice not in ['y', 'n']:
                    print("please enter 'y' or 'n'.")
                elif choice == 'y':
                    makedirs(serve_path)
                    input_valid = True
            else:
                input_valid = True

        protopath = join(prefix, 'share/rst0.17/proto')
        input_valid = False if not args.generate else True
        while not input_valid:
            protopath = raw_input("Location of proto-files? [%s]:" % protopath) or protopath
            if not exists(protopath) and not args.generate:
                choice = raw_input("%s does not exist! "
                                   "Do you want to ommit RST in your configuration? [y]/n:" % protopath) or 'y'
                if choice not in ['y', 'n']:
                    print("please enter 'y' or 'n'.")
                if choice =='y':
                    input_valid = True
                    protopath = None
            else:
                input_valid = True

        if exists(config_path) and not args.force:
            print "Config file already exists! Use --force to overwrite."
            return
        else:
            if not exists(dirname(abspath(config_path))):
                makedirs(dirname(abspath(config_path)))

        ssl_cert = False
        input_valid = False if not args.generate else True
        while not input_valid:
            ssl_cert = raw_input("Location of TLS certificate (without .crt and .key) if needed. "
                                 "Leave empty if not needed:") or ssl_cert
            input_valid = True
            if ssl_cert:
                if not exists(ssl_cert + ".crt"):
                    print("%s does not exist!" % (ssl_cert + ".crt"))
                    input_valid = True
                    ssl_cert = False

        with open(config_path, 'w') as target:
            j = json.loads(CONFIG_JSON)
            paths = j['workers'][0]['transports'][0]
            paths['paths']['/']['directory'] = serve_path
            if protopath:
                paths['paths']['proto']['directory'] = protopath
            else:
                del paths['paths']['proto']
            if ssl_cert:
                paths['endpoint']['tls']['key'] = ssl_cert + '.key'
                paths['endpoint']['tls']['certificate'] = ssl_cert + '.crt'
            else:
                del paths['endpoint']['tls']

            json.dump(j, target, indent=4)

    # In a dry generation run we can exit here
    if args.generate:
        return

    t1 = threading.Thread(target=run_crossbar, args=(config_path, args.keep_alive,))
    t1.setDaemon(True)
    t1.start()
    while not check_server('localhost', 8181):
        time.sleep(0.5)
    with open(config_path) as crossbar_config:
        j = json.load(crossbar_config)
        ssl_cert = None
        if 'tls' in j['workers'][0]['transports'][0]['endpoint']:
            ssl_cert = j['workers'][0]['transports'][0]['endpoint']['tls']['certificate']
    try:
        # async cannot deal with ssl yet and importing the runner
        # already sets the environment to asyncio
        if ssl_cert:
            raise RuntimeError
        from .async import main_entry as server_main_entry
    except RuntimeError:
        # will be used if a) twisted has been used before or if an ssl_cert should be used
        from .twist import main_entry as server_main_entry
    server_main_entry(ssl_cert)


def check_server(address, port):
    # Create a TCP socket
    s = socket.socket()
    try:
        s.connect((address, port))
        # print "Connected to %s on port %s" % (address, port)
        s.close()
        return True
    except socket.error, e:
        # print "Connection to %s on port %s failed: %s" % (address, port, e)
        return False


CONFIG_JSON = """
{
  "version": 2,
  "controller": {},
  "workers": [
    {
      "transports": [
        {
          "paths": {
            "ws": {
              "type": "websocket"
            },
            "/": {
              "directory": ".",
              "type": "static"
            },
            "proto": {
              "directory": ".",
              "type": "static"
            }
          },
          "endpoint": {
            "type": "tcp",
            "port": 8181,
            "tls": {
                "key": "server.key",
                "certificate": "server.crt"
            }
          },
          "type": "web"
        }
      ],
      "type": "router",
      "options": {
        "pythonpath": [""]
      },
      "realms": [
        {
          "name": "realm1",
          "roles": [
            {
              "name": "anonymous",
              "permissions": [
                {
                  "uri": "",
                  "match": "prefix",
                  "allow": {
                    "call": true,
                    "register": true,
                    "publish": true,
                    "subscribe": true
                  },
                  "disclose": {
                    "caller": false,
                    "publisher": false
                  },
                  "cache": true
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
"""


if __name__ == '__main__':
    main_entry()
