import sftdyn.args as args
import http
import ssl
from http.server import BaseHTTPRequestHandler
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

class GetHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        requestkey = self.path.lstrip('/')
        if handle_request(requestkey, self.client_address[0]):
            text, code = "OK", 200
        else:
            text, code = "FAIL", 403

        self.send_response(code)
        self.end_headers()
        self.wfile.write(text.encode('utf-8'))

def serve():
    addr = (args.listen, args.port)
    httpd = http.server.HTTPServer(addr, GetHandler)
    httpd.socket = ssl.wrap_socket(
        httpd.socket,
        server_side=True,
        keyfile=args.key,
        certfile=args.cert,
        ssl_version=ssl.PROTOCOL_TLSv1)
    print("listening on " + args.listen + ":" + str(args.port))
    httpd.serve_forever()
