import json
import dbus
import sys
import os
from gi.repository import GObject
from dbus.mainloop.glib import DBusGMainLoop


def extract_json():
  return json.loads(str(sys.stdin.buffer.read(int(os.environ.get("CONTENT_LENGTH"))), 'utf-8'))


class DbusProxyIface(object):
  def __init__(self, proxy, iface):
    self.proxy = proxy;
    self.iface = iface;

  def GetProperty(self, property):
    return self.proxy.Get(self.iface, property, dbus_interface=dbus.PROPERTIES_IFACE)

  def SetProperty(self, property, value):
    self.proxy.Set(self.iface, property, value, dbus_interface=dbus.PROPERTIES_IFACE)

  def CallMethod(self, method, *args):
    return self.proxy.get_dbus_method(method, dbus_interface=self.iface)(*args)


class DbusKeyring(object):
  def __init__(self):
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    self.bus = dbus.SessionBus()
    self.bus.add_signal_receiver(handler_function=self._received_pw, signal_name="Completed", dbus_interface="org.freedesktop.Secret.Prompt")
    self.secretsProxy = DbusProxyIface(self.bus.get_object("org.freedesktop.secrets", "/org/freedesktop/secrets"), "org.freedesktop.Secret.Service")
    self.loop = GObject.MainLoop()
    self.session = None

  def SetSecret(self, item, password):
    secret = self.ToDbusSecret(password)
    DbusProxyIface(self.bus.get_object("org.freedesktop.secrets", item), "org.freedesktop.Secret.Item").CallMethod("SetSecret", secret)

  def GetSecret(self, item):
    if self.session == None: (_, self.session) = self.secretsProxy.CallMethod("OpenSession", "plain", "")
    secret = DbusProxyIface(self.bus.get_object("org.freedesktop.secrets", item), "org.freedesktop.Secret.Item").CallMethod("GetSecret", self.session)
    return bytearray(secret[2]).decode('utf-8')

  def ToDbusSecret(self, password):
    if self.session == None: (_, self.session) = self.secretsProxy.CallMethod("OpenSession", "plain", "");
    return (self.session, bytearray(), bytearray(password, 'utf-8'), "text/plain; charset=utf8")

  def GetCollections(self):
    return self.secretsProxy.GetProperty("Collections")

  def UnlockItem(self, item):
    (unlocked, prompt) = self.secretsProxy.CallMethod("Unlock", [item])
    if prompt != '/': return self.WaitForPrompt(prompt)
    return True

  def WaitForPrompt(self, prompt):
    DbusProxyIface(self.bus.get_object("org.freedesktop.secrets", prompt), "org.freedesktop.Secret.Prompt").CallMethod("Prompt", "")
    self.loop.run()
    return not self.PromptDismissed

  def FindItem(self, attributesToMatch):
    (unlockedItems, lockedItems) = self.secretsProxy.CallMethod("SearchItems", attributesToMatch)
    item = None
    if len(unlockedItems) > 0:
      item = unlockedItems[0]
    elif len(lockedItems) > 0:
      self.UnlockItem(lockedItems[0])
      item = lockedItems[0]
    else:
      return (None, None)
    allAttribs = DbusProxyIface(self.bus.get_object("org.freedesktop.secrets", item), "org.freedesktop.Secret.Item").GetProperty("Attributes")
    return (allAttribs, self.GetSecret(item))


  def _received_pw(self, dismissed, objectPath):
    self.PromptDismissed = dismissed
    self.loop.quit()
