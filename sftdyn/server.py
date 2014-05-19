import sftdyn.args as args
from sftdyn.handler import GetHandler
import http
import ssl

def serve():
    addr = (args.listen, args.port)
    httpd = http.server.HTTPServer(addr, GetHandler)
    httpd.socket = ssl.wrap_socket(
        httpd.socket,
        server_side=True,
        keyfile=args.key,
        certfile=args.cert,
        ssl_version=ssl.PROTOCOL_TLSv1_2)
    print("listening on " + args.listen + ":" + str(args.port))
    httpd.serve_forever()
