# -*- coding: utf-8 -*-

# (c) 2016 Boundless, http://boundlessgeo.com
# This code is licensed under the GPL 2.0 license.


import os

from qgis.PyQt.QtCore import QVariant
from qgis.core import (QgsProcessingException,
                       QgsCoordinateReferenceSystem,
                       QgsCoordinateTransform,
                       QgsField,
                       QgsProject,
                       QgsFeatureSink,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterString,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterFeatureSink)
from processing.algs.qgis.QgisAlgorithm import QgisAlgorithm

from what3words.w3w import what3words
from qgiscommons2.settings import pluginSetting

pluginPath = os.path.split(os.path.dirname(__file__))[0]

class Add3WordsFieldAlgorithm(QgisAlgorithm):

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'

    def group(self):
        return self.tr('what3words')

    def groupId(self):
        return 'w3w'

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSource(self.INPUT, self.tr('Input layer')))
        self.addParameter(QgsProcessingParameterFeatureSink(self.OUTPUT,
                                                            self.tr('Output')))

    def name(self):
        return 'addw3wfield'

    def displayName(self):
        return self.tr('Add what3words field')

    def processAlgorithm(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INPUT, context)        
        fields = source.fields()
        field = QgsField("w3w", QVariant.String)
        fields.append(field)
        apiKey = pluginSetting("apiKey")
        addressLanguage = pluginSetting("addressLanguage")
        w3w = what3words(apikey=apiKey,addressLanguage=addressLanguage)
        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT, context,
                                               fields, source.wkbType(), source.sourceCrs())

        features = source.getFeatures()
        total = 100.0 / source.featureCount() if source.featureCount() else 0

        epsg4326 = QgsCoordinateReferenceSystem('EPSG:4326')
        transform = QgsCoordinateTransform(source.sourceCrs(), epsg4326, QgsProject.instance())

        for current, feat in enumerate(features):
            if feedback.isCanceled():
                break

            feedback.setProgress(int(current * total))
            attrs = feat.attributes()
            pt = feat.geometry().centroid().asPoint()
            try:
                pt4326 = transform.transform(pt.x(), pt.y())
                threeWords = w3w.convertTo3wa(pt4326.y(), pt4326.x())["words"]
            except Exception as e:
                progress.setDebugInfo("Failed to retrieve w3w address for feature {}:\n{}".format(feat.id(), str(e)))
                threeWords = ""

            attrs.append(threeWords)
            feat.setAttributes(attrs)
            sink.addFeature(feat, QgsFeatureSink.FastInsert)

        return {self.OUTPUT: dest_id}
