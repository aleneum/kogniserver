#!/bin/bash

openssl req -nodes -new -x509 -keyout server.key \
        -subj '/C=DE/ST=NRW/L=Bielefeld/O=Bielefeld University/CN=localhost/' \
        -out server.crt
