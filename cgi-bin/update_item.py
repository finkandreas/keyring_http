#!/usr/bin/env python3

import json
import cgi
import sys
import dbus
from gi.repository import GObject
from dbus.mainloop.glib import DBusGMainLoop

global loop


def received_pw(dismissed, objectPath):
  global loop
  loop.quit()


formData = cgi.FieldStorage()
data = json.loads(formData.getvalue("json"))
dbus_path = data["dbus_path"]
label = data["label"]
password = data["password"]
attributes = data["attributes"]

DBusGMainLoop(set_as_default=True)
bus = dbus.SessionBus()

# unlock
bus.add_signal_receiver(handler_function=received_pw, signal_name="Completed", dbus_interface="org.freedesktop.Secret.Prompt", )
secrets = bus.get_object("org.freedesktop.secrets", "/org/freedesktop/secrets")
(unlocked, prompt) = secrets.get_dbus_method("Unlock", dbus_interface="org.freedesktop.Secret.Service")([dbus_path])
if dbus_path not in unlocked:
  bus.get_object("org.freedesktop.secrets", prompt).get_dbus_method("Prompt", dbus_interface="org.freedesktop.Secret.Prompt")("")
  loop = GObject.MainLoop()
  loop.run()

# open session
(_, session) = secrets.get_dbus_method("OpenSession", dbus_interface="org.freedesktop.Secret.Service")("plain", "")
itemProxy = bus.get_object("org.freedesktop.secrets", dbus_path)

if len(attributes) > 0: itemProxy.get_dbus_method("Set", dbus_interface="org.freedesktop.DBus.Properties")("org.freedesktop.Secret.Item", "Attributes", attributes)
itemProxy.get_dbus_method("Set", dbus_interface="org.freedesktop.DBus.Properties")("org.freedesktop.Secret.Item", "Label", label)

# set password
secret = (session, bytearray(), bytearray(password, 'utf-8'), "text/plain; charset=utf8")
itemProxy.get_dbus_method("SetSecret", dbus_interface="org.freedesktop.Secret.Item")(secret)

print('Content-Type: application/json\n')
print(json.dumps({"status": "success"}))
