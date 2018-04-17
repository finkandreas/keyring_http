#!/usr/bin/env python3

# exports everything without the passwords
# The output can be used as input to import.py and you will be asked during import for the secrets

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
    collected_results[collection].append({"dbus_path" : item, "label": label, "attributes": attributes})

print(json.dumps(collected_results, indent=4))
