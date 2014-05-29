import sftdyn
import sftdyn.args as args
import sftdyn.server as server
import sftdyn.interactivesession as interactivesession

args = args.parse()

server.clients = args.clients
server.nsupdatecommand = args.nsupdatecommand

if args.http:
    httpserver = server.Server(args.http)
    print("running http server at " + args.http[0] + ':' +
            str(args.http[1]))
    httpserver.start()

if args.https:
    httpsserver = server.Server(args.https, (args.key, args.cert))
    print("running https server at " + args.https[0] + ':' +
            str(args.https[1]))
    httpsserver.start()

interactivesession.interact(server.lock, globals(), "sftdyn " + sftdyn.VERSION)

#terminate semi-cleanly (wait until no server is serving a client)
with server.lock:
    exit(0)
