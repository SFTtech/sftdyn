#!/usr/bin/env python3
from distutils.core import setup
from sftdyn import VERSION

setup(
    name="sftdyn",
    version=VERSION,
    description="HTTPs-based DDNS updater",
    long_description="dyndns-like service that accepts update requests " +
                     "via HTTPs and forwards them to a locally running DNS " +
                     "server via nsupdate -l",
    author="Michael Enßlin",
    author_email="michael@ensslin.cc",
    url="https://github.com/SFTtech/sftdyn",
    license="GPLv3 or higher",
    packages=["sftdyn"],
    scripts=["bin/sftdyn"],
    data_files=[("/etc/sftdyn/", ["sample.conf"])]
)
