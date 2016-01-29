#!/usr/bin/env python3

import json
import common

data = common.extract_json()
dbus_path = data["dbus_path"]
label = data["label"]
password = data["password"]
attributes = data["attributes"]

keyring = common.DbusKeyring()
keyring.UnlockItem(dbus_path)
itemProxy = common.DbusProxyIface(keyring.bus.get_object("org.freedesktop.secrets", dbus_path), "org.freedesktop.Secret.Item")
if len(attributes) > 0: itemProxy.SetProperty("Attributes", attributes)
itemProxy.SetProperty("Label", label)
keyring.SetSecret(dbus_path, password)

print('Content-Type: application/json\n')
print(json.dumps({"status": "success"}))
