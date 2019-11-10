# sftdyn dynamic dns server

`sftdyn` is a minimalistic dynamic DNS server that accepts update requests via HTTP(S) and forwards them to a locally running DNS server via `nsupdate -l`.

It lets you easily create a dyndns.org-like service, using your own DNS server, and can (probably) be used with your router.

## Operation

* Some device submits a https request to a "secret URL" of `sftdyn`
* From this, `sftdyn` knows the request origin IP
* From the "secret URL", `sftdyn` updates the DNS record of the associated hostname
* The request therfore updated an IP in your zone


## Requirements

* [Python >=3.5](https://www.python.org/)
* [`aiohttp`](https://aiohttp.readthedocs.io/)


## Quick Guide

`sftdyn` is for you if you host a DNS zone and can run a Python server so it updates the nameserver records.
This guide assumes that you're using [BIND](https://en.wikipedia.org/wiki/BIND), your zone is `dyn.sft.mx`, and your server's IP is `12.345.678.90`.
Substitute the correct values for zone and IP as you use this guide.


### Nameserver

`bind` has to be configured to serve the updatable zone.

Somewhere in `named.conf`, add

```
zone "dyn.sft.mx" IN {
    type master;
    file "/etc/bind/dyn.sft.mx.zone";
    journal "/var/cache/bind/dyn.sft.mx.zone.jnl";
    update-policy local;
};
```

`/var/cache/bind` and `/etc/bind/dyn.sft.mx.zone` must be writable for *bind*.

Create the empty zone file

```
cp /etc/bind/db.empty /etc/bind/dyn.sft.mx.zone
```

If you want to use `dyn.sft.mx` as the hostname for the server that gets IP update requests later, add a record to the zone file (this requires the `sftdyn`-server to have this static IP, `@` means the zone name itself).

```
@ 10m IN A 12.345.678.90
@ 10m IN AAAA some:ipv6::address
```


### sftdyn

To install *sftdyn*, use `pip install sftdyn` or `./setup.py install`.

Launch it with `python3 -m sftdyn [command-line options]`.

Configuration is by command-line parameters and conf file.
A sample conf file is provided in `etc/sample.conf`.
If no conf file name is provided, `/etc/sftdyn/conf` is used.
Hostnames/update keys are specified in the conf file.

`sftdyn` _should_ run under the same user as your DNS server, or it _might_ not be able to update it properly.


#### systemd service

To run `sftdyn` automatically, you can use a systemd service.

The `sftdyn` distribution package should automatically install `sftdyn.service`.

If you have to manually install it, use the example unit `etc/sftdyn.service`
and copy it to `/etc/systemd/system/sftdyn.service` on the `sftdyn` host machine.

Enable the launch on boot and also start `sftdyn` now:

```
sudo systemctl enable --now sftdyn.service
```

#### Unencrypted operation

You _can_ use `sftdyn` in plain HTTP mode.
Your average commercial dynamic DNS provider provides a HTTP interface, so most routers only support that.

Somebody could grab your "secret url" with this and perform unintended updates of your record.


#### Encrypted operation

Because of the above reason, you _should_ use HTTPS to keep your update url token secret.
For that, your server needs a X.509 key and certificate.
You can create those with [let's encrypt](https://letsencrypt.org/), buy those somewhere, or create a self-signed one.


##### Let's Encrypt

If you got a certificate by [Let's Encrypt](https://letsencrypt.org/), configure `sftdyn` to use it:

```
# in sftdyn.conf:
key = "/etc/letsencrypt/live/host.name.lol/privkey.pem"
cert = "/etc/letsencrypt/live/host.name.lol/fullchain.pem"
```

Make sure the certificate is valid for the domain your `sftdyn` is getting requests for.

A `https` request to `sftdyn` to update an IP will then be secure™ (e.g. with `curl`).


##### Self-signed certificate

To generate `server.key` and a self-signed `server.crt` valid for 1337 days:

```
openssl genrsa -out server.key 4096
openssl req -new -key server.key -out server.csr
openssl x509 -req -days 1337 -in server.csr -signkey server.key -out server.crt
rm server.csr
```

Make sure you enter your server's domain name for _Common Name_ (the hostname you'll use for querying `sftdyn` with clients.

A `https` request to `sftdyn` to update an IP will then be more secure™ than a globally valid certificate like from Let's Encrypt, but you'll need to transfer the `server.crt` to the device performing the request (e.g. with `curl`).


### Client

The client triggers the IP update at the `sftdyn` server, so your DNS then delivers the correct IP.

#### Plastic router

To use your cheap plastic router as client, select _user-defined provider_, enter http://dyn.sft.mx:8080/yourupdatekey as the update URL, and random stuff as domain name/user name/password (tested with my AVM Fritz!Box. YMMV).
Most routers don't support HTTPS update requests (especially not with custom CA-cert, so you'll probably need HTTP.

#### Request with `curl`

If you want to update the external IP of some NAT gateway (like home router, ...), and you have a machine in that network which can use `curl`, choose this client method.

If you use HTTPS with a self-signed certificate, `curl` will refuse to talk to the server.
 - Use `curl -k` to ignore the error (Warning: see the security considerations below).
 - Copy `server.crt` to the client, and use `curl --cacert server.crt`.

| HTTP code     | Text          | Response interpretation             |
| ------------- | ------------- | ----------------------------------- |
| 200           | OK            | Update successful                   |
| 200           | UPTODATE      | Update unneccesary                  |
| 403           | BADKEY        | Unknown update key                  |
| 500           | FAIL          | Internal error (see the server log) |
| 200           | _your ip_     | Returned if no key is provided      |

##### systemd timer

`systemd` timers are like cronjobs. Use them to periodically run the update query.

Create `/etc/systemd/system/sftdynupdate.timer`:
```
[Unit]
Description=SFTdyn dns updater

[Timer]
OnCalendar=*:0/15
Persistent=true

[Install]
WantedBy=timers.target
```

Create `/etc/systemd/system/sftdynupdate.service`:
```
[Unit]
Description=SFTdyn name update

[Service]
Type=oneshot
User=nobody
ExecStart=/usr/bin/env curl -f -s --cacert /path/to/server.crt https://dyn.sft.mx:4443/yoursecretupdatekey
```

Activate the timer firing with:

```
sudo systemctl enable --now sftdyn.timer
```

Verify the timer is scheduled:

```
sudo systemctl list-timers
```

To manually trigger the update (e.g. for testing purposes):

```
sudo systemctl start sftdyn.service
```

##### Cronjob

Cronjobs are the legacy variant to periodically run a task, you could do this like this:

```
*/10 * * * * curl https://dyn.sft.mx:4443/mysecretupdatekey
```


## About

This software was written after the free `dyndns.org` service was shut down.
After a week or so of using plain `nsupdate`, we were annoyed enough to decide to write this.

The main goal of this tool is to stay as minimal as possible; for example, we deliberately didn't implement a way to specify the hostname or IP that you want to update; just a simple secret update key is perfectly good for the intended purpose.
If you feel like it, you can make the update key look like a more complex request; every character is allowed.
Example: `host=test.sft.mx,key=90bbd8698198ea76`.

The conf file is interpreted as python code, so you can do arbitrarily complex stuff there.

## Security considerations

- When using HTTP, or if your `server.key` has been stolen or broken, an eavesdropper can steal your update key, and use that to steal your domain name.
- When using HTTPS with `curl -k`, a man-in-the-middle can steal your update key.
- When using HTTPS with a paid certificate, a man-in-the-middle with access to a CA can steal your update key (no problem for government agencies, but this is pretty unlikely to happen).
- When using HTTPS with a self-signed certificate and `curl --cacert server.crt`, no man-in-the-middle can steal your update key.

`sftdyn` is pretty minimalistic, and written in python, so it's unlikely to contain any security vulnerabilities. The python ssl and http modules are used widely, and open-source, so there _should_ be no security vulnerabilities there.

Somebody who knows a valid udpate key could semi-effectively DOS your server by spamming update requests from two different IPs. For each request, nsupdate would be launched and your zone file updated.

## Development

For us, the project is feature-complete, it has everything that **we** currently need.
If you actually _did_ implement a useful feature, please send a pull request; We'd be happy to merge it.

If you have any **requests**, **ideas**, **feedback** or **bug reports**,
are simply **filled with pure hatred**,
or just **need help** getting the damn thing to run,
join our chatroom and just ask:

- Matrix: [`#sfttech:matrix.org`](https://riot.im/app/#/room/#sfttech:matrix.org)
- IRC: [`irc.freenode.net #sfttech`](https://webchat.freenode.net/?channels=sfttech)


The license is GNU GPLv3 or higher.
