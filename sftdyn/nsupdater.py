import sftdyn.args as args
from subprocess import Popen, PIPE

def handle_request(ckey, ip):
    if ckey not in args.clients:
        print("Illegal key from " + ip)
        return False

    print("Updating " + args.clients[ckey] + " to " + ip)

    s = args.nsupdatecommand
    s = s.replace('$HOST', args.clients[ckey])
    s = s.replace('$IP', ip)
    s = s.replace('$ZONE', args.zone)

    p = Popen(['nsupdate', '-l'], stdin=PIPE)
    p.communicate(input=s.encode('utf-8'))

    return p.returncode is 0
