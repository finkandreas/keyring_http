#!/usr/bin/env python3

# imports from a file, you will be asked for every secret
# python3 import.py import_file

import json
import common
import sys

if len(sys.argv) < 2:
  print("Usage: import.py import_file.txt")
  sys.exit(1)

keyring = common.DbusKeyring()
all = json.load(open(sys.argv[1], 'r'))
for collection,items in all.items():
  if items: keyring.UnlockItem(collection)
  for item in items:
    print("Label={}\nAttributes={}".format(item['label'], item['attributes']))
    password = input("Password: ")
    secret = keyring.ToDbusSecret(password)
    attribs = { "org.freedesktop.Secret.Item.Label": item['label'], "org.freedesktop.Secret.Item.Attributes": item['attributes'] }
    (objPath, prompt) = common.DbusProxyIface(keyring.bus.get_object("org.freedesktop.secrets", collection), "org.freedesktop.Secret.Collection").CallMethod("CreateItem", attribs, secret, False)
    if (objPath == "/"): keyring.WaitForPrompt(prompt)
