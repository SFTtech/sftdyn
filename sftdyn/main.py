#!/usr/bin/env python3
import sftdyn.args
import sftdyn.server

def main():
    sftdyn.args.parse()
    try:
        sftdyn.server.serve()
    except KeyboardInterrupt:
        pass
