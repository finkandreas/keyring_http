#!/usr/bin/env python3

import dbus
from gi.repository import GObject
from dbus.mainloop.glib import DBusGMainLoop
import sys
import json


global missing_items
global loop
global item2collection
global collected_results
missing_items = set()

def received_pw(dismissed, objectPath):
  global loop
  if dismissed: loop.quit()
  else:
    process_item(objectPath[0])


def process_item(item):
  itemProxy = bus.get_object("org.freedesktop.secrets", item)
  attributes = itemProxy.get_dbus_method("Get", dbus_interface="org.freedesktop.DBus.Properties")("org.freedesktop.Secret.Item", "Attributes")
  label = itemProxy.get_dbus_method("Get", dbus_interface="org.freedesktop.DBus.Properties")("org.freedesktop.Secret.Item", "Label")
  locked = itemProxy.get_dbus_method("Get", dbus_interface="org.freedesktop.DBus.Properties")("org.freedesktop.Secret.Item", "Locked")
  if locked:
    (unlocked, prompt) = secrets.get_dbus_method("Unlock", dbus_interface="org.freedesktop.Secret.Service")([item])
    if item not in unlocked:
      bus.get_object("org.freedesktop.secrets", prompt).get_dbus_method("Prompt", dbus_interface="org.freedesktop.Secret.Prompt")("")
  else:
    secret = itemProxy.get_dbus_method("GetSecret", dbus_interface="org.freedesktop.Secret.Item")(session)
    collected_results[item2collection[item]].append({"dbus_path" : item, "label": label, "attributes": attributes, "password": str(bytearray(secret[2]), 'utf-8')})
    process_missing_items()

def process_missing_items():
  global missing_items
  global loop
  if len(missing_items) > 0: process_item(missing_items.pop())
  else: loop.quit()

DBusGMainLoop(set_as_default=True)
bus = dbus.SessionBus()
bus.add_signal_receiver(handler_function=received_pw, signal_name="Completed", dbus_interface="org.freedesktop.Secret.Prompt", )
secrets = bus.get_object("org.freedesktop.secrets", "/org/freedesktop/secrets")
(_, session) = secrets.get_dbus_method("OpenSession", dbus_interface="org.freedesktop.Secret.Service")("plain", "")

collections = secrets.get_dbus_method("Get", dbus_interface="org.freedesktop.DBus.Properties")("org.freedesktop.Secret.Service", "Collections")
item2collection = {}
collected_results = {}
for collection in collections:
  collectionProxy = bus.get_object("org.freedesktop.secrets", collection)
  collectionLabel = collectionProxy.get_dbus_method("Get", dbus_interface="org.freedesktop.DBus.Properties")("org.freedesktop.Secret.Collection", "Label")
  items = collectionProxy.get_dbus_method("Get", dbus_interface="org.freedesktop.DBus.Properties")("org.freedesktop.Secret.Collection", "Items")
  collected_results[collection] = []
  for item in items:
    missing_items.add(item)
    item2collection[item] = collection

loop = GObject.MainLoop()
process_missing_items()
if len(missing_items) > 0:
  loop.run()

print("Content-Type: application/json\n")
print(json.dumps(collected_results))
