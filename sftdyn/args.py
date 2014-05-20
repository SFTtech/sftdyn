import argparse
import os

p = argparse.ArgumentParser(description="SFT dynamic DNS updater HTTPS server")
p.add_argument("-c", "--cert", type=str,
               help="X.509 cert file")
p.add_argument("-k", "--key", type=str,
               help="X.509 key file")
p.add_argument("conffile", type=str, nargs="?", default="/etc/sftdyn/conf",
               help="conf file, will be exec'd as python3")
p.add_argument("-p", "--port", type=int, default=4443)
p.add_argument("-l", "--listen", type=str, default="0.0.0.0")
p.add_argument("--nsupdatecommand", type=str,
               default="update delete $HOST A\n" +
                       "update add $HOST 30 A $IP\n" +
                       "send\n",
               help="template command list for nsupdate")


def parse():
    args = p.parse_args()
    args.clients = {}

    if not os.path.isfile(args.conffile):
        p.error("Not a valid conf file: " + args.conf)

    exec(open(args.conffile).read(), args.__dict__)

    if not args.cert or not args.key:
        p.error("You must provide key and cert files")

    return args
