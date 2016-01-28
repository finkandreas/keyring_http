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
collection = data["collection"]
label = data["label"]
password = data["password"]

DBusGMainLoop(set_as_default=True)
bus = dbus.SessionBus()
bus.add_signal_receiver(handler_function=received_pw, signal_name="Completed", dbus_interface="org.freedesktop.Secret.Prompt", )
secrets = bus.get_object("org.freedesktop.secrets", "/org/freedesktop/secrets")
(_, session) = secrets.get_dbus_method("OpenSession", dbus_interface="org.freedesktop.Secret.Service")("plain", "")
collectionProxy = bus.get_object("org.freedesktop.secrets", collection)
attribs = { "org.freedesktop.Secret.Item.Label": label, "org.freedesktop.Secret.Item.Attributes": {'xdg:schema': 'org.freedesktop.Secret.Generic'} }
secret = (session, bytearray(), bytearray(password, 'utf-8'), "text/plain; charset=utf8")
(objPath, prompt) = collectionProxy.get_dbus_method("CreateItem", dbus_interface="org.freedesktop.Secret.Collection")(attribs, secret, False)
if (objPath == "/"):
  bus.get_object("org.freedesktop.secrets", prompt).get_dbus_method("Prompt", dbus_interface="org.freedesktop.Secret.Prompt")("")
  loop = GObject.MainLoop()
  loop.run()

print('Content-Type: application/json\n')
print(json.dumps({"status": "success"}))
