import argparse
from os.path import abspath, exists, join
import re
import subprocess
import json
import threading
import time
import sys

from .async import main_entry as async_main


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
        input_valid = False
        while not input_valid:
            choice = raw_input("config.json for crossbar does not exists. Should a default one be created? [y]/n:") or 'y'
            if choice not in ['y','n']:
                print("please enter 'y' or 'n'.")
            else:
                input_valid = True

    if choice in 'y' or args.force:
        default_path = config_path
        input_valid = False
        while not input_valid:
            protopath = raw_input("Location of proto-files? [%s]:" % default_path) or default_path
            if not exists(protopath):
                print("%s does not exist!" % protopath)
            else:
                input_valid = True

        if exists(config_path) and not args.force:
            print "Config file already exists! Use --force to overwrite."
            return

        with open(config_path, 'w') as target:
            j = json.loads(CONFIG_JSON)
            paths = j['workers'][0]['transports'][0]['paths']
            paths['/']['directory'] = join(prefix, paths['/']['directory'])
            if protopath:
                paths['proto']['directory'] = protopath
            else:
                del paths['proto']
            json.dump(j, target, indent=4)

    t1 = threading.Thread(target=run_crossbar, args=(config_path,args.keep_alive,))
    t1.setDaemon(True)
    t1.start()
    time.sleep(5)
    async_main()


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
              "directory": "./config.json",
              "type": "static"
            }
          },
          "endpoint": {
            "type": "tcp",
            "port": 8181
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