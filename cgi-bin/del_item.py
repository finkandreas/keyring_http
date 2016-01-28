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

DBusGMainLoop(set_as_default=True)
bus = dbus.SessionBus()
itemProxy = bus.get_object("org.freedesktop.secrets", dbus_path)
prompt = itemProxy.get_dbus_method("Delete", dbus_interface="org.freedesktop.Secret.Item")()

if prompt != "/":
  bus.add_signal_receiver(handler_function=received_pw, signal_name="Completed", dbus_interface="org.freedesktop.Secret.Prompt", )
  bus.get_object("org.freedesktop.secrets", prompt).get_dbus_method("Prompt", dbus_interface="org.freedesktop.Secret.Prompt")("")
  loop = GObject.MainLoop()
  loop.run()

print('Content-Type: application/json\n')
print(json.dumps({"status": "success"}))
