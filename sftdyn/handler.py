from http.server import BaseHTTPRequestHandler
from sftdyn.nsupdater import handle_request

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
