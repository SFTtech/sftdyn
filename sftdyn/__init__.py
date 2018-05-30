"""
sftdyn is a simple dynamic dns server for http requests
which then update dns records with nsupdate.
"""

VERSION = "0.7"


import asyncio
from logging import info


from .args import parse_args
from .util import log_setup
from .server import Server


def main():
    args = parse_args(__doc__)

    log_setup(args.verbose - args.quiet)

    # the known ip associations
    # maps host => ip
    associations = dict()

    loop = asyncio.get_event_loop()
    loop.set_debug(args.debug)

    if args.http:
        http_server = server.Server(args.http,
                                    args.clients,
                                    associations,
                                    args.nsupdatecommand)
        info("starting http server at %s:%d" % args.http)
        loop.run_until_complete(http_server.listen(loop))

    if args.https:
        https_server = server.Server(args.https,
                                     args.clients,
                                     associations,
                                     args.nsupdatecommand,
                                     tls=(args.cert, args.key))
        info("starting https server at %s:%d" % args.https)
        loop.run_until_complete(https_server.listen(loop))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("exiting...")
    loop.close()
