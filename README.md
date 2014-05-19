sftdyn is a minimalistic (< 100 lines!) python script that lets you easily create a dyndns.org-like service, using your own DNS server.

# Quick Guide

### Nameserver
Somewhere in `named.conf`, add

    zone "dyn.sft.mx" IN {
        type master;
        file "/etc/bind/dyn.sft.mx.zone";
        journal "/var/cache/bind/dyn.sft.mx.zone.jnl";
        update-policy local;
    };

`/var/cache/bind` must be writable for *bind*.

Create the empty zone file

    cp /etc/bind/db.empty /etc/bind/dyn.sft.mx.zone

If you want to use `dyn.sft.mx` as the hostname for your update requests, add a record to the zone file:

    IN A 12.345.678.901

### sftdyn
To install *sftdyn*, use `./setup.py install`. You can then launch it via `sftdyn [command-line options]`.
You can pass all info to `sftdyn` via command-line options, or use `--conf=file.cfg` to load them from a file. A sample conf file is provided in `sample.conf`.

In the conf file, you **must** specify
 - key (server.key)
 - cert (server.crt)
 - zone (dyn.sft.mx)
 - a list of clients

sftdyn relies on HTTPs for security, so you need a certificate/key. You can buy one from your DNS provider, or create a self-signed one; both have their benefit.

Quick and dirty options to create self-signed `server.key` and `server.crt`:

    openssl genrsa -des3 -out server.key 4096
    openssl req -new -key server.key -out server.csr
    cp server.key server.key.org
    openssl rsa -in server.key.org -out server.key
    openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt
    rm server.csr

Add clients to the conf file like this:

    clients["mysupersecretupdatekey"]="test.dyn.sft.mx"

sftdyn should run under the same user as your DNS server.

### Client
Just set up a cronjob that talks to sftdyn every few minutes:

    /10 * * * * curl https://dyn.sft.mx:4443/mysecretupdatekey

The curl command will return `OK` on success, and `FAIL` on error (such as wrong password). To resolve errors, take a look at sftdyn command-line output.

The default server port is 4443; you can change this in the conf file.

If your certificate was self-signed, curl will refuse to talk to the server.
 - Quick 'n dirty: Use `curl -k` to ignore the warning. MITM attackers could steal your update key that way.
 - Clean: Copy `server.crt` to the client, and use `curl --cacert=server.crt`. This is even more secure  than a paid certificate.

# About
I wrote this script after the free dyndns.org service was shut down. First, I tried using nsupdate manually, but that's getting annoying really fast, so I decided to build this.

I chose HTTPs for security purposes; with the plain HTTP protocols of major dynamic dns providers, anybody who sniffs on your connection can hijack your domain name. With the HTTPs security layer of sftdyn, that's not possible anymore.

It is the main goal to stay as minimal as possible; for example, I deliberately didn't implement a way to specify the hostname or IP that you want to update; just a simple secret update key is perfectly good for the intended purpose of this project.

If you want to, you can make the update key look like an actual more complex request; everything except a colon or \0 is allowed. Example key format: `?host=test.sft.mx&key=90bbd8698198ea76`.

The conf file is actually python, and is executed as such when loaded, so you can put arbitrarily complex stuff there; for example, you could assemble the clients directory from some external information source. You could even make it into some complex class that dynamically does... stuff... whatever. have fun.

# Development
IMHO, the project is feature-complete; it has everything that **I** currently want.

Features that might be useful includes:
 - A plain HTTP version for our less ~~paranoid~~ security-aware fellows
 - A version that is supported by common router's dynamic DNS feature
 - I'm sure there is more

If you want to give me your requests, feedback, bug reports, piles of money or just pure hatred, join `irc.freenode.net/#sfttech` (I'm mic_e).

If you actually _did_ implement a useful feature in a sufficiently non-bloaty way, please send a pull request.

The license is `GNU GPLv3+`.
