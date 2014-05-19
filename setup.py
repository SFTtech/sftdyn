#!/usr/bin/env python3
from distutils.core import setup
from sftdyn import VERSION

setup(
    name='sftdyn',
    version=VERSION,
    description='dyndns/dynamic DNS server and updater for bind',
    author='Michael Enßlin',
    author_email='michael@ensslin.cc',
    url='https://github.com/SFTtech/sftdyn',
    license='GPLv3 or higher',
    packages=['sftdyn'],
    scripts=['bin/sftdyn'],
    data_files=[('/etc/sftdyn/', ['sample.conf'])]
)
