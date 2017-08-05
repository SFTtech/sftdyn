"""
Argument parsing for all your configuration needs.
"""

import argparse
import ipaddress
import os
from pathlib import Path


def get_parser(intro):
    """
    Create the argument parser.
    """
    cmd = argparse.ArgumentParser(description=intro,
                                  epilog="SFT dynamic DNS updater HTTPS server")
    cmd.add_argument("conffile", type=str, nargs="?",
                     default="/etc/sftdyn/conf",
                     help="conf file, will be exec'd as python3")
    cmd.add_argument("-l", "--http", metavar="IP:PORT",
                     help="Enable HTTP server")
    cmd.add_argument("-s", "--https", metavar="IP:PORT",
                     help="Enable HTTPS server")
    cmd.add_argument("-c", "--cert", type=str, help="HTTPS X.509 cert file")
    cmd.add_argument("-k", "--key", type=str, help="HTTPS X.509 key file")
    cmd.add_argument("-i", "--interactive", action="store_true",
                     help="launch a interactive session")
    cmd.add_argument("--nsupdatecommand", type=str,
                     default=("update delete <host> A\n"
                              "update add <host> 30 A <ip>\n"
                              "send\n"),
                     help="template command list for nsupdate")

    cmd.add_argument("-d", "--debug", action="store_true",
                     help="enable asyncio debugging")
    cmd.add_argument("-v", "--verbose", action="count", default=0,
                     help="increase program verbosity")
    cmd.add_argument("-q", "--quiet", action="count", default=0,
                     help="decrease program verbosity")

    return cmd


def stringtoipport(txt):
    """
    splits an IP:PORT string, as expected for --http and --https

    txt
        input string, either PORT or I.P.AD.DR:PORT
    returns
        (ip, port) where ip is a string and port is an int
    """
    if type(txt) == int:
        return "0.0.0.0", txt

    if not txt.count(':'):
        return "0.0.0.0", int(txt)
    else:
        ipraw, port = txt.split(':')
        ip = ipaddress.ip_address(ipraw)
        return str(ip), int(port)


def parse_args(intro):
    """
    Parses the args, and returns the namespace.
    The config file is evaluated after the args and may replace its values.

    intro: info text displayed as program description.
    """
    cmd = get_parser(intro)
    args = cmd.parse_args()

    # read the conffile
    if not os.path.isfile(args.conffile):
        cmd.error("Not a valid conf file: " + args.conffile)

    # execute the file so globals defined in it are added to args
    exec(open(args.conffile).read(), vars(args))

    if not args.clients:
        cmd.error("config file does not declare the clients dict")

    # check https IP:PORT string
    if args.https:
        try:
            args.https = stringtoipport(args.https)
        except ValueError:
            cmd.error("Invalid [IP:]PORT for --https: " + args.https)

    # check http IP:PORT string
    if args.http:
        try:
            args.http = stringtoipport(args.http)
        except ValueError:
            cmd.error("Invalid [IP:]PORT for --http: " + args.http)

    # check cert/key
    if args.https or args.cert or args.key:
        if not (args.https and args.cert and args.key):
            cmd.error("--https, --cert and --key need to be used together")

        conffolder = Path(args.conffile).parent
        # make cert paths relative to the conf file
        if not Path(args.cert).is_absolute():
            args.cert = str(conffolder / args.cert)

        if not Path(args.key).is_absolute():
            args.key = str(conffolder / args.key)


    return args
