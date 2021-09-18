#!/bin/bash

# VERSION_OLD=0.4
# LINK=https://github.com/Psy-Fer/interARTIC/releases/download/v${VERSION_OLD}/interartic-v${VERSION_OLD}-${OS}-${ARCH}-binaries.tar.gz

# ARCH=x86-64
# #ARCH=aarch64
# OS=linux
# #os=macos

set -e
set -x

VERSION_NEW=`git describe --tags`

wget ${LINK} -O interartic_bin.tar.gz -q
tar xf interartic_bin.tar.gz
rm interartic_bin.tar.gz
rm -rf interartic_bin/templates interartic_bin/scripts interartic_bin/static interartic_bin/src interartic_bin/primer-schemes interartic_bin/*.sh interartic_bin/*.py interartic_bin/LICENSE.interartic.txt
git clone https://github.com/Psy-Fer/interARTIC.git
mv interARTIC/templates interARTIC/scripts interARTIC/static interARTIC/src interARTIC/primer-schemes interARTIC/main.py interARTIC/config.init interartic_bin/

if [ "${OS}" = macos ]; then
	mv interARTIC/run_mac.sh interartic_bin/run.sh
else
	mv interARTIC/run.sh interartic_bin/run.sh
fi

mv interARTIC/LICENSE interartic_bin/LICENSE.interartic.txt
rm -rf interARTIC

tar zcf interartic-${VERSION_NEW}-${OS}-${ARCH}-binaries.tar.gz interartic_bin
rm -rf interartic_bin

exit 0
