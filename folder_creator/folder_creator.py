# -*- coding: utf-8 -*-
"""
/***************************************************************************
 FolderCreator
                                 A QGIS plugin
 This plugin automates the creation of folders for each settlements in a work order
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2022-04-29
        git sha              : $Format:%H$
        copyright            : (C) 2022 by Integration Environment & Energy
        email                : ejolaiya@integration.org
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from math import ceil
import shutil


from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.core import Qgis,QgsVectorLayer,QgsVectorFileWriter,QgsProject
# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .folder_creator_dialog import FolderCreatorDialog
import os


class FolderCreator:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'FolderCreator_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Folder Creator')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None
        
    def generate_folders(self):

        joined_layer:QgsVectorLayer = self.dlg.joined_layer.currentLayer()
        work_order_number:int = self.dlg.work_order_number.value()
        state:str= self.dlg.state_name.text() 
        settlement_id_name:str = 'Name' if self.dlg.settlement_id_column_name.text() =="" else self.dlg.settlement_id_column_name.text()
        output_folder:str = self.dlg.output_folder.filePath()
        progress_bar = self.dlg.progress_bar

        #sanity checks

        if not (joined_layer.isSpatial() and isinstance(joined_layer,QgsVectorLayer)):
            
            self.iface.messageBar().pushMessage(
                "Layer error", "Selected layer is not supported. Plugin only support a vector Layer(GeoPackage, Shapefile etc)",level=Qgis.Critical,duration=5)

        elif state == "":
            self.iface.messageBar().pushMessage(
                "State error", "State name not provided",level=Qgis.Critical,duration=5
            )
        
        elif not os.path.exists(output_folder):

            self.iface.messageBar().pushMessage(
                "Path error", "Provided output folder does not exist",level=Qgis.Critical,duration=5
            )

        elif not joined_layer.hasFeatures():
            
            self.iface.messageBar().pushMessage(
                "Layer error", "Provided layer does not have a feature",level=Qgis.Critical,duration=5
            )
        
        else:


            total_features = len([x for x in joined_layer.getFeatures()])
            multiplication_factor = ceil(100/total_features)


            #QGIS output file options
            options=QgsVectorFileWriter.SaveVectorOptions()
            options.driverName="GPKG"
            options.onlySelectedFeatures = True
            context = QgsProject.instance().transformContext()

           
            for index,feature in enumerate(joined_layer.getFeatures()):

                
                joined_layer.select(feature.id())
                
                progress_bar.setValue(multiplication_factor * index + multiplication_factor) #needs some touches

                cluster_id = feature['cluster_of']  #assumed all cluster id column name are cluster_of
                settlement_id = feature[settlement_id_name]
                cleaned_cluster_id = str(cluster_id).split(".")[0] if isinstance(cluster_id,float) else cluster_id
                directory_name = f"{state}_WO{work_order_number}-{settlement_id}_{cleaned_cluster_id}"
                file_name = f"cluster_{cleaned_cluster_id}.gpkg"
                full_path = os.path.join(output_folder,directory_name)
                full_file_path = os.path.join(full_path,file_name)

                if not os.path.exists(full_path):
                    os.mkdir(full_path)
                    _writer = QgsVectorFileWriter.writeAsVectorFormatV3(
                    joined_layer,full_file_path,context,options
                    )
                    joined_layer.removeSelection()
                else:
                    shutil.rmtree(full_path)
                    os.mkdir(full_path)
                    _writer = QgsVectorFileWriter.writeAsVectorFormatV3(
                        joined_layer,full_file_path,context,options
                    )
                    joined_layer.removeSelection()
                
            
            self.iface.messageBar().pushMessage("Success", f"Operation completed,check here for generated folders: {full_path}",level=Qgis.Success,duration=5)
            
    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('FolderCreator', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/folder_creator/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Automated Folder Creation'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Folder Creator'),
                action)
            self.iface.removeToolBarIcon(action)

    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = FolderCreatorDialog()
            
        self.dlg.generate_button.clicked.connect(self.generate_folders)
        # show the dialog
        self.dlg.show()
        self.dlg.progress_bar.setValue(0)
        # Run the dialog event loop
        result = self.dlg.exec_()
        
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass 








