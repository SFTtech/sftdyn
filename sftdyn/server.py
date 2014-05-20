import sftdyn.args as args
import http
import ssl
from http.server import BaseHTTPRequestHandler
from subprocess import Popen, PIPE

currentips = {}


def handle_request(key, ip):
    if not key:
        return ip, 200

    try:
        host = args.clients[ckey]
    except:
        return "BADKEY", 403

    if currentips.get(host, None) is ip:
        return "UPTODATE", 200

    print("updating " + host + " to " + ip)

    p = Popen(['nsupdate', '-l'], stdin=PIPE)
    cmd = args.nsupdatecommand.replace('$HOST', host).replace('$IP', ip)
    p.communicate(input=cmd.encode('utf-8'))

    if p.returncode is 0:
        currentips[host] = ip
        return "OK", 200
    else:
        return "FAIL", 500


class GetHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.lstrip('/')
        text, code = handle_request(path, self.client_address[0])
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
