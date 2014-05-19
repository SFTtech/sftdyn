import sftdyn.args as args

def handle_request(ckey, ip):
    if ckey not in args.clients:
        print("Illegal key from " + ip)
        return False

    print("Updating " + args.clients[ckey] + " to " + ip)
    return True
