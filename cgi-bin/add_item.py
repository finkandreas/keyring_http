#!/usr/bin/env python3

import json
import common

data = common.extract_json()
collection = data["collection"]
label = data["label"]
password = data["password"]

keyring = common.DbusKeyring()
keyring.UnlockItem(collection)
secret = keyring.ToDbusSecret(password)
attribs = { "org.freedesktop.Secret.Item.Label": label, "org.freedesktop.Secret.Item.Attributes": {'xdg:schema': 'org.freedesktop.Secret.Generic'} }
(objPath, prompt) = common.DbusProxyIface(keyring.bus.get_object("org.freedesktop.secrets", collection), "org.freedesktop.Secret.Collection").CallMethod("CreateItem", attribs, secret, False)
if (objPath == "/"): keyring.WaitForPrompt(prompt)

print('Content-Type: application/json\n')
print(json.dumps({"status": "success"}))
