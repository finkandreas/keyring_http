#!/usr/bin/env python3

import json
import common

keyring = common.DbusKeyring()

collections = keyring.GetCollections()
collected_results = {}
for collection in collections:
  collectionProxy = common.DbusProxyIface(keyring.bus.get_object("org.freedesktop.secrets", collection), "org.freedesktop.Secret.Collection")
  # collectionLabel = collectionProxy.GetProperty("Label")
  items = collectionProxy.GetProperty("Items")
  collected_results[collection] = []
  for item in items:
    keyring.UnlockItem(item)
    itemProxyIface = common.DbusProxyIface(keyring.bus.get_object("org.freedesktop.secrets", item), "org.freedesktop.Secret.Item")
    attributes = itemProxyIface.GetProperty("Attributes")
    label = itemProxyIface.GetProperty("Label")
    secret = keyring.GetSecret(item)
    collected_results[collection].append({"dbus_path" : item, "label": label, "attributes": attributes, "password": secret})

print("Content-Type: application/json\n")
print(json.dumps(collected_results))
