#!/bin/sh
#scp /tmp/shot.jpg cos@5w.fi:/var/www/shot.jpg

curl -F "image=@/tmp/shot.jpg" https://vaasa.hacklab.fi/cam/cam.php -o /dev/null -s
