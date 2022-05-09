"""
Model exported as python.
Name : A4 field paper
Group : field paper
With QGIS : 32003
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsCoordinateReferenceSystem
from qgis.core import QgsExpression
import processing
import os

class A4FieldPaper(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('residentialboundary', 'Residential boundary', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Final', 'Final', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(6, model_feedback)
        results = {}
        outputs = {}

        # Create grid
        alg_params = {
            'CRS': QgsCoordinateReferenceSystem('EPSG:3857'),
            'EXTENT': parameters['residentialboundary'],
            'HOVERLAY': 0,
            'HSPACING': 195,
            'TYPE': 2,  # Rectangle (Polygon)
            'VOVERLAY': 0,
            'VSPACING': 235,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CreateGrid'] = processing.run('native:creategrid', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # COL Field calculator
        alg_params = {
            'FIELD_LENGTH': 50,
            'FIELD_NAME': 'col',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': QgsExpression('\'((\' || \'left\' || \' - \' ||  \'minimum(left)\'  || \')/195)+1\'').evaluate(),
            'INPUT': outputs['CreateGrid']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        
        outputs['ColFieldCalculator'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        
        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # ROW Field calculator
        alg_params = {
            'FIELD_LENGTH': 50,
            'FIELD_NAME': 'row',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': QgsExpression('\'((\' || \'top\' || \' - \' ||  \'maximum(top)\'  || \')/235)*-1\'').evaluate(),
            'INPUT': outputs['ColFieldCalculator']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RowFieldCalculator'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Letter Field calculator
        alg_params = {
            'FIELD_LENGTH': 6,
            'FIELD_NAME': 'let',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # String
            'FORMULA': QgsExpression(' \'char(65+\' || \'row\' || \')\'').evaluate(),
            'INPUT': outputs['RowFieldCalculator']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['LetterFieldCalculator'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Final field calculator
        alg_params = {
            'FIELD_LENGTH': 5,
            'FIELD_NAME': 'g_id',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # String
            'FORMULA': QgsExpression(' \'concat(\'|| \'let\' ||\',\'|| \'col\' || \')\'').evaluate(),
            'INPUT': outputs['LetterFieldCalculator']['OUTPUT'],
            'OUTPUT': parameters['Final']
        }
        outputs['FinalFieldCalculator'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Final'] = outputs['FinalFieldCalculator']['OUTPUT']

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Set style for vector layer
        basepath = os.path.dirname(__file__)
        style_path = os.path.join(basepath,'styles/a4_grid_style.qml')
        alg_params = {
            'INPUT': outputs['FinalFieldCalculator']['OUTPUT'],
            'STYLE': style_path
        }
        outputs['SetStyleForVectorLayer'] = processing.run('qgis:setstyleforvectorlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        
        
        return results

    def name(self):
        return 'A4 field paper'

    def displayName(self):
        return 'A4 field paper'

    def group(self):
        return 'field paper'

    def groupId(self):
        return 'field paper'

    def createInstance(self):
        return A4FieldPaper()
