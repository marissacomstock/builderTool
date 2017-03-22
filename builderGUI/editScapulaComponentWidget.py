#*******************************************************************************
#
# $Id$ 
#*******************************************************************************

import os
import pymel.core as pm
import maya.cmds as cmds

from tip.qt.pkg import QtCore, QtGui, uic

from tip.maya.studio.core import naming
from tip.maya.puppet.tools.builderTool.builderGUI import editWidget

# __dialogs = list()

FILEPATH = os.path.dirname(__file__).replace('builderGUI', 'builderUI')

assignPath = os.path.join(FILEPATH, "editScapulaComponentWidget.ui")

QtCore.QCoreApplication.setOrganizationName("Tippett")
QtCore.QCoreApplication.setOrganizationDomain("tippett.com")


class AssignNewComponentWidget(editWidget.EditWidget):
    '''
    Corrective assign edit widget, modify basic widget for new group functionality

    TODO: Fix bug that causes create new group dialog to appear in top left corner

    '''

    refreshSignal = QtCore.Signal()

    def __init__(self, parent=None,
                widgetDict=None,
                pupList=None,
                textEditor=None,
                builderList=None,
                allBuilderWidget=None,
                editorWidget=None,
                compType=None,
                limb=None):
        super(AssignNewComponentWidget, self).__init__(parent,
                                                     assignPath=assignPath,
                                                     compType=compType)

        #init variables
        #EDITER variables
        self.pupList = pupList
        self.widgetDict = widgetDict
        self.textEditor = textEditor
        self.builderList = builderList
        self.allBuilderWidget = allBuilderWidget
        self.editorWidget = editorWidget
        self.limb = limb
        #COMPONENT variables
        self.startJoint = None
        self.side = None
        self.name = None
        self.endJoint = None
        self.orient = None
        self.orientLabel = None
        self.aim = None
        self.aimLabel = None

        #Connect Slots
        #COMPONENT SENDERS
        self.widget.startJoint_pushButton.clicked.connect(self.assignObject)
        self.widget.name_lineEdit.textChanged.connect(self.assignObject)
        self.widget.endJoint_pushButton.clicked.connect(self.assignObject)
        self.widget.orient_pushButton.clicked.connect(self.assignObject)
        self.widget.orientLabel_lineEdit.textChanged.connect(self.assignObject)
        self.widget.aim_pushButton.clicked.connect(self.assignObject)
        self.widget.aimLabel_lineEdit.textChanged.connect(self.assignObject)
        #ATTACH SENDERS
        self.widget.addDrivers_pushButton.clicked.connect(self.assignObject)
        self.widget.removeDrivers_pushButton.clicked.connect(self.assignObject)
        self.widget.addLabels_pushButton.clicked.connect(self.assignObject)
        self.widget.removeLabels_pushButton.clicked.connect(self.assignObject)
        self.widget.configNode_lineEdit.textChanged.connect(self.assignObject)
        self.widget.attachPoint_True.toggled.connect(self.assignObject)
        self.widget.attachPoint_False.toggled.connect(self.assignObject)
        self.widget.attachOrient_True.toggled.connect(self.assignObject)
        self.widget.attachOrient_False.toggled.connect(self.assignObject)
        self.widget.attachScale_True.toggled.connect(self.assignObject)
        self.widget.attachScale_False.toggled.connect(self.assignObject)

        #Default Buttons
        self.widget.ok_pushButton.clicked.connect(self.slotCreateGroup)
        self.widget.reset_pushButton.clicked.connect(self.slotReset)
        self.widget.cancel_pushButton.clicked.connect(self.close)

        #clean window
        self.update()
        self.slotReset()

    def initWindow(self, grpDict=None, attachDict=None):
        #COMPONENT variables
        if grpDict:
            if grpDict["startJoint"]:
                self.widget.startJoint_lineEdit.setText(grpDict["startJoint"])
            if grpDict["side"]:
                self.widget.side_lineEdit.setText(grpDict["side"])
                self.side = grpDict["side"]
            if grpDict["name"]:
                self.widget.name_lineEdit.setText(grpDict["name"])
                self.name = grpDict["name"]
            if grpDict["endJoint"]:
                self.widget.endJoint_lineEdit.setText(grpDict["endJoint"])
            if grpDict["orient"]:
                self.widget.orient_lineEdit.setText(grpDict["orient"])
            if grpDict["orientLabel"]:
                self.widget.orientLabel_lineEdit.setText(grpDict["orientLabel"])
            if grpDict["aim"]:
                self.widget.aim_lineEdit.setText(grpDict["aim"])
            if grpDict["aimLabel"]:
                self.widget.aimLabel_lineEdit.setText(grpDict["aimLabel"])
        #ATTACH variables
        if attachDict:
            if isinstance(attachDict["drivers"], (list,tuple)):
                for item in attachDict["drivers"]:
                    self.widget.driver_listWidget.addItem(item)
            else:
                if attachDict["drivers"]:
                    self.widget.driver_listWidget.addItem(attachDict["drivers"])
            if isinstance(attachDict["labels"], (list, tuple)):
                for item in attachDict["labels"]:
                    self.widget.labels_listWidget.addItem(item)
            else:
                if attachDict["labels"]:
                    self.widget.labels_listWidget.addItem(attachDict["labels"])
            if attachDict["config"]:
                self.widget.configNode_lineEdit.setText(attachDict["config"])
            self.widget.attachPoint_True.setChecked(True)
            self.widget.attachOrient_True.setChecked(False)
            self.widget.attachScale_True.setChecked(False)

        if self.limb:
            self.pupList.addItem(self.limb)
            #self.widgetDict[self.limb] = self
        self.update()
        self.setSceneGroupDict(self._groupDict)


    def assignObject(self):
        ''' fill form based on sender, then update group dict'''
        sender = self.sender()

        #COMPONENT SENDERS
        #start joint, side, name
        if sender is self.widget.startJoint_pushButton:
            self.widget.startJoint_lineEdit.setText(self._selectedItem()[0].shortName())
            if self.widget.startJoint_lineEdit.text().find("Lf") > -1:
                self.side = "left"
                self.widget.side_lineEdit.setText("left")
            elif self.widget.startJoint_lineEdit.text().find("Rt") > -1:
                self.side = "right"
                self.widget.side_lineEdit.setText("right")
            else:
                self.side = None
                self.widget.side_lineEdit.clear()
            if self.side:
                self.name = self._selectedItem()[0].split(naming.getSideName(self.side))[0][:-2]
                self.widget.name_lineEdit.setText(self.name)
            else:
                self.name = self._selectedItem()[0].split("_bnd")[0][:-2]
                self.widget.name_lineEdit.setText(self._selectedItem()[0].split("_bnd")[0][:-2])
        elif sender is self.widget.endJoint_pushButton:
            self.widget.endJoint_lineEdit.setText(self._selectedItem()[0].shortName())
        elif sender is self.widget.orient_pushButton:
            self.widget.orient_lineEdit.setText(self._selectedItem()[0].shortName())
        elif sender is self.widget.aim_pushButton:
            self.widget.aim_lineEdit.setText(self._selectedItem()[0].shortName())

        #ATTACH SENDERS
        #driversList
        elif sender is self.widget.addDrivers_pushButton:
            self._addItem(self.widget.driver_listWidget, self._selectedItem())
        elif sender is self.widget.removeDrivers_pushButton:
            self._removeItem(self.widget.driver_listWidget)
        #labelsList
        elif sender is self.widget.addLabels_pushButton:
            self._addItem(self.widget.labels_listWidget, self._selectedItem())
        elif sender is self.widget.removeLabels_pushButton:
            self._removeItem(self.widget.labels_listWidget)

        #Get limb Name
        self.limb = self.widget.name_lineEdit.text() + naming.getSideName(self.side)

        self.update()


    def setSceneGroupDict(self, groupDict):
        '''local dict to check if window has been edited. deal with later when creating comp chunks'''
        self.oldLimb = self.limb
        self._sceneGroupDict = groupDict


    def slotReset(self):
        ''' not sure why it didnt let me override this method'''

        self.widget.startJoint_lineEdit.clear()
        self.widget.side_lineEdit.clear()
        self.widget.name_lineEdit.clear()
        self.widget.endJoint_lineEdit.clear()
        self.widget.orient_lineEdit.clear()
        self.widget.orientLabel_lineEdit.clear()
        self.widget.aim_lineEdit.clear()
        self.widget.aimLabel_lineEdit.clear()
        self.widget.driver_listWidget.clear()
        self.widget.labels_listWidget.clear()
        self.widget.attachPoint_True.setChecked(True)
        self.widget.attachOrient_True.setChecked(False)
        self.widget.attachScale_True.setChecked(False)


    def _selectedItem(self):
        '''return selected'''
        sel = pm.ls(selection=True)
        return sel


    def update(self):
        '''update dict with latest edits'''
        #COMPONENT DICT
        self._groupDict['startJoint'] = str(self.widget.startJoint_lineEdit.text())
        self._groupDict['side'] = str(self.widget.side_lineEdit.text())
        self._groupDict['name'] = str(self.widget.name_lineEdit.text())
        self._groupDict['endJoint'] = self.widget.endJoint_lineEdit.text()
        self._groupDict['orient'] = self.widget.orient_lineEdit.text()
        self._groupDict['orientLabel'] = self.widget.orientLabel_lineEdit.text()
        self._groupDict['aim'] = self.widget.aim_lineEdit.text()
        self._groupDict['aimLabel'] = self.widget.aimLabel_lineEdit.text()

        #ATTACH DICT
        items = list()
        for index in xrange(self.widget.driver_listWidget.count()):
            items.append(self.widget.driver_listWidget.item(index).text())
        self._attachDict["drivers"] = items
        items = list()
        for index in xrange(self.widget.labels_listWidget.count()):
            items.append(self.widget.labels_listWidget.item(index).text())
        self._attachDict["labels"] = items
        self._attachDict["config"] = self.widget.configNode_lineEdit.text()
        self._attachDict["attachPoint"] = self.widget.attachPoint_True.isChecked()
        self._attachDict["attachOrient"] = self.widget.attachOrient_True.isChecked()
        self._attachDict["attachScale"] = self.widget.attachScale_True.isChecked()


    def closeEvent(self, event):
        self.settings.beginGroup("AssignNewGroupWidget")

        # set dict values
        for s in self._groupDict.keys():
            txt = self._groupDict[s]
            self.settings.setValue(s, txt)
        for s in self._attachDict.keys():
            txt = self._attachDict[s]
            self.settings.setValue(s, txt)

        self.settings.setValue("size", self.size())
        self.settings.setValue("pos", self.pos())
        self.settings.endGroup()


    def showEvent(self, event):
        ''' override showEvent, fill form with saved values'''
        super(AssignNewComponentWidget, self).showEvent(event)
        self.settings.beginGroup("AssignNewGroupWidget")
        #restore previous values
        for s in self._groupDict.keys():
            text = self.settings.value(s)
            if text:
                if s == 'startJoint':
                    self.widget.startJoint_lineEdit.setText(text.toString())
                elif s == 'side':
                    self.widget.side_lineEdit.setText(text.toString())
                elif s == 'name':
                    self.widget.name_lineEdit.setText(text.toString())
                elif s == 'endJoint':
                    self.widget.endJoint_lineEdit.setText(text)
                elif s == 'orient':
                    self.widget.orient_lineEdit.setText(text.toString())
                elif s == 'orientLabel':
                    self.widget.orientLabel_lineEdit.setText(text)
                elif s == 'aim':
                    self.widget.aim_lineEdit.setText(text.toString())
                elif s == 'aimLabel':
                    self.widget.aimLabel_lineEdit.setText(text)
                elif s == 'drivers':
                    for x in text:
                        self.widget.driver_listWidget.addItem(x.toString())
                elif s == 'labels':
                    for x in text:
                        self.widget.labels_listWidget.addItem(x.toString())
                elif s == 'attachPoint':
                    self.widget.attachPoint_True.setChecked(bool(text.toString()))
                elif s == 'attachOrient':
                    self.widget.attachPoint_True.setChecked(bool(text.toString()))
                elif s == 'attachScale':
                    self.widget.attachPoint_True.setChecked(bool(text.toString()))


    def slotCreateGroup(self):
        ''' CHECK IF ALREADY A GROUP WORK ON LATER WHEN BUILDING CHUNKS, make more robust??
        :type self: object
        '''

        try:
            cmds.undoInfo(openChunk=True)

            #update puppet component list
            items = []
            for index in xrange(self.pupList.count()):
                items.append(self.pupList.item(index).text())
            try:
                items.index(self.limb)
            except:
                if self.limb != self.oldLimb:
                    if self.oldLimb:
                        self.pupList.takeItem(items.index(self.oldLimb))
                self.pupList.addItem(self.limb)

            #reset widget pointer
            self.widgetDict[self.limb] = self

            self.setSceneGroupDict(self._groupDict)
            self.hide()
            self.refreshSignal.emit()

        finally:
            cmds.undoInfo(closeChunk=True)


    def returnGroupDictObjects(self):
        '''return limb, group dict, and attachdict to the all builder'''
        #ONLY RETURN IF EDITED
        return self.limb, self._groupDict, self._attachDict

