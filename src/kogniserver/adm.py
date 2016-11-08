import argparse
from os import makedirs
from os.path import abspath, exists, join, dirname
import re
import subprocess
import time
import json
import threading
import socket
import sys

from .twist import main_entry as async_main


def run_crossbar(config_path, keep_alive):
    ret = subprocess.call(['crossbar', 'status'])

    if ret == 0 and not keep_alive:
        subprocess.call(['crossbar', 'stop'])

    if ret != 0 or not keep_alive:
        subprocess.call(['crossbar', 'start', '--config=%s' % config_path])


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

    config_path = join(prefix, 'etc/crossbar/config.json') if not args.config else args.config

    choice = 'n'
    if exists(config_path) is False:
        input_valid = False if not args.generate else True
        while not input_valid:
            choice = raw_input("config.json for crossbar does not exists. Should a default one be created? [y]/n:") or 'y'
            if choice not in ['y', 'n']:
                print("please enter 'y' or 'n'.")
            else:
                input_valid = True

    if choice in 'y' or args.force:
        protopath = join(prefix, 'share/rst0.12/proto')
        input_valid = False if not args.generate else True
        while not input_valid:
            protopath = raw_input("Location of proto-files? [%s]:" % protopath) or protopath
            if not exists(protopath) and not args.generate:
                print("%s does not exist!" % protopath)
            else:
                input_valid = True

        if exists(config_path) and not args.force:
            print "Config file already exists! Use --force to overwrite."
            return
        else:
            if not exists(dirname(config_path)):
                makedirs(dirname(config_path))

        ssl_cert = False
        input_valid = False if not args.generate else True
        while not input_valid:
            ssl_cert = raw_input("Location of TLS certificate (without .crt and .key) if needed."
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
            paths['paths']['/']['directory'] = join(prefix, paths['paths']['/']['directory'])
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

    t1 = threading.Thread(target=run_crossbar, args=(config_path,args.keep_alive,))
    t1.setDaemon(True)
    t1.start()
    while not check_server('localhost', 8181):
        time.sleep(0.5)
    with open(config_path) as crossbar_config:
        j = json.load(crossbar_config)
        ssl_cert = None
        if 'tls' in j['workers'][0]['transports'][0]['endpoint']:
            ssl_cert = j['workers'][0]['transports'][0]['endpoint']['tls']['certificate']
    async_main(ssl_cert)


def check_server(address, port):
    # Create a TCP socket
    s = socket.socket()
    try:
        s.connect((address, port))
        #print "Connected to %s on port %s" % (address, port)
        s.close()
        return True
    except socket.error, e:
        #print "Connection to %s on port %s failed: %s" % (address, port, e)
        return False

if __name__ == '__main__':
    main_entry()



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
              "directory": "var/www/kogniserver",
              "type": "static"
            },
            "proto": {
              "directory": "share/rst0.12/proto",
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
