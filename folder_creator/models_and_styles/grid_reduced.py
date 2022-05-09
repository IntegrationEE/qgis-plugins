"""
Model exported as python.
Name : grid_reduced
Group : 
With QGIS : 32003
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing
import os

class Grid_reduced(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('grid', 'grid', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('outline', 'outline', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Grid_reduced', 'grid_reduced', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(2, model_feedback)
        results = {}
        outputs = {}

        # Extract by location
        alg_params = {
            'INPUT': parameters['grid'],
            'INTERSECT': parameters['outline'],
            'PREDICATE': [0],  # intersect
            'OUTPUT': parameters['Grid_reduced']
        }
        outputs['ExtractByLocation'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Grid_reduced'] = outputs['ExtractByLocation']['OUTPUT']

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        basepath = os.path.dirname(__file__)
        style_path = os.path.join(basepath,'styles/a4_grid_reduced_style.qml')
        # Set style for vector layer
        alg_params = {
            'INPUT': outputs['ExtractByLocation']['OUTPUT'],
            'STYLE': style_path
        }
        outputs['SetStyleForVectorLayer'] = processing.run('qgis:setstyleforvectorlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        return results

    def name(self):
        return 'grid_reduced'

    def displayName(self):
        return 'grid_reduced'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Grid_reduced()
