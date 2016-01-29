#!/usr/bin/env python3

import json
import common

data = common.extract_json()
dbus_path = data["dbus_path"]

keyring = common.DbusKeyring()
keyring.UnlockItem(dbus_path)
prompt = common.DbusProxyIface(keyring.bus.get_object("org.freedesktop.secrets", dbus_path), "org.freedesktop.Secret.Item").CallMethod("Delete")
if prompt != "/": keyring.WaitForPrompt(prompt)

print('Content-Type: application/json\n')
print(json.dumps({"status": "success"}))
