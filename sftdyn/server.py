import http
import ssl
import threading
from http.server import BaseHTTPRequestHandler
from subprocess import Popen, PIPE

currentips = {}
lock = threading.Lock()


def handle_request(key, ip):
    """
    the actual application-specific code

    key
        the path part of the client request URL, without the leading '/'
    ip
        the IP address of the client
    """

    if not key:
        return ip, 200

    try:
        host = clients[key]
    except:
        return "BADKEY", 403

    if currentips.get(host, None) == ip:
        return "UPTODATE", 200

    print("updating " + host + " to " + ip)

    p = Popen(['nsupdate', '-l'], stdin=PIPE)
    cmd = nsupdatecommand.replace('<host>', host).replace('<ip>', ip)
    p.communicate(input=cmd.encode('utf-8'))

    if p.returncode == 0:
        currentips[host] = ip
        return "OK", 200
    else:
        return "FAIL", 500


class GetHandler(BaseHTTPRequestHandler):
    """
    used by all Server objects to handle GET requests
    """

    def do_GET(self):
        path = self.path.lstrip('/')

        # wheee, thread-safety!
        with lock:
            text, code = handle_request(path, self.client_address[0])

        self.send_response(code)
        self.end_headers()
        self.wfile.write(text.encode('utf-8'))


class Server(threading.Thread):
    """
    single HTTP(S) server class

    use start() to run in a thread.
    """

    def __init__(self, addr, use_ssl=None):
        """
        opens the socket and creates the HTTPServer.

        addr
            (ip, port) listening address
        ssl
            if not None, must be a (key, cert) tuple
        """
        super().__init__()

        # clean thread termination would seriously not be worth the effort.
        # hundreds of man-years have been wasted on simply making threaded
        # programs shutdown 'cleanly', while fractions of seconds later
        # the kernel would have cleaned up their remains anyway.
        # in our case, because program termination requires the lock,
        # the only ressource held by the thread is its socket.
        # if you _really_ want to waste time on this, go for it; I'll pull it.
        self.daemon = True

        self.httpd = http.server.HTTPServer(addr, GetHandler)

        if use_ssl:
            self.httpd.socket = ssl.wrap_socket(
                self.httpd.socket,
                server_side=True,
                keyfile=use_ssl[0],
                certfile=use_ssl[1],
                ssl_version=ssl.PROTOCOL_TLSv1)

    def run(self):
        self.httpd.serve_forever()
