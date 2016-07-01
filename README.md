# KogniServer

A web server and bridge between networks using the Web Application Message Protocol ([WAMP])(http://wamp-proto.org/) and the Robotic Service Bus ([RSB](https://code.cor-lab.org/projects/rsb)) build upon [crossbar](http://crossbar.io/).
WAMP is provided by [autobahn](http://autobahn.ws/). This software is actively developed as part of the project [KgoniHome](http://www.kognihome.de).

## Installation

KogniServer can be obtained via pip

```bash
$ pip install kogniserver
```

or cloned and installed from github

```bash
$ git clone https://github.com/aleneum/kogniserver.git
$ cd kogniserver
$ python setup.py install (--prefix=/install/path/prefx)
$ # python setup.py install --prefix=/usr/local
```

`/install/path` should be the *root* of your preferred environment and will be concatenated with *'lib/python2.7/site-packages'*. Make sure that `/install/path/lib/python2.7/site-packages` is in your `PYTHONPATH`.


### Configuration

To configure crossbar you need to create a `config.json` and tell crossbar where to find it. `kogniserver` comes with an administration tool which will create a typical crossbar configuration and get you started.

```bash
$ kogniserver-adm configure --protopath=/path/to/proto/files
$ # kogniserver-adm configure --protopath=/usr/local/share/rst0.12/proto
```

This will create a common config.json at `/install/path/etc/crossbar.json.
`-p, --protopath=` is an optional argument and can be used if protocol buffer files are already installed.
 If provided, the proto path will be linked under '/server_root/proto' into the server environment.


### Starting

The easiest way to start crossbar and kogniserver is again with the kogniserver-adm tool.

```bash
$ kogniserver-adm start
```

Alternatively you can start crossbar and kogniserver individually. First start a crossbar instance:

```bash
$ crossbar start --config=/path/to/config.json
```

After that you can initialize kogniserver:

```
$ kogniserver
kogniserver(asyncio) started...
```

If you use the standard configuration, files will be hosted under `$prefix/var/www/kogniserver` and can be reached via
`http://localhost:8181`.

### What now?

If you plan to write applications in javascript, head over to [KogniJS-Framework](http://github.com/aleneum/kognijs-rsb).