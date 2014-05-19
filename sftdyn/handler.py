from http.server import BaseHTTPRequestHandler
from sftdyn.nsupdater import handle_request

class GetHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()

        requestkey = self.path.lstrip('/')
        if handle_request(requestkey, self.client_address[0]):
            self.wfile.write(b"OK")
        else:
            self.wfile.write(b"FAIL")
