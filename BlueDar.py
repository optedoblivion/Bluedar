#!/usr/bin/python
# coding: utf-8

import gobject
import gtk
import os
import pygtk
pygtk.require('2.0')
import sys

import BlueDarLib

ICON = "icons/bl.png"
CONFIG_FILE = ".BlueDar"
CONFIG = os.popen("echo $HOME")
CONFIG = str(CONFIG.next())[:-1]
CONFIG = CONFIG + "/" + CONFIG_FILE
VERSION = "1.2.0"

class About(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self)
        self.set_icon(gtk.gdk.pixbuf_new_from_file(ICON))

class ScrollWindow(gtk.ScrolledWindow):
    def __init__(self):
        gtk.ScrolledWindow.__init__(self)
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

class Notebook(gtk.Notebook):
    def __init__(self):
        gtk.Notebook.__init__(self)

    def append(self, widget, label="Test"):
        label = gtk.Label(label)
        self.append_page(widget, label)

    def prepend(self, widget, label="Test"):
        label = gtk.Label(label)
        self.prepend_page(widget, label)


class Tree(gtk.TreeView):
    def __init__(self):
        self.model = gtk.TreeStore(gobject.TYPE_STRING, gobject.TYPE_STRING,
                                       gobject.TYPE_STRING, gobject.TYPE_STRING)
                                       
        gtk.TreeView.__init__(self, self.model)
        
        self.nameRenderer = gtk.CellRendererText()
        self.macRenderer = gtk.CellRendererText()
        
        self.nameColumn = gtk.TreeViewColumn("Device Name", self.nameRenderer,
                                             text=0, foreground=2, background=3)
        self.macColumn = gtk.TreeViewColumn("Device Mac Address",
                           self.macRenderer, text=1, foreground=2, background=3)
                           
        self.append_column(self.nameColumn)
        self.append_column(self.macColumn)
        self.set_headers_visible(True)
        self.nameColumn.set_sort_column_id(0)
        self.macColumn.set_sort_column_id(1)
        self.set_search_column(1)
        self.set_reorderable(True)
        self.columns_autosize()

    def test(self):
        print "Fuck"

    def insertRow(self, parent=None, name='Error'):
        iter = self.model.append(parent, [name[0],  name[1],"#000000","#FFFFFF"])
        return iter

    def clear(self):
        self.model.clear()

class BlueDar(gtk.Window):
    """
        Class extends gtk.Window for GUI config.
    """

    about = About()
    radar = None
    verbose = False

    def __init__(self):
        ## Setup window.
        gtk.Window.__init__(self)
        self.set_default_size(400, 300)
        self.set_title("BlueDar %s"%VERSION)
        self.set_decorated(True)
        self.set_icon(gtk.gdk.pixbuf_new_from_file(ICON))
        self.set_border_width(5)
        self.connect('delete-event', self.Destroy)

        ## Make button
        self.confirmButton = gtk.Button('Apply')
        self.cancelButton = gtk.Button('Close')
        self.scanButton = gtk.Button('Scan')
        self.setMacButton = gtk.Button('Set Mac')
        self.clearScanButton = gtk.Button('Clear')
        self.enableButton = gtk.Button("Disable")
        
        self.confirmButton.connect('clicked', self.saveAll)
        self.cancelButton.connect('clicked', self.showAll)
        self.scanButton.connect('clicked', self.scan)
        self.setMacButton.connect('clicked', self.setMacAddress)
        self.clearScanButton.connect('clicked', self.clearScan)
        self.enableButton.connect('clicked', self.toggleRadar)

        ## Setup status icon in sys tray.
        self.icon = gtk.StatusIcon()
        self.setStatus("BlueDar %s"%VERSION)
        self.icon.set_from_file(ICON)

        ## Create VBox and HBox.
        self.configBox = gtk.VBox(True, 1)
        self.vBox = gtk.VBox(False, 1)
        self.vBox2 = gtk.VBox(True, 1)
        self.vBox3 = gtk.VBox(True, 1)
        self.hBox1 = gtk.HBox(True, 0)
        self.hBox2 = gtk.HBox(True, 0)
        self.hBox3 = gtk.HBox(True, 0)
        self.hBox4 = gtk.HBox(True, 0)
        self.hBox5 = gtk.HBox(True, 0)
        self.hBox6 = gtk.HBox(True, 0)
        self.hBox7 = gtk.HBox(True, 0)
        self.label1 = gtk.Label("Mac Address: ")
        self.label2 = gtk.Label("Lock Signal: ")
        self.label3 = gtk.Label("Unlock Signal: ")
        self.label4 = gtk.Label("Lock Command: ")
        self.label5 = gtk.Label("Unlock Command: ")
        self.label6 = gtk.Label("Proximity Command: ")
        self.label7 = gtk.Label("Interval: ")
        self.label1.set_alignment(0,1)
        self.label2.set_alignment(0,1)
        self.label3.set_alignment(0,1)
        self.label4.set_alignment(0,1)
        self.label5.set_alignment(0,1)
        self.label6.set_alignment(0,1)
        self.label7.set_alignment(0,1)

        ## Create Text Entries.
        self.entry1 = gtk.Entry()
        self.entry2 = gtk.Entry()
        self.entry3 = gtk.Entry()
        self.entry4 = gtk.Entry()
        self.entry5 = gtk.Entry()
        self.entry6 = gtk.Entry()
        self.entry7 = gtk.Entry()

        ## Pack HBoxes
        self.hBox1.pack_start(self.label1, False, True, 1)
        self.hBox1.pack_start(self.entry1, True, True, 1)
        self.hBox2.pack_start(self.label2, False, True, 1)
        self.hBox2.pack_start(self.entry2, True, True, 1)
        self.hBox3.pack_start(self.label3, False, True, 1)
        self.hBox3.pack_start(self.entry3, True, True, 1)
        self.hBox4.pack_start(self.label4, False, True, 1)
        self.hBox4.pack_start(self.entry4, True, True, 1)
        self.hBox5.pack_start(self.label5, False, True, 1)
        self.hBox5.pack_start(self.entry5, True, True, 1)
        self.hBox6.pack_start(self.label6, False, True, 1)
        self.hBox6.pack_start(self.entry6, True, True, 1)
        self.hBox7.pack_start(self.label7, False, True, 1)
        self.hBox7.pack_start(self.entry7, True, True, 1)

        ## Pack entries on the hBox.
        self.vBox2.pack_start(self.hBox1, True, True, 1)
        self.vBox2.pack_start(self.hBox2, True, True, 1)
        self.vBox2.pack_start(self.hBox3, True, True, 1)
        self.vBox2.pack_start(self.hBox4, True, True, 1)
        self.vBox2.pack_start(self.hBox5, True, True, 1)
        self.vBox2.pack_start(self.hBox6, True, True, 1)
        self.vBox2.pack_start(self.hBox7, True, True, 1)

        self.buttonHBox = gtk.HBox(True, 0)
        self.buttonHBox.pack_start(self.confirmButton, False, True, 1)
        self.buttonHBox.pack_start(self.cancelButton, False, True, 1)

        ## Pack box of configs into this container.
        self.configBox.pack_start(self.vBox2, True, True, 1)

        ## Make notebook
        self.Notebook1 = Notebook()
        self.DeviceList = Tree()
        self.avBox = gtk.VBox(False, 1)
        sw = ScrollWindow()
        sw.add(self.DeviceList)
        self.ahBox = gtk.HBox(True, 1)
        self.ahBox.pack_start(self.scanButton, False, True, 1)
        self.ahBox.pack_start(self.setMacButton, False, True, 1)
        self.ahBox.pack_start(self.clearScanButton, False, True, 1)
        self.avBox.pack_start(sw, True, True, 1)
        self.avBox.pack_start(self.ahBox, False, False, 1)

        self.vBox3.pack_start(self.enableButton, True, False, 1)

        self.Notebook1.prepend(self.avBox, "BlueDar")
        self.Notebook1.append(self.configBox, "Config")
        self.Notebook1.append(self.vBox3, "Controls")

        ## Pack buttons onto vBox3
        self.vBox.pack_start(self.Notebook1, True, False, 1)
        self.vBox.pack_start(self.buttonHBox, False, False, 1)
        
        self.vBox.show_all()
        self.add(self.vBox)

        ## Setup menu for status icon.
        self.popupmenu = gtk.Menu()
        menuItem = gtk.ImageMenuItem(gtk.STOCK_PREFERENCES)
        menuItem.connect('activate', self.showAll)
        self.popupmenu.append(menuItem)
        menuItem = gtk.ImageMenuItem(gtk.STOCK_ABOUT)
        menuItem.connect('activate', self.showAbout)
        self.popupmenu.append(menuItem)
        menuItem = gtk.MenuItem()
        self.popupmenu.append(menuItem)
        menuItem = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        menuItem.connect('activate', self.quit)
        self.popupmenu.append(menuItem)

        ## Connect icon events.
        self.icon.connect('activate', self.showAll)
        self.icon.connect('popup-menu', self.menu, self.popupmenu)

        ## Show Status Icon.
        self.icon.set_visible(True)

        ## Start radar
        self.startRadar()

    def startRadar(self):
        self.radar = BlueDarLib.BlueDar()
        if self.verbose:
            self.radar.verbose = verbose
            print "Starting radar thread..."
        self.radar.start()

    def termRadar(self):
        self.radar.terminateFlag = True

    def loadConfig(self):
        if os.path.exists(CONFIG):
            configFile = open(CONFIG, 'rb')
            data = configFile.readlines()
            self.configs = {}
            for line in data:
                if not str(line)[0] == "#":
                    key = str(line).split('=')[0]
                    val = str(line).split('=')[1].replace('\n','')
                    self.configs[str(key)] = str(val)

            self.entry1.set_text(self.configs['macAddress'])
            self.entry2.set_text(self.configs['lockDistance'])
            self.entry3.set_text(self.configs['unlockDistance'])
            self.entry4.set_text(self.configs['lockCommand'])
            self.entry5.set_text(self.configs['unlockCommand'])
            self.entry6.set_text(self.configs['proximityCommand'])
            self.entry7.set_text(self.configs['updateInterval'])
            configFile.close()

    def clearScan(self, widget, data = None):
        self.DeviceList.clear()

    def Destroy(self, widget, data = None):
        self.showAll(widget, data)
        return True

    def quit(self, widget, data = None):
        self.termRadar()
        gtk.main_quit()

    def menu(self, widget, button, time, data = None):
        if button == 3:
            if data:
                data.show_all()
                data.popup(None, None, None, 3, time)

    def scan(self, widget, data = None):
        self.termRadar()
        blue = BlueDarLib.BlueDar()
        for device in blue.getNearbyDevices():
            self.DeviceList.insertRow(None, device)
        self.startRadar()

    def saveAll(self, widget, data = None):
        configFile = open(CONFIG, "wb")
        configFile.write("# Bluedar Config")
        configFile.write("\n")
        configFile.write("macAddress="+str(self.entry1.get_text()))
        configFile.write("\n")
        configFile.write("lockDistance="+str(self.entry2.get_text()))
        configFile.write("\n")
        configFile.write("unlockDistance="+str(self.entry3.get_text()))
        configFile.write("\n")
        configFile.write("lockCommand="+str(self.entry4.get_text()))
        configFile.write("\n")
        configFile.write("unlockCommand="+str(self.entry5.get_text()))
        configFile.write("\n")
        configFile.write("proximityCommand="+str(self.entry6.get_text()))
        configFile.write("\n")
        configFile.write("updateInterval="+str(self.entry7.get_text()))
        configFile.write("\n")
        configFile.close()
    
    def setMacAddress(self, widget, data = None):
        selection = self.DeviceList.get_selection()
        (mac, name) = selection.get_selected()
        if name:
            mac = self.DeviceList.model.get(name, 0)
        if type(mac) == type(()):
            mac = mac[0]
            self.entry1.set_text(mac)

    def setStatus(self, msg):
        self.icon.set_tooltip(msg)

    def showAll(self, widget, data = None):
        if self.get_property("visible"):
            self.hide()
        else:
            self.loadConfig()
            self.show_all()

    def showAbout(self, widget, data = None):
        if self.about.get_property("visible"):
            self.about.hide()
        else:
            self.about.show()

    def toggleRadar(self, widget, data = None):
        if self.radar.isAlive():
            self.enableButton.set_label("Enable")
            self.termRadar()
            self.setStatus("Radar Disabled")
        else:
            self.enableButton.set_label("Disable")
            self.startRadar()
            self.setStatus("Radar Enabled")

if __name__=="__main__":

    bluedar = BlueDar()
    bluedar.loadConfig()
    gtk.gdk.threads_init()
    gtk.main()
