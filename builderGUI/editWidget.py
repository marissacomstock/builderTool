#*******************************************************************************
# Copyright (c) 2013 Tippett Studio. All rights reserved.
#
# $Id$ 
#*******************************************************************************

import os
import pymel.core as pm
import maya.cmds as cmds

from tip.qt.pkg import QtCore, QtGui, uic

from tip.maya.studio.core import checks
from tip.maya.studio.core import naming
from tip.maya.puppet.tools.builderTool.builderGUI import attachWidget
from tip.maya.puppet.tools.builderTool.builderUtils import attachInfo
from tip.maya.puppet.tools.builderTool.builderUtils import hierInfo

# __dialogs = list()

QtCore.QCoreApplication.setOrganizationName("Tippett")
QtCore.QCoreApplication.setOrganizationDomain("tippett.com")

FILEPATH = os.path.dirname(__file__).replace('builderGUI', 'builderUI')
assignPath = os.path.join(FILEPATH, "editFKComponentWidget.ui")

HIERWIDGET = os.path.join(FILEPATH, "hierarchyGroupWidget.ui")
EXECWIDGET = os.path.join(FILEPATH, "executeWidget.ui")

#################################################################################

class EditWidget(QtGui.QDialog):

    def __init__(self,
                 parent=None,
                 componentDict=None,
                 componentWidget=None,
                 compType='FKComponent',
                 assignPath=None,
                 limb=None,
                 puppet=None):

        super(EditWidget, self).__init__()

        #Init Default variables for Builder
        self.limb = limb
        self.oldLimb = None
        self.puppet = puppet
        self.compType = compType
        self.componentDict = componentDict
        self.componentListWidget = componentWidget

        if assignPath:
            self.compWidget = uic.loadUi(assignPath)

        #Add Hierarchy Widget
        self.hierWidget = uic.loadUi(HIERWIDGET)

        #Create Attach Widget
        attachObj = attachWidget.AttachWidget()
        self.attachWidget = attachObj

        #Add Execute Widget
        self.execWidget = uic.loadUi(EXECWIDGET)

        layout = QtGui.QVBoxLayout()
        if assignPath:
            layout.addWidget(self.compWidget)
        layout.addWidget(self.hierWidget)
        layout.addWidget(self.attachWidget)
        layout.addWidget(self.execWidget)
        self.setLayout(layout)

        #other settings
        #hierWidget width/height
        if assignPath:
            compHeight = self.compWidget.height()
        else:
            compHeight = 0
        height = compHeight + self.hierWidget.height() + self.attachWidget.height() + self.execWidget.height()
        self.setMinimumSize(500, height - 100)
        self.setMaximumSize(500, height - 100)

        self.settings = QtCore.QSettings()

        #Open in the Middle of the Screen
        screenWidth, screenHeight = self.screenCenter()
        self.move(QtCore.QPoint(screenWidth, screenHeight))

        #create dicts
        self._sceneGroupDict = dict()
        self._hierarchyAttrList = dict()
        self._attachAttrList = dict()

        if assignPath:
            self.compWidget.widget_groupBox.toggled.connect(self.showAttach)
        self.hierWidget.widget_groupBox.toggled.connect(self.showAttach)
        self.attachWidget.widget_groupBox.toggled.connect(self.showAttach)

        #ATTACH
        #attach widget things
        self.attachWidget.attachPoint_groupBox.clicked.connect(self.assignObject)
        self.attachWidget.attachPointNode_groupBox.clicked.connect(self.assignObject)
        self.attachWidget.attachOrient_groupBox.clicked.connect(self.assignObject)
        self.attachWidget.attachOrientNode_groupBox.clicked.connect(self.assignObject)

        #ATTACH SENDERS
        self.attachWidget.driven_pushButton.clicked.connect(self.assignObject)
        self.attachWidget.addDrivers_pushButton.clicked.connect(self.assignObject)
        self.attachWidget.removeDrivers_pushButton.clicked.connect(self.assignObject)
        self.attachWidget.loadConfig_pushButton.clicked.connect(self.assignObject)
        self.attachWidget.loadAttachPoint_pushButton.clicked.connect(self.assignObject)
        self.attachWidget.loadAttachOrient_pushButton.clicked.connect(self.assignObject)


        self.execWidget.cancel_pushButton.clicked.connect(self.close)

        #clean window
        self.slotReset()
        self.update()

    def assignObject(self, sender=None):
        if not sender:
            sender = self.sender()

        #driven
        if sender == self.attachWidget.driven_pushButton:
            sel = pm.ls(selection=True)
            if sel:
                self.attachWidget.driven_lineEdit.setText(sel[0])

        #add drivers
        if sender is self.attachWidget.addDrivers_pushButton:
            sel = pm.ls(selection=True)
            numRows = self.attachWidget.drivers_tableWidget.rowCount()
            for i, s in enumerate(sel):
                name = naming.TipName(name=s)
                self.attachWidget.drivers_tableWidget.insertRow(numRows + i)
                self.attachWidget.drivers_tableWidget.setItem(numRows + i, 0, QtGui.QTableWidgetItem(str(s)))
                self.attachWidget.drivers_tableWidget.setItem(numRows + i, 1, QtGui.QTableWidgetItem(str(name.base)))

        #remove drivers
        if sender is self.attachWidget.removeDrivers_pushButton:
            for item in self.attachWidget.drivers_tableWidget.selectedItems():
                self.attachWidget.drivers_tableWidget.setItem(item.row())

        #config
        if sender is self.attachWidget.loadConfig_pushButton:
            sel = pm.ls(selection=True)
            if sel:
                self.attachWidget.configNode_lineEdit.setText(str(sel[0]))

        #attach point
        if sender is self.attachWidget.loadAttachPoint_pushButton:
            sel = pm.ls(selection=True)
            if sel:
                self.attachWidget.loadAttachPoint_lineEdit.setText(str(sel[0]))

        #attach orient
        if sender is self.attachWidget.loadAttachOrient_pushButton:
            sel = pm.ls(selection=True)
            if sel:
                self.attachWidget.loadAttachOrient_lineEdit.setText(str(sel[0]))

        #checkboxes
        if sender is self.attachWidget.attachPoint_groupBox:
            if self.attachWidget.attachPoint_groupBox.isChecked():
                self.attachWidget.attachPointNode_groupBox.setChecked(False)
        if sender is self.attachWidget.attachPointNode_groupBox:
            if self.attachWidget.attachPointNode_groupBox.isChecked():
                self.attachWidget.attachPoint_groupBox.setChecked(False)

        if sender is self.attachWidget.attachOrient_groupBox:
            if self.attachWidget.attachOrient_groupBox.isChecked():
                self.attachWidget.attachOrientNode_groupBox.setChecked(False)
        if sender is self.attachWidget.attachOrientNode_groupBox:
            if self.attachWidget.attachOrientNode_groupBox.isChecked():
                self.attachWidget.attachOrient_groupBox.setChecked(False)

        self.updateHierarchyAttrs()
        self.updateAttachAttrs()


    def getHierarchyAttrs(self):
        ''' Get Hierarchy Attrs'''

        return self._hierarchyAttrList

    def setHierarchyAttrs(self, hierDict):

        if 'rootGroup' in hierDict:
            self.hierWidget.rootGroup_checkBox.setChecked(hierDict['rootGroup'])
        else:
            self.hierWidget.rootGroup_checkBox.setChecked(True)
        if 'localGroup' in hierDict:
            self.hierWidget.localGroup_checkBox.setChecked(hierDict['localGroup'])
        else:
            self.hierWidget.localGroup_checkBox.setChecked(True)
        if 'worldGroup' in hierDict:
            self.hierWidget.worldGroup_checkBox.setChecked(hierDict['worldGroup'])
        else:
            self.hierWidget.worldGroup_checkBox.setChecked(False)
        if 'localPosition' in hierDict:
            self.hierWidget.localPosition_True.setChecked(hierDict['localPosition'])
        else:
            self.hierWidget.localPosition_False.setChecked(True)

        self.updateHierarchyAttrs()

    def updateHierarchyAttrs(self):
        '''Set Hierarchy Attr dict'''

        self._hierarchyAttrList = [self.hierWidget.rootGroup_checkBox.isChecked(),
                                   self.hierWidget.localGroup_checkBox.isChecked(),
                                   self.hierWidget.worldGroup_checkBox.isChecked(),
                                   self.hierWidget.localPosition_True.isChecked()]

    def getAttachAttrs(self):
        return self._attachAttrList

    def setAttachAttrs(self, attachDict):

        #ATTACH variables
        if 'driven' in attachDict:
            self.attachWidget.driven_lineEdit.setText(attachDict['driven'])
        if 'drivers' in attachDict:
            for i, item in enumerate(attachDict['drivers']):
                self.attachWidget.drivers_tableWidget.setItem(i, 0,
                                                      QtGui.QTableWidgetItem(str(item)))
        if 'labels' in attachDict:
            for i, item in enumerate(attachDict['labels']):
                self.attachWidget.drivers_tableWidget.setItem(i, 1,
                                                      QtGui.QTableWidgetItem(str(item)))
        if 'config' in attachDict:
            self.attachWidget.configNode_lineEdit.setText(attachDict['config'])
        if 'prefix' in attachDict:
            self.attachWidget.attrPrefix_lineEdit.setText(attachDict['prefix'])
        if 'point' in attachDict:
            self.attachWidget.point_checkBox.setChecked(attachDict['point'])
        if 'orient' in attachDict:
            self.attachWidget.orient_checkBox.setChecked(attachDict['orient'])
        if 'scale' in attachDict:
            self.attachWidget.scale_checkBox.setChecked(attachDict['scale'])
        if 'attachPoint' in attachDict:
            if isinstance(attachDict['attachPoint'], bool):
                self.attachWidget.attachPoint_groupBox.setChecked(True)
                self.attachWidget.attachPointNode_groupBox.setChecked(False)
                if attachDict['attachPoint']:
                    self.attachWidget.attachPoint_True.setChecked(True)
                else:
                    self.attachWidget.attachPoint_False.setChecked(True)
            else:
                self.attachWidget.attachPoint_groupBox.setChecked(False)
                self.attachWidget.attachPointNode_groupBox.setChecked(True)
                self.attachWidget.loadAttachPoint_lineEdit.setText(attachDict['attachPoint'])
        if 'attachOrient' in attachDict:
            if isinstance(attachDict['attachOrient'], bool):
                self.attachWidget.attachOrient_groupBox.setChecked(True)
                self.attachWidget.attachOrientNode_groupBox.setChecked(False)
                if attachDict['attachOrient']:
                    self.attachWidget.attachOrient_True.setChecked(True)
                else:
                    self.attachWidget.attachOrient_False.setChecked(True)
            else:
                self.attachWidget.attachOrient_groupBox.setChecked(False)
                self.attachWidget.attachOrientNode_groupBox.setChecked(True)
                self.attachWidget.loadAttachOrient_lineEdit.setText(attachDict['attachOrient'])
        if 'attachScale' in attachDict:
            if isinstance(attachDict['attachScale'], bool):
                self.attachWidget.attachScale_groupBox.setChecked(True)
                self.attachWidget.attachScaleNode_groupBox.setChecked(False)
                if attachDict['attachScale']:
                    self.attachWidget.attachScale_True.setChecked(True)
                else:
                    self.attachWidget.attachScale_False.setChecked(True)
            else:
                self.attachWidget.attachScale_groupBox.setChecked(False)
                self.attachWidget.attachScaleNode_groupBox.setChecked(True)
                self.attachWidget.loadAttachScale_lineEdit.setText(attachDict['attachOrient'])
        if 'multiAttr':
            self.attachWidget.multiAttrSwitch_checkBox.setChecked(attachDict['multiAttr'])
        if 'switch':
            self.attachWidget.multiAttrSwitch_checkBox.setChecked(attachDict['switch'])

        self.updateAttachAttrs()

    def updateAttachAttrs(self):

        #get control shapes and indeces
        drivers = list()
        labels = list()
        numRows = self.attachWidget.drivers_tableWidget.rowCount()
        for x in range(0, numRows):
            if self.attachWidget.drivers_tableWidget.item(x, 0):
                drivers.append(self.attachWidget.drivers_tableWidget.item(x, 0).text())
            if self.attachWidget.drivers_tableWidget.item(x, 1):
                labels.append(self.attachWidget.drivers_tableWidget.item(x, 1).text())

        if self.attachWidget.attachPoint_groupBox.isChecked():
            pointAttach = self.attachWidget.attachPoint_True.isChecked()
        else:
            pointAttach = self.attachWidget.loadAttachPoint_lineEdit.text()
        if self.attachWidget.attachOrient_groupBox.isChecked():
            orientAttach = self.attachWidget.attachOrient_True.isChecked()
        else:
            orientAttach = self.attachWidget.loadAttachOrient_lineEdit.text()
        if self.attachWidget.attachScale_groupBox.isChecked():
            scaleAttach = self.attachWidget.attachScale_True.isChecked()
        else:
            scaleAttach = self.attachWidget.loadAttachScale_lineEdit.text()

        self._attachAttrList = [self.attachWidget.driven_lineEdit.text(),
                                drivers,
                                labels,
                                self.attachWidget.configNode_lineEdit.text(),
                                self.attachWidget.attrPrefix_lineEdit.text(),
                                self.attachWidget.point_checkBox.isChecked(),
                                self.attachWidget.orient_checkBox.isChecked(),
                                self.attachWidget.scale_checkBox.isChecked(),
                                pointAttach,
                                orientAttach,
                                scaleAttach,
                                self.attachWidget.multiAttrSwitch_checkBox.isChecked(),
                                self.attachWidget.constraintSwitch_checkBox.isChecked()]


    def showAttach(self):
        winHeight = self.height()
        sender = self.sender()

        #checkboxes
        if sender is self.attachWidget.widget_groupBox:
            widget = self.attachWidget
        elif sender is self.hierWidget.widget_groupBox:
            widget = self.hierWidget
        elif sender is self.compWidget.widget_groupBox:
            widget = self.compWidget

        widgetHeight = widget.height()

        if widget.widget_groupBox.isChecked():
            winHeight += widget.widget_GroupFrame.height()
            widgetHeight += widget.widget_GroupFrame.height()
            widget.widget_GroupFrame.show()
        else:
            winHeight -= widget.widget_GroupFrame.height()
            widgetHeight -= widget.widget_GroupFrame.height()
            widget.widget_GroupFrame.hide()

        widget.setMinimumSize(widget.width(), widgetHeight)
        widget.setMaximumSize(widget.width(), widgetHeight)
        self.setMinimumSize(self.width(), winHeight)
        self.setMaximumSize(self.width(), winHeight)

    def screenCenter(self):
        resolution = QtGui.QDesktopWidget().screenGeometry()
        width = (resolution.width() / 2) - (self.frameSize().width() / 2)
        height = (resolution.height() / 2) - (self.frameSize().height() / 2)
        return width, height

    def setTitle(self):
        if self.limb:
            self.setWindowTitle('%s%s Component' % (self.limb[0].title(), self.limb[1:]))
        else:
            self.setWindowTitle('Create New %s' % self.compType.title())
        self.compWidget.widget_groupBox.setTitle('%s' % self.compType.upper())

    def slotReset(self):
        #hier widget
        self.hierWidget.rootGroup_checkBox.setChecked(True)
        self.hierWidget.localGroup_checkBox.setChecked(True)
        self.hierWidget.worldGroup_checkBox.setChecked(False)
        self.hierWidget.localPosition_True.setChecked(True)

        #attach Group
        self.attachWidget.driven_lineEdit.clear()
        numRows = self.attachWidget.drivers_tableWidget.rowCount()
        for row in range(0, numRows):
            self.attachWidget.drivers_tableWidget.setItem(row, 0, None)
            self.attachWidget.drivers_tableWidget.setItem(row, 1, None)
        self.attachWidget.configNode_lineEdit.clear()
        self.attachWidget.attrPrefix_lineEdit.clear()
        self.attachWidget.point_checkBox.setChecked(True)
        self.attachWidget.orient_checkBox.setChecked(True)
        self.attachWidget.scale_checkBox.setChecked(False)
        self.attachWidget.attachPoint_groupBox.setChecked(True)
        self.attachWidget.attachPoint_True.setChecked(True)
        self.attachWidget.attachOrient_groupBox.setChecked(True)
        self.attachWidget.attachOrient_True.setChecked(True)
        self.attachWidget.attachScale_False.setChecked(True)
        self.attachWidget.multiAttrSwitch_checkBox.setChecked(True)
        self.attachWidget.constraintSwitch_checkBox.setChecked(True)

    def setSlot(self, oldLimb=None):

        if oldLimb != self.limb:
            for item in self.componentDict.keys():
                if item == oldLimb:
                    del self.componentDict[item]
                for index in reversed(range(0, self.componentListWidget.count())):
                    if oldLimb == self.componentListWidget.item(index).text():
                        self.componentListWidget.takeItem(index)
                break
            self.componentListWidget.addItem(self.limb)
        else:
            found = False
            for index in reversed(range(0, self.componentListWidget.count())):
                if self.limb == self.componentListWidget.item(index).text():
                    found = True
                    pass
            if not found:
                self.componentListWidget.addItem(self.limb)
        self.componentDict[self.limb] = self
        self.hide()
        self.refreshSignal.emit()

        self.setHierString(oldLimb)
        self.setAttachString(oldLimb)

        #remove component
        self.compObj.removeComponent(oldLimb)
        #add new component
        self.compObj.addComponent(self.limb)
        self.puppet.buildComponents.setLocked(False)
        self.puppet.buildComponents.set(self.compObj.toJson(), type='string')
        self.puppet.buildComponents.setLocked(True)

    def setHierString(self, oldLimb):

        #delete old attribute if the limb name has changed
        if oldLimb != self.limb:
            if self.puppet.hasAttr('%s_hier' % oldLimb):
                pm.setAttr('%s.%s_hier' % (self.puppet, oldLimb), lock=False)
                pm.deleteAttr('%s.%s_hier' % (self.puppet, oldLimb))

        if self.puppet and self.limb:
            if not self.puppet.hasAttr('%s_hier' % self.limb):
                self.puppet.addTag('%s_hier' % self.limb)

            hierObj = hierInfo.HierInfo()

            hierObj.setHierValues(rootGroup=self._hierarchyAttrList[0],
                                  localGroup=self._hierarchyAttrList[1],
                                  worldGroup=self._hierarchyAttrList[2],
                                  localPosition=self._hierarchyAttrList[3])

            #unlock string
            pm.setAttr('%s.%s_hier' % (self.puppet, self.limb), lock=False)
            pm.setAttr('%s.%s_hier' % (self.puppet, self.limb), hierObj.toJson(), type='string')
            pm.setAttr('%s.%s_hier' % (self.puppet, self.limb), lock=True)

    def setAttachString(self, oldLimb):

        #delete old attribute if the limb name has changed
        if oldLimb != self.limb:
            if self.puppet.hasAttr('%s_attach' % oldLimb):
                pm.setAttr('%s.%s_attach' % (self.puppet, oldLimb), lock=False)
                pm.deleteAttr('%s.%s_attach' % (self.puppet, oldLimb))

        if self.puppet and self.limb:

            if not self.puppet.hasAttr('%s_attach' % self.limb):
                self.puppet.addTag('%s_attach' % self.limb)

            attachObj = attachInfo.AttachInfo()

            attachObj.setAttachValues(attach=False,
                                  driven=self._attachAttrList[0],
                                  drivers=self._attachAttrList[1],
                                  labels=self._attachAttrList[2],
                                  prefix=self._attachAttrList[4],
                                  point=self._attachAttrList[5],
                                  orient=self._attachAttrList[6],
                                  scale=self._attachAttrList[7],
                                  switch=self._attachAttrList[12],
                                  multiAttr=self._attachAttrList[11],
                                  config=self._attachAttrList[3],
                                  attachPoint=self._attachAttrList[8],
                                  attachOrient=self._attachAttrList[9],
                                  attachScale=self._attachAttrList[10])

            #unlock string
            pm.setAttr('%s.%s_attach' % (self.puppet, self.limb), lock=False)
            pm.setAttr('%s.%s_attach' % (self.puppet, self.limb), attachObj.toJson(), type='string')
            pm.setAttr('%s.%s_attach' % (self.puppet, self.limb), lock=True)
