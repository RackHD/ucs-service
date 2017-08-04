#!/bin/bash -ex
echo "deb http://ftp.debian.org/debian jessie-backports main" >> /etc/apt/sources.list
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 8B48AD6246925553
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 7638D0442B90D010
apt-get update
apt-get -t jessie-backports install dh-virtualenv
