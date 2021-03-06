# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DDGStreetImages
                                 A QGIS plugin
 The plugin open DDG street images in the browser
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2018-10-08
        git sha              : $Format:%H$
        copyright            : (C) 2018 by COWI A/S
        email                : jxa@cowi.dk
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
import uuid
import requests
import json
import os

from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QObject, QUrl
from PyQt5.QtGui import QIcon, QDesktopServices
from PyQt5.QtWidgets import QAction, QPushButton, QDialog, QSizePolicy, QGridLayout, QDialogButtonBox, QMessageBox

# Initialize Qt resources from file resources.py
from qgis._core import Qgis, QgsProject
from qgis._gui import QgsMessageBar, QgsMapToolEmitPoint
from qgis.utils import iface

from .resources import *
# Import the code for the dialog
from .ddg_street_images_dialog import DDGStreetImagesDialog
import os.path

unikId = ""


def makeUrl(thisUuid, login, password, project, xCoord, yCoord, srid, maximize, assLayers, vLayers):
    thisUrl = 'https://cmv.cowi.com/?'
    thisUrl += 'msid=' + thisUuid
    thisUrl += '&u=' + login
    thisUrl += '&p=' + password
    thisUrl += '&origin=desktop'
    thisUrl += '&cmd=state'
    thisUrl += '&project=' + project
    thisUrl += '&x=' + xCoord
    thisUrl += '&y=' + yCoord
    thisUrl += '&srid=' + srid
    thisUrl += '&maximize=' + maximize
    thisUrl += '&assLayers=' + assLayers
    thisUrl += '&vLayers=' + vLayers
    return str(thisUrl)


class DDGStreetImages:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """QGIS Plugin Implementation."""

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        # refernce to map canvas
        self.canvas = self.iface.mapCanvas()
        # out click tool will emit a QgsPoint on every click
        self.clickTool = QgsMapToolEmitPoint(self.canvas)
        # create our GUI dialog
        # self.dlg =ZoomerDialog()

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        self.action = QAction(QIcon(":/plugins/ddg_street_images/icon.png"), \
                              "klik i kort", self.iface.mainWindow())
        # connect the action to the run method
        self.action.triggered.connect(self.run)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("&DDG Street Images", self.action)

        # connect our custom function to a clickTool signal that the canvas was clicked
        result = self.clickTool.canvasClicked.connect(self.handleMouseDown)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        self.iface.removePluginMenu("&DDG Street Images", self.action)
        self.iface.removeToolBarIcon(self.action)

    def run(self):
        """Run method that performs all the real work"""
        self.canvas.setMapTool(self.clickTool)

    def handleMouseDown(self, point, button):

        #		crsSrc = QgsCoordinateReferenceSystem(4326)    # WGS 84
        #		crsDest = QgsCoordinateReferenceSystem(25832)  # WGS 84 / UTM zone 33N
        #		xform = QgsCoordinat    eTransform(crsSrc, crsDest)
        # pt1 = xform.transform(QgsPoint(18,5))
        #		x, y = xform.transform(18,5)
        #		QMessageBox.information(self.iface.mainWindow(),"Info", str(x))

        global unikId
        id = 0

        crs = QgsProject.instance()
        authid = crs.crs().authid()
        if authid.find(":") > 0:
            temp = authid.split(":")
            id = temp[1]

        if not str(id) == str(4326) and not str(id) == str(3857) and not str(id) == str(25832) and not str(id) == str(
                3009):
            QMessageBox.information(self.iface.mainWindow(), "Info", "du har valgt SRID: " + str(
                id) + ", men kun følgende er supporteret 3009, 3857, 4326, 25832")
            return

        subpath = "QGIS\QGIS3\profiles\default\python\plugins\ddg_street_images"
        path = os.path.join(os.getenv("APPDATA"), subpath)

        if os.path.exists(path) == "false":
            QMessageBox.information(self.iface.mainWindow(), "Info", "kunne ikke finde config fil")
            return

        completePath = path + '\config.txt'
        text = open(completePath).read()
        json_result = json.loads(text)

        login = str(json_result["login"])
        password = str(json_result["password"])
        project = str(json_result["project"])
        vLayers = str(json_result["vLayers"])
        hLayers = str(json_result["hLayers"])
        maximize = str(json_result["maximize"])
        xCoord = str(point.x())
        yCoord = str(point.y())
        srid = str(id)
        dssLayers = str(json_result["dssLayers"])
        assLayers = str(json_result["assLayers"])
        ssTrigger = str(json_result["ssTrigger"])

        if unikId == "":
            unikId = str(uuid.uuid4())
            newUrl = makeUrl(unikId, login, password, project, xCoord, yCoord, srid, maximize, assLayers, vLayers)
            result = QDesktopServices.openUrl(QUrl(newUrl))
            # QMessageBox.information(self.iface.mainWindow(), "Info", "start link")
        else:
            headers = {'content-type': 'application/x-www-form-urlencoded'}
            token = unikId
            origin = "desktop"
            messagetext = {'Cmd': 'state', 'Project': project, 'vLayers': vLayers, 'hLayers': hLayers,
                           'Maximize': maximize, 'Address': '', 'Parcels': '', 'propertyId': '', 'X': xCoord,
                           'Y': yCoord, 'Srid': srid, 'dssLayers': dssLayers, 'assLayers': assLayers,
                           'ssTrigger': ssTrigger}
            # messagetext = {'Cmd':'state','Project':'SKM - Vurderingsstyrelsen-1','vLayers':'Skaermkort;DDG 2016 Complete','hLayers':'DDG 2016 Complete;Husnummer foto','Maximize':'DDG 2016 Complete','Address':'Merkurvej 16, 7080 Børkop','Parcels':'1170252-6cc','propertyId':'18567836','X':'542671.94','Y':'6168845.69','Srid':'25832','dssLayers':'','assLayers':'','ssTrigger':''}

            r = requests.post("https://cmv.cowi.com/Messageshab/PutMessage",
                              data="origin=desktop&token=" + token + "&isjson=true&messageText=" + json.dumps(
                                  messagetext), headers=headers)
            # QMessageBox.information(self.iface.mainWindow(), "Info", str(r.status_code))
            if r.status_code == 205:
                newUrl = makeUrl(unikId, login, password, project, xCoord, yCoord, srid, maximize, assLayers, vLayers)
                result = QDesktopServices.openUrl(QUrl(newUrl))
