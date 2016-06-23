import argparse
from os.path import abspath, exists, join
import json
import re
import subprocess
import threading
import time


def run_crossbar(config_path):
    subprocess.call(['crossbar', 'start', '--config=%s' % config_path])

def main_entry():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', help='administration action to be executed', choices=['configure', 'start'])
    parser.add_argument('-p', '--protopath', help='path containing proto files', type=str)
    parser.add_argument('-f', '--force', help='overwrite config file if it already exists', action='store_true')
    args = parser.parse_args()

    pwd = abspath(__file__)
    elems = re.compile('[\\\\/]+').split(pwd)[:-6]
    prefix = join("/", *elems)
    config_path = join(prefix, 'etc/crossbar/config.json')

    if args.command == 'configure':

        protopath = abspath(args.protopath) if args.protopath else False

        if exists(config_path) and not args.force:
            print "Config file already exists! Use --force to overwrite."
            return

        with open(join(prefix, 'etc/crossbar/config.json'), 'w') as target:
            j = json.loads(CONFIG_JSON)
            paths = j['workers'][0]['transports'][0]['paths']
            paths['/']['directory'] = join(prefix, paths['/']['directory'])
            if protopath:
                paths['proto']['directory'] = protopath
            else:
                del paths['proto']
            json.dump(j, target, indent=4)

    elif args.command == 'start':
        t = threading.Thread(target=run_crossbar, args=(config_path,))
        t.start()
        time.sleep(3)
        subprocess.call(['kogniserver'])

CONFIG_JSON = """
{
   "controller": {
   },
   "workers": [
      {
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
                           "uri": "*",
                           "publish": true,
                           "subscribe": true,
                           "call": true,
                           "register": true
                        }
                     ]
                  }
               ]
            }
         ],
         "transports": [
            {
               "type": "web",
               "endpoint": {
                  "type": "tcp",
                  "port": 8181
               },
               "paths": {
                  "ws": {
                    "type": "websocket"
                  },
                  "/": {
                     "type": "static",
                     "directory": "var/www/kogniserver"
                  },
                  "proto": {
                    "type": "static",
                    "directory": ""
                  }
               }
            }
         ]
      }
   ]
}
"""