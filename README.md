# KogniServer [![Build Status](https://travis-ci.org/aleneum/kogniserver.svg?branch=master)](https://travis-ci.org/aleneum/kogniserver) [![Coverage Status](https://coveralls.io/repos/github/aleneum/kogniserver/badge.svg?branch=master)](https://coveralls.io/github/aleneum/kogniserver?branch=master)

A web server and bridge between networks using the Web Application Message Protocol ([WAMP](http://wamp-proto.org/)) and the Robotic Service Bus ([RSB](https://code.cor-lab.org/projects/rsb)) build upon [crossbar](http://crossbar.io/).
WAMP is provided by [autobahn](http://autobahn.ws/). This software is actively developed as part of the project [KogniHome](http://www.kognihome.de).


## Installation

KogniServer can be obtained via pip

```bash
$ pip install kogniserver
```

or cloned and installed from github

```bash
$ git clone https://github.com/aleneum/kogniserver.git
$ cd kogniserver
$ python setup.py install (--prefix=/install/path/prefix)
$ # python setup.py install --prefix=/usr/local
```

`/install/path` should be the *root* of your preferred environment and will be concatenated with *'lib/python2.7/site-packages'*. Make sure that `/install/path/lib/python2.7/site-packages` is in your `PYTHONPATH`.


### Configuration and Starting

To configure crossbar you need to create a `config.json` and tell crossbar where to find it. `kogniserver` will assist you in creating a file if it cannot find one.

```bash
$ kogniserver 
config.json for crossbar does not exists. Should a default one be created? [y]/n:y
Location of proto-files? [/usr/local/share/rst0.12/proto]:/usr/local/share/rst0.12/proto/
No Crossbar.io instance is currently running from node directory /home/foobar/kogniserver.
...
```

This will create a common config.json at `/install/path/etc/crossbar/config.json` (e.g. `/usr/local/etc...`)
If you like to use an existing config.json you can use the `-c` option:
```bash
$ kogniserver -c /path/to/your/crossbar/config.json
...
```

To overwrite an existing config.json at `/install/path/etc/crossbar/config.json`, start `kogniserver` with `-f`:
```bash
$ kogniserver -f
Location of proto-files? [/usr/local/share/rst0.12/proto]:
...
```

Alternatively you can start crossbar and kogniserver individually. First start a crossbar instance:
```bash
$ crossbar start --config=/path/to/config.json
```

After that you can initialize `kogniserver`:
```
$ kogniserver -k # --keep-alive; use existing crossbar instance
kogniserver(asyncio) started...
```

The `--keep-alive` flag will tell `kogniserver` to use the running instance. If it is not passed, `kogniserver` will
try to shutdown this instance and start a new one.

If you use the standard configuration, files will be hosted under `/install/path/var/www/kogniserver` and can be reached via
`http://localhost:8181`.

`Ctrl+C` or a `SIGTERM` will exit the server.

### What now?

If you plan to write applications in javascript, head over to the [KogniJS-Framework](http://github.com/kognihome/kognijs).

## Acknowledgements

The development of this software was supported through project grants [KogniHome](kogni-home.de) (German Federal Ministry of Education and Research (BMBF) grant no. 16SV7054K) at Bielefeld University.
