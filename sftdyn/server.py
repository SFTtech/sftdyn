import sftdyn.args as args
import http
import ssl
from http.server import BaseHTTPRequestHandler
from sftdyn.handler import handle_request

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
