import argparse

p = argparse.ArgumentParser(description="SFT dynamic DNS updater HTTPS server")
p.add_argument("-v", "--verbose", action='count', default=0)
p.add_argument("-c", "--cert", type=str,
               help="X.509 cert file")
p.add_argument("-k", "--key", type=str,
               help="X.509 key file")
p.add_argument("client", type=str, nargs='*',
               help="clientkey:hostname tuples")
p.add_argument("-p", "--port", type=int, default=4443)
p.add_argument("-l", "--listen", type=str, default="0.0.0.0")
p.add_argument("--conf", type=str,
               help="conf file, will be exec'd as python3")
p.add_argument("--nsupdatecommand", type=str,
               default="update delete $HOST A\nupdate add $HOST 30 A $IP\nsend\n",
               help="template command list for nsupdate")


def parse():
    args = p.parse_args()

    args.clients = [c.split(':', maxsplit=1) for c in args.client]
    args.clients = {ckey: chost for ckey, chost in args.clients}
    del args.client

    if args.conf:
        exec(open(args.conf).read(), args.__dict__)
    if not args.cert or not args.key:
        p.error("You must provide key and cert files")

    return args
