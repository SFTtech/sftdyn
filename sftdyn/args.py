import argparse
import os

p = argparse.ArgumentParser(description="SFT dynamic DNS updater HTTPS server")
p.add_argument("conffile", type=str, nargs="?", default="/etc/sftdyn/conf",
               help="conf file, will be exec'd as python3")
p.add_argument("-l", "--http", metavar="IP:PORT", help="Enable HTTP server")
p.add_argument("-s", "--https", metavar="IP:PORT", help="Enable HTTPS server")
p.add_argument("-c", "--cert", type=str, help="HTTPS X.509 cert file")
p.add_argument("-k", "--key", type=str, help="HTTPS X.509 key file")
p.add_argument("--nsupdatecommand", type=str,
               default="update delete <host> A\n" +
                       "update add <host> 30 A <ip>\n" +
                       "send\n",
               help="template command list for nsupdate")

def stringtoipport(s):
    """
    splits an IP:PORT string, as expected for --http and --https

    s
        input string, either PORT or I.P.AD.DR:PORT
    returns
        (ip, port) where ip is a string and port is an int
    """
    if type(s) == int:
        return "0.0.0.0", s

    if not s.count(':'):
        return "0.0.0.0", int(s)
    else:
        ip, port = s.split(':')
        assert ip.count('.') == 3
        assert all(0 <= int(x) < 256 for x in ip.split('.'))
        return ip, int(port)

def parse():
    """
    parses the args, and returns the namespace.
    """
    args = p.parse_args()

    # read the conffile
    if not os.path.isfile(args.conffile):
        p.error("Not a valid conf file: " + args.conffile)

    exec(open(args.conffile).read(), vars(args))

    # check https IP:PORT string
    if args.https:
        try:
            args.https = stringtoipport(args.https)
        except:
            p.error("Invalid [IP:]PORT for --https: " + args.https)

    # check http IP:PORT string
    if args.http:
        try:
            args.http = stringtoipport(args.http)
        except:
            p.error("Invalid [IP:]PORT for --http: " + args.http)

    # check cert/key
    if args.https or args.cert or args.key:
        if not args.https or not args.cert or not args.key:
            p.error("--https, --cert and --key need to be used together")

    return args
