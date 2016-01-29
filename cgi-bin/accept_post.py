#!/usr/bin/env python3

import json
import os
#import cgi
import sys

# debug
import cgitb
cgitb.enable()

myJson = json.loads(str(sys.stdin.buffer.read(int(os.environ.get("CONTENT_LENGTH"))), 'utf-8'))
sys.stderr.write(str(myJson)+"\n")

print('Content-Type: application/json\n')
print(json.dumps({"status": "success"}))


