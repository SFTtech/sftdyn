"""
http(s) server implementation for sftdyn.
"""


import ssl
import asyncio

from logging import info
from aiohttp import web


class Server:
    """
    HTTP(S) server for DNS record update requests.
    """

    def __init__(self, addr, clients, associations, nsupdatecommands, tls=None):
        """
        addr: (ip, port) to listen on
        clients: {dnsclient: dnshostname} map of allowed clients
        associations: {dnshostname: ipaddr} map to cache current dynamic ips
        nsupdatecommands: function to generate the `nsupdate` stdin,
                          will be called with `host` and `new_ip` args.
        tls: (cerfilename, keyfilename) to use for the tls socket
        """

        self.addr = addr
        self.clients = clients
        self.associations = associations
        self.nsupdatecommands = nsupdatecommands

        if tls:
            # create SSLContext for our TLS server
            self.sslcontext = ssl.create_default_context(
                purpose=ssl.Purpose.CLIENT_AUTH
            )
            self.sslcontext.load_cert_chain(tls[0], tls[1])
        else:
            self.sslcontext = None

    async def listen(self, loop):
        """
        Let the server listen on the given event loop.
        """

        server = web.Server(self.handler)
        await loop.create_server(
            server,
            self.addr[0],
            self.addr[1],
            ssl=self.sslcontext
        )

    async def handler(self, request):
        """
        Handler for a single request.
        """

        if request.method != "GET":
            return web.Response(status=405)

        path = request.path_qs.lstrip('/')
        peername = request.transport.get_extra_info('peername')
        if peername is None:
            return web.Response(status=500)

        addr = peername[0]
        text, code = await self.handle_request(path, addr, request.headers)

        return web.Response(text=text, status=code)

    async def handle_request(self, key, ip, headers=None):
        """
        the actual application-specific code

        key
            the path part of the client request URL, without the leading '/'
        ip
            the IP address of the client

        returns
            (status, httpcode) after examining the key
        """

        if not key:
            return ip, 200

        try:
            host = self.clients[key]
        except KeyError:
            return "BADKEY", 403

        if self.associations.get(host, None) == ip:
            return "UPTODATE", 200

        info("update request for %s => %s" % (host, ip))

        if not headers:
            headers = dict()

        # call to user-defined function
        cmdlist = self.nsupdatecommands(host, ip, headers)

        iter(cmdlist)  # check if the generated updatecommand is iterable
        cmd = "\n".join(cmdlist) + "\n"

        proc = await asyncio.create_subprocess_exec(
            'nsupdate', '-l',
            stdin=asyncio.subprocess.PIPE
        )
        proc.stdin.write(cmd.encode())
        proc.stdin.close()
        await proc.wait()

        if proc.returncode == 0:
            self.associations[host] = ip
            return "OK", 200

        return "FAIL", 500
