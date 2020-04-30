# -*- coding: utf-8 -*-

# (c) 2016 Boundless, http://boundlessgeo.com
# This code is licensed under the GPL 2.0 license.

import os

from qgis.PyQt.QtGui import QIcon

from qgis.core import QgsProcessingProvider
 
from processing.core.ProcessingConfig import Setting, ProcessingConfig
from what3words.processingprovider.add3wordsfield import Add3WordsFieldAlgorithm

pluginPath = os.path.split(os.path.dirname(__file__))[0]

class W3WProvider(QgsProcessingProvider):

    def __init__(self):
        super().__init__()

    def load(self):
        ProcessingConfig.settingIcons[self.name()] = self.icon()
        ProcessingConfig.addSetting(Setting(self.name(), 'ACTIVATE_W3W',
                                            'Activate', False))
        ProcessingConfig.readSettings()
        self.refreshAlgorithms()
        return True

    def unload(self):
        pass

    def isActive(self):
        """Return True if the provider is activated and ready to run algorithms"""
        return ProcessingConfig.getSetting('ACTIVATE_W3W')

    def setActive(self, active):
        ProcessingConfig.setSettingValue('ACTIVATE_W3W', active)

    def id(self):
        return 'what3words'

    def name(self):        
        return 'what3words Tools'

    def icon(self):        
        return QIcon(os.path.join(pluginPath, 'icons', 'w3w.png'))

    def loadAlgorithms(self):
        for alg in [Add3WordsFieldAlgorithm()]:
            self.addAlgorithm(alg)

