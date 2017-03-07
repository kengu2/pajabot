#!/bin/sh

wget 'http://10.10.0.11/snapshot.cgi?user=cam1&pwd=cam1' -O /tmp/shot.jpg -o /dev/null &

#raspistill -o /tmp/shot.jpg


