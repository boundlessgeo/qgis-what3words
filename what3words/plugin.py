from __future__ import absolute_import
from builtins import object
# -*- coding: utf-8 -*-
#
# (c) 2016 Boundless, http://boundlessgeo.com
# This code is licensed under the GPL 2.0 license.
#

import os
import webbrowser

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from qgis.gui import QgsMessageBar
from qgis.core import QgsApplication
from qgis.utils import iface

from what3words.maptool import W3WMapTool
from what3words.coorddialog import W3WCoordInputDialog

from qgiscommons2.gui import (addAboutMenu,
                             removeAboutMenu,
                             addHelpMenu,
                             removeHelpMenu)
from qgiscommons2.gui.settings import (
                                  addSettingsMenu,
                                  removeSettingsMenu)
from qgiscommons2.settings import (readSettings,
                                  pluginSetting
                                  )

try:
    from processing.core.Processing import Processing
    from what3words.processingprovider.w3wprovider import W3WProvider
    processingOk = True
except:
    processingOk = False

class W3WTools(object):

    def __init__(self, iface):
        self.iface = iface

        try:
            from what3words.tests import testerplugin
            from qgistester.tests import addTestModule
            addTestModule(testerplugin, "what3words")
        except:
            pass

        self.mapTool = None
        if processingOk:
            self.provider = W3WProvider()

        readSettings()

    def initGui(self):
        mapToolIcon = QIcon(os.path.join(os.path.dirname(__file__), "icons", "w3w.png"))
        self.toolAction = QAction(mapToolIcon, "what3words map tool",
                                     self.iface.mainWindow())
        self.toolAction.triggered.connect(self.setTool)
        self.toolAction.setCheckable(True)
        self.iface.addToolBarIcon(self.toolAction)
        self.iface.addPluginToMenu("what3words", self.toolAction)

        zoomToIcon = QIcon(':/images/themes/default/mActionZoomIn.svg')
        self.zoomToAction = QAction(zoomToIcon, "Zoom to 3 word address",
                                     self.iface.mainWindow())
        self.zoomToAction.triggered.connect(self.zoomTo)
        self.iface.addPluginToMenu("what3words", self.zoomToAction)

        addSettingsMenu(
            "what3words", self.iface.addPluginToMenu)
        addHelpMenu(
            "what3words", self.iface.addPluginToMenu)
        addAboutMenu(
            "what3words", self.iface.addPluginToMenu)

        self.iface.mapCanvas().mapToolSet.connect(self.unsetTool)

        self.zoomToDialog = W3WCoordInputDialog(self.iface.mapCanvas(), self.iface.mainWindow())
        self.iface.addDockWidget(Qt.TopDockWidgetArea, self.zoomToDialog)
        self.zoomToDialog.hide()

        if processingOk:
            Processing.addProvider(self.provider)

        try:
            from lessons import addLessonsFolder, addGroup
            folder = os.path.join(os.path.dirname(__file__), "_lessons")
            addLessonsFolder(folder, "what3words")
        except:
            pass

    def zoomTo(self):
        apikey = pluginSetting("apiKey")
        if apikey is None or apikey == "":
            self._showMessage('what3words API key is not set. Please set it and try again.', QgsMessageBar.WARNING)
            return
        self.zoomToDialog.setApiKey(apikey)
        self.zoomToDialog.show()

    def unsetTool(self, tool):
        try:
            if not isinstance(tool, W3WMapTool):
                self.toolAction.setChecked(False)
        except:
            # ignore exceptions thrown when unloading plugin, since
            # map tool class might not exist already
            pass

    def setTool(self):
        apikey = pluginSetting("apiKey")
        if apikey is None or apikey == "":
            self._showMessage('what3words API key is not set. Please set it and try again.', QgsMessageBar.WARNING)
            return
        if self.mapTool is None:
            self.mapTool = W3WMapTool(self.iface.mapCanvas())
        self.toolAction.setChecked(True)
        self.iface.mapCanvas().setMapTool(self.mapTool)

    def unload(self):
        self.iface.mapCanvas().unsetMapTool(self.mapTool)
        self.iface.removeToolBarIcon(self.toolAction)
        self.iface.removePluginMenu("what3words", self.toolAction)
        self.iface.removePluginMenu("what3words", self.zoomToAction)

        removeSettingsMenu("what3words")
        removeHelpMenu("what3words")
        removeAboutMenu("what3words")

        self.iface.removeDockWidget(self.zoomToDialog)

        if processingOk:
            Processing.removeProvider(self.provider)

        try:
            from what3words.tests import testerplugin
            from qgistester.tests import removeTestModule
            removeTestModule(testerplugin, "what3words")
        except:
            pass

        try:
            from lessons import removeLessonsFolder
            folder = os.path.join(pluginPath, '_lessons')
            removeLessonsFolder(folder)
        except:
            pass

    def _showMessage(self, message, level=QgsMessageBar.INFO):
        iface.messageBar().pushMessage(
            message, level, iface.messageTimeout())
