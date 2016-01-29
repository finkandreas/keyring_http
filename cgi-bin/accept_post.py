#!/usr/bin/env python3

import json
import os
#import cgi
import sys

# debug
import cgitb
cgitb.enable()

myJson = json.loads(sys.stdin.read(int(os.environ.get("CONTENT_LENGTH"))))
sys.stderr.write(str(myJson)+"\n")

print('Content-Type: application/json\n')
print(json.dumps({"status": "success"}))
