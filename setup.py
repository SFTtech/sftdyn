#!/usr/bin/env python3
from distutils.core import setup
from sftdyn import VERSION
from sys import version_info

if version_info[0] < 3:
    print("use python3 to install sftdyn (e.g. pip3)")
    exit(1)

setup(
    name="sftdyn",
    version=VERSION,
    description="HTTP(S)-based dynamic DNS updater server",
    long_description="dyndns.org-like service that accepts update requests " +
                     "via HTTP(S) and forwards them to a locally running " +
                     "DNS server via nsupdate -l.\n" +
                     "Works with most routers.\n" +
                     "Readme: " +
                     "https://github.com/SFTtech/sftdyn/blob/master/README.md",
    author="Michael Ensslin",
    author_email="michael@ensslin.cc",
    url="https://github.com/SFTtech/sftdyn",
    license="GPL3+",
    packages=["sftdyn"],
    scripts=["bin/sftdyn"],
    data_files=[
        ("/etc/sftdyn/", ["etc/sample.conf"]),
        ("/usr/lib/systemd/system/", ["etc/sftdyn.service"]),
    ],
    platforms=[
        'Linux',
    ],
    classifiers=[
        ("License :: OSI Approved :: "
         "GNU General Public License v3 or later (GPLv3+)"),
        "Topic :: Internet :: WWW/HTTP",
        "Intended Audience :: Developers",
        "Environment :: Console",
        "Operating System :: POSIX :: Linux"
    ],
)
