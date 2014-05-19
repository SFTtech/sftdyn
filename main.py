#!/usr/bin/env python3
import http.server
import ssl
import sftdyn.args
import sftdyn.server

def main():
    sftdyn.args.parse()
    try:
        sftdyn.server.serve()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
