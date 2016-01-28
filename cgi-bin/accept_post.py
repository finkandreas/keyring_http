#!/usr/bin/env python3

import json
import cgi
import sys

# debug
#import cgitb
#cgitb.enable()

data = json.loads(cgi.FieldStorage().getvalue("json"))
dbus_path = data["dbus_path"]
label = data["label"]
password = data["password"]
attributes = data["attributes"]

print('Content-Type: application/json\n')
print(json.dumps({"dbus_path": dbus_path, "label": label, "password": password, "attributes": attributes}))
