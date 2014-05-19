import argparse

p = argparse.ArgumentParser(description="SFT dynamic DNS updater HTTPS server")
p.add_argument("-v", "--verbose", action='count', default=0)
p.add_argument("-c", "--cert", type=str,
    help="X.509 cert file")
p.add_argument("-k", "--key", type=str,
    help="X.509 key file")
p.add_argument("-p", "--port", type=int, default=4443)
p.add_argument("-l", "--listen", type=str, default="0.0.0.0")
p.add_argument("--conf", type=str,
    help="conf file, will be exec'd as python3, with args as global()")
p.add_argument("client", type=str, nargs='*',
    help="tuples of the form clientid:domainname")

def parse():
    args = p.parse_args().__dict__
    globals().update(args)

    global clients
    clients = {}
    for c in client:
        ckey, cdns = c.split(':', maxsplit=1)
        clients[ckey] = cdns

    if conf:
        exec(open(conf).read(), globals())
    if not cert or not key:
        p.error("You must provide key and cert files")
