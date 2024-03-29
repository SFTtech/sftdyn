# sftdyn dynamic dns server

`sftdyn` is a minimalistic dynamic DNS server that accepts update requests via `http` or `https` and forwards them to a locally running DNS server via `nsupdate -l`.
You can use it to easily update IPs of hosts in a domain whose IPs are not static and change to unpredictable addresses.

It lets you easily create a dyndns.org-like service, using your own DNS server, and can (probably) be used with your router at home.

## Operation

* You have a domain, e.g. `sft.rofl`, and a subdomain for dynamic entries, e.g. `dyn.sft.rofl`
* The device whose IP address you want to store submits a https request to the `sftdyn` server containing a secret token, in order to update `devicename.dyn.sft.rofl`
* From this, the `sftdyn` server knows the request origin IP
* From the secret token, `sftdyn` can associate a hostname to update its DNS record (`devicename.dyn.sft.rofl`)
* The request therfore updated an IP in your zone


## Requirements

* [Python >=3.5](https://www.python.org/)
* [`aiohttp`](https://aiohttp.readthedocs.io/)


## Setup Guide

`sftdyn` is for you if you host a DNS zone and can run a Python server so it updates the nameserver records.
This guide assumes that you're using [BIND](https://en.wikipedia.org/wiki/BIND), your zone is `dyn.sft.rofl`, and your server's IP is `12.345.678.90`.
Substitute the correct values for zone and IP as you use this guide.


### Nameserver

`bind` has to be configured to serve the updatable zone.

You probably have a zonefile for `sft.rofl` already.
You need to delegate `dyn.sft.rofl` to the local nameserver.

In the `sft.rofl` zone, add `NS records` to the new dynamic zone we're about to create:

```
# so the dyn.sft.rofl zone is delegated to the nameserver running sftdyn.
# likely you need the same NS record as for the sft.rofl zone itself.
dyn 30m IN NS yournameserver's_a_record
```

Now let's create the `dyn.sft.rofl` zone, where all the dynamic records will live.
Somewhere in `named.conf`, add the new dynamic zone:

```
zone "dyn.sft.rofl" IN {
    type master;
    file "/etc/bind/dyn.sft.rofl.zone";
    journal "/var/cache/bind/dyn.sft.rofl.zone.jnl";
    update-policy local;
};
```

`/var/cache/bind` and `/etc/bind/dyn.sft.rofl.zone` must be writable for *bind*.

Create the empty zone file

```
cp /etc/bind/db.empty /etc/bind/dyn.sft.rofl.zone
```

We also can define a hostname to send the IP update requests to within the `dyn.sft.rofl` zone, or even use `dyn.sft.rofl` itself.
`@` means the zone name itself.

```
# within the dyn.sft.rofl zonefile, we set the IP for the dyn.sft.rofl host itself.
# this is the ip of the nameserver itself, where sftdyn is running.
# -> you can then send update requests to https://dyn.sft.rofl/...
@ 10m IN A 12.345.678.90
@ 10m IN AAAA some:ipv6::address
```


### sftdyn server setup

To install *sftdyn*, use `pip install sftdyn` or `./setup.py install`.

Launch it with `python3 -m sftdyn [command-line options]`.

Configuration is by command-line parameters and conf file.
A sample conf file is provided in `etc/sample.conf`.
If no conf file name is provided, `/etc/sftdyn/conf` is used.
Hostnames/update keys are specified in the conf file.

`sftdyn` _should_ run under the same user as your DNS server, or it _might_
not be able to update it properly. Alternatively, to run sftdyn as the user of
your choice, see Advanced setup later in this article.


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

##### Reverse proxy

Your server running `sftdyn` may already have a webserver (e.g. nginx) to handle other web requests.
It may already have proper certificates setup (e.g. with letsencrypt) - which you can just reuse for sftdyn.

If you have `nginx`, the following config block will redirect requests to `dyn.sft.rofl` to the `sftdyn` server.

Remember to use the `X-Forwarded-For` header in the `sftdyn` config (in `get_ip`) as the client ip!

```nginx
server {
    server_name dyn.sft.rofl;

    // ...

    location / {
        # with this line, nginx relays the request to sftdyn
        proxy_pass http://localhost:8080/;

        # remember the original ip - we need to extract it in get_ip
        # in the sftdyn config then!
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header Host            $host;
    }

    // ...
}
```

Alternatively, you can add the location block with `location /dyn` or something to some existing server block.

In any way, you can then submit requests to the regular https port since you send to nginx now.
-> remove `:4443` in the client requests.


##### Let's Encrypt

If you don't want to use a reverse proxy to terminate the tls connection, you can directly configure `sftdyn` to use the certificate.
To use a certificate by [Let's Encrypt](https://letsencrypt.org/) directly in `sftdyn`:

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

The client is the device whose IP we want to update in the dynamic zone.
Common clients are your plastic router at home that changes it's DSL IP address from time to time.

The client triggers the IP update at the `sftdyn` server, so your DNS then delivers the correct IP.

#### Plastic router

Cheap plastic routers often have built-in dynamic dns update support.
Since `sftdyn` is not that well known, within the plastic router's web UI you need to select something like _user-defined provider_, and enter http://dyn.sft.rofl:8080/yourupdatekey as the update URL.
Write random stuff as name/user name/password, since just the update URL is the secret alone (tested with my AVM Fritz!Box. YMMV).
Most routers don't support HTTPS update requests (especially not with custom CA-cert, so you'll probably need HTTP.

If you set up `sftdyn` with let's encrypt, https may work - just test it :)

#### Request with `curl`

If you want to update the external IP of some NAT gateway (like home router, ...), and you have a machine in that network which can use `curl`, choose this client method.

If you use HTTPS with a let's encrypt certificate, `curl` will be happy to request with encryption

If you use a self-signed certificate, `curl` will refuse to talk to the server (because it obviously can't trust it without knowing it).
To make `curl` trust the self-signed certificate:
 - Copy `server.crt` to the client, and use `curl --cacert server.crt`.
Alternatively, to let `curl` ignore the security problem and just accept whatever it gets:
 - Use `curl -k` to ignore the error (Warning: see the security considerations below).

The result codes mean the following:

| HTTP code     | Text          | Response interpretation                         |
| ------------- | ------------- | ----------------------------------------------- |
| 200           | OK            | Update successful                               |
| 200           | UPTODATE      | Update unneccesary                              |
| 403           | BADKEY        | Unknown update key                              |
| 500           | FAIL          | Internal error (see the server log)             |
| 200           | _your ip_     | Returned if no association key is provided      |

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
ExecStart=/usr/bin/env curl -f -s --cacert /path/to/server.crt https://dyn.sft.rofl:4443/yoursecretupdatekey
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
*/10 * * * * curl https://dyn.sft.rofl:4443/mysecretupdatekey
```


### Advanced setup

#### Pre-generated keyfile

By default sftdyn uses a key auto-generated by bind, `/var/run/named/session.key`.
The permissions of this file may be reset on startup, and could be too
restrictive for sftdyn.

If you see errors such as these in `journalctl -u sftdyn`, it may indicate a
permission issue with the keyfile:
```
; TSIG error with server: tsig indicates error
update failed: NOTAUTH(BADSIG)
```

An alternative approach is to use a pre-generated keyfile dedicated to sftdyn,
which lets you have more control over the file permissions.

##### Create a new key

The example script below generates a keyfile in `/etc/bind/keys/sftdyn.key`,
and changes the user/group ownership to `bind:sftdyn`. Modify as needed to
best suit your specific setup.

```sh
b=$(dnssec-keygen -a hmac-sha512 -b 512 -n USER -K /tmp foo)
cat > /etc/bind/keys/sftdyn.key <<EOF
key "sftdyn" {
    algorithm hmac-sha512;
    secret "$(awk '/^Key/{print $2}' /tmp/$b.private)";
};
EOF
rm -f /tmp/$b.{private,key}
chown bind:sftdyn /etc/bind/keys/sftdyn.key # or whatever permissions
chmod 640 /etc/bind/keys/sftdyn.key
```

##### Include the key in named.conf

```
include "/etc/bind/keys/sftdyn.key";
```

##### Configure named zone to use the key

```
zone "dyn.sft.mx" IN {
    type master;
    file "/etc/bind/dyn.sft.mx.zone";
    journal "/var/cache/bind/dyn.sft.mx.zone.jnl";
    allow-update { key "sftdyn"; };
};
```

##### Change sftdyn configuration to use the key

Edit the nskeyfile option in the configuration file, by default located in
`/etc/sftdyn/conf`:

```
nskeyfile = "/etc/bind/keys/sftdyn.key"
```

## About

This software was written after the free `dyndns.org` service was shut down.
After a week or so of using plain `nsupdate`, we were annoyed enough to decide to write this.

The main goal of this tool is to stay as minimal as possible; for example, we deliberately didn't implement a way to specify the hostname or IP that you want to update; just a simple secret update key is perfectly good for the intended purpose.
If you feel like it, you can make the update key look like a more complex request; every character is allowed.
Example: `host=test.sft.rofl,key=90bbd8698198ea76`.

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

- Matrix: [`#sfttech:matrix.org`](https://matrix.to/#/#sfttech:matrix.org)


The license is GNU GPLv3 or higher.
