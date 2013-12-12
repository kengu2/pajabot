#!/bin/sh
raspistill -vf -hf -o /tmp/shot.jpg
scp /tmp/shot.jpg cos@5w.fi:/var/www/shot.jpg

