# -*- coding: utf-8 -*-
"""
/***************************************************************************
 FolderCreator
                                 A QGIS plugin
 This plugin automates the creation of folders for each settlements in a work order
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2022-04-29
        copyright            : (C) 2022 by Integration Environment & Energy
        email                : ejolaiya@integration.org
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load FolderCreator class from file FolderCreator.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .folder_creator import FolderCreator
    return FolderCreator(iface)
