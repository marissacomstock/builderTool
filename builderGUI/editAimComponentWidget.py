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
from tip.maya.puppet.tools.builderTool.builderUtils import buildInfo
from tip.maya.studio.tipModules import controller

# __dialogs = list()

FILEPATH = os.path.dirname(__file__).replace('builderGUI', 'builderUI')

ASSIGNPATH = os.path.join(FILEPATH, "editAimComponentWidget.ui")

QtCore.QCoreApplication.setOrganizationName("Tippett")
QtCore.QCoreApplication.setOrganizationDomain("tippett.com")


class AssignNewComponentWidget(editWidget.EditWidget):
    '''
    Corrective assign edit widget, modify basic widget for new group functionality

    TODO: Fix bug that causes create new group dialog to appear in top left corner

    '''

    refreshSignal = QtCore.Signal()

    def __init__(self, parent=None,
                 componentDict=None,
                 componentWidget=None,
                 compType='Aim',
                 limb=None,
                 puppet=None,
                 compObj=None):

        super(AssignNewComponentWidget, self).__init__(parent,
                                                       componentDict=componentDict,
                                                       componentWidget=componentWidget,
                                                       assignPath=ASSIGNPATH,
                                                       compType=compType)
        #init variables
        #EDITER variables
        self.compType = compType
        self.limb = limb
        self.puppet = puppet
        self.compObj = compObj

        #init component list
        self._componentAttrList = list()

        #Connect Slots
        #COMPONENT ACTIVE SENDERS
        self.compWidget.startJoint_pushButton.clicked.connect(self.assignObject)
        self.compWidget.endListAdd_pushButton.clicked.connect(self.assignObject)
        self.compWidget.endListRemove_pushButton.clicked.connect(self.assignObject)
        self.compWidget.aimAdd_pushButton.clicked.connect(self.assignObject)
        self.compWidget.aimRemove_pushButton.clicked.connect(self.assignObject)

        #reset
        self.execWidget.reset_pushButton.clicked.connect(self.slotReset)
        self.execWidget.ok_pushButton.clicked.connect(self.setSlot)


        #clean window
        self.slotReset()
        self.update()

    def initWindow(self, buildDict=None, hierDict=None, attachDict=None):
        #COMPONENT variables

        if buildDict:
            #startJoint
            if 'startJoint' in buildDict:
                self.compWidget.startJoint_lineEdit.setText(buildDict['startJoint'])
            if 'name' in buildDict:
                self.compWidget.name_lineEdit.setText(buildDict['name'])
            if 'side' in buildDict:
                if buildDict['side'] == 'left':
                    self.compWidget.left_radioButton.setCcontrolIndex_tableWidgethecked(True)
                elif buildDict['side'] == 'right':
                    self.compWidget.right_radioButton.setChecked(True)
                else:
                    self.compWidget.center_radioButton.setChecked(True)
                self.side = buildDict['side']
            if 'endList' in buildDict and buildDict['endList']:
                for i, item in enumerate(buildDict['endList']):
                    self.compWidget.endList_listWidget.insertItem(i, item)
            if 'aimJoints' in buildDict and buildDict['aimJoints']:
                numRows = self.compWidget.aim_tabelWidget.rowCount()
                for x in range(0, numRows):
                    self.compWidget.aim_tabelWidget.removeRow(x)

                for i, item in enumerate(buildDict['aimJoints']):
                    self.compWidget.aim_tabelWidget.insertRow(i)
                    self.compWidget.aim_tabelWidget.setItem(i, 0,
                                                          QtGui.QTableWidgetItem(str(item)))
                    if 'aimSockets' in buildDict:
                        self.compWidget.aim_tabelWidget.setItem(i, 1,
                                                          QtGui.QTableWidgetItem(str(buildDict['aimSockets'][i])))
            if 'controlOffset' in buildDict:
                self.compWidget.controlOffset_doubleSpinBox.setValue(buildDict['controlOffset'])
            if 'controlScale' in buildDict:
                self.compWidget.controlScale_doubleSpinBox.setValue(buildDict['controlScale'])
            if 'style' in buildDict:
                if isinstance(buildDict['style'], str) or isinstance(buildDict['style'], unicode):
                    index = controller.PUPPET_CONTROL_SHAPE_TYPES.index(buildDict['style'])
                    self.compWidget.controlStyle_comboBox.setCurrentIndex(index)
                else:
                    self.compWidget.controlStyle_comboBox.setCurrentIndex(buildDict['style'])

        #init hier and attach attrs
        if hierDict:
            self.setHierarchyAttrs(hierDict)
        if attachDict:
            self.setAttachAttrs(attachDict)
        self.update()

    def assignObject(self):
        ''' fill form based on sender, then update group dict'''
        sender = self.sender()

        #COMPONENT SENDERS
        #start joint, side, name
        if sender is self.compWidget.startJoint_pushButton:
            sel = pm.ls(selection=True)
            if sel:
                self.compWidget.startJoint_lineEdit.setText(sel[0].shortName())
                name = naming.TipName(self.compWidget.startJoint_lineEdit.text())
                self.compWidget.name_lineEdit.setText(name.base)
                if name.isSideLeft():
                    self.side = 'left'
                    self.compWidget.left_radioButton.setChecked(True)
                elif name.isSideRight():
                    self.side = 'right'
                    self.compWidget.right_radioButton.setChecked(True)
                else:
                    self.side = None
                    self.compWidget.center_radioButton.setChecked(True)
                self.limb = self.compWidget.name_lineEdit.text() + naming.getSideName(self.side)
                self.attachWidget.attrPrefix_lineEdit.setText(self.limb)
        #endList
        elif sender is self.compWidget.endListAdd_pushButton:
            sel = pm.ls(selection=True)
            if sel:
                for item in pm.ls(selection=True):
                    self.compWidget.endList_listWidget.addItem(str(item))
        elif sender is self.compWidget.endListRemove_pushButton:
            for item in self.compWidget.endList_listWidget.selectedItems():
                self.compWidget.endList_listWidget.removeItemWidget(item)
        #aim List
        elif sender is self.compWidget.aimAdd_pushButton:
            sel = pm.ls(selection=True)
            numRows = self.compWidget.aim_tabelWidget.rowCount()
            if sel:
                self.compWidget.aim_tabelWidget.insertRow(numRows)
                self.compWidget.aim_tabelWidget.setItem(numRows, 0, QtGui.QTableWidgetItem(str(sel[0])))
                self.compWidget.aim_tabelWidget.setItem(numRows, 1, QtGui.QTableWidgetItem(str(sel[1])))
        elif sender is self.compWidget.aimRemove_pushButton:
            for item in self.compWidget.aim_tabelWidget.selectedItems():
                self.attachWidget.aim_tabelWidget.removeRow(item.row())

        #also excute overridden assign object
        super(AssignNewComponentWidget, self).assignObject(sender)

        self.update()

    def slotReset(self):
        ''' not sure why it didnt let me override this method'''

        self.compWidget.startJoint_lineEdit.clear()
        self.compWidget.center_radioButton.setChecked(True)
        self.compWidget.name_lineEdit.clear()
        self.compWidget.endList_listWidget.clear()
        self.compWidget.controlOffset_doubleSpinBox.setValue(1)
        self.compWidget.controlScale_doubleSpinBox.setValue(1)
        self.compWidget.controlStyle_comboBox.setCurrentIndex(0)

        super(AssignNewComponentWidget, self).slotReset()

    def update(self):
        '''update dict with latest edits'''
        #COMPONENT DICT

        #get endlist
        endList = list()
        for index in xrange(self.compWidget.endList_listWidget.count()):
            endList.append(self.compWidget.endList_listWidget.item(index).text())

        #get control shapes and indeces
        aimJoints = list()
        aimSockets = list()
        numRows = self.compWidget.aim_tabelWidget.rowCount()
        for x in range(0, numRows):
            if self.compWidget.aim_tabelWidget.item(x, 0):
                aimJoints.append(self.compWidget.aim_tabelWidget.item(x, 0).text())
                aimSockets.append(self.compWidget.aim_tabelWidget.item(x, 1).text())

        #get side
        if self.compWidget.center_radioButton.isChecked():
            self.side = None
        elif self.compWidget.left_radioButton.isChecked():
            self.side = 'left'
        else:
            self.side = 'right'

        #Get limb Name
        self.limb = self.compWidget.name_lineEdit.text() + naming.getSideName(self.side)

        self._componentAttrList = [str(self.compWidget.startJoint_lineEdit.text()),
                           str(self.compWidget.name_lineEdit.text()),
                           self.side,
                           endList,
                           aimJoints,
                           aimSockets,
                           self.compWidget.controlOffset_doubleSpinBox.value(),
                           self.compWidget.controlScale_doubleSpinBox.value(),
                           self.compWidget.controlStyle_comboBox.currentIndex()]

        self.updateHierarchyAttrs()
        self.updateAttachAttrs()

    def showEvent(self, event):
        '''override showEvent, fill form with saved values
        super(AssignNewComponentWidget, self).showEvent(event)
        self.settings.beginGroup("AssignNewGroupWidget")
        #restore prethe wewous values'''
        self.setTitle()

    def returnGroupAttrObjects(self):
        '''return limb, group dict, and attach dict to the all builder'''
        #ONLY RETURN IF EDITED
        return self.limb, self._componentAttrList, self._hierarchyAttrList, self._attachAttrList

    def setSlot(self):
        oldLimb = self.limb
        self.update()
        self.setBuildString(oldLimb)
        super(AssignNewComponentWidget, self).setSlot(oldLimb)

    def setBuildString(self, oldLimb):
        #delete old attribute if the limb name has changed
        if oldLimb != self.limb:
            if self.puppet.hasAttr('%s_build' % oldLimb):
                pm.setAttr('%s.%s_build' % (self.puppet, oldLimb), lock=False)
                pm.deleteAttr('%s.%s_build' % (self.puppet, oldLimb))

        if self.puppet and self.limb:

            if not self.puppet.hasAttr('%s_build' % self.limb):
                self.puppet.addTag('%s_build' % self.limb)

            buildObj = buildInfo.BuildInfo()
            buildObj.setBuildValues(compType=self.compType,
                                    startJoint=self._componentAttrList[0],
                                    endList=self._componentAttrList[3],
                                    name=self._componentAttrList[1],
                                    side=self._componentAttrList[2],
                                    aimJoints=self._componentAttrList[4],
                                    aimSockets=self._componentAttrList[5],
                                    style=self._componentAttrList[8],
                                    controlScale=self._componentAttrList[7],
                                    controlOffset=self._componentAttrList[6])

            #unlock string
            pm.setAttr('%s.%s_build' % (self.puppet, self.limb), lock=False)
            pm.setAttr('%s.%s_build' % (self.puppet, self.limb), buildObj.toJson(), type='string')
            pm.setAttr('%s.%s_build' % (self.puppet, self.limb), lock=True)

    @property
    def component(self):
        name = naming.TipName(base=self.name, side=self.side, descriptor='component', suffix='1')
        return pm.PyNode(name.name)

    @property
    def rootGroup(self):
        name = naming.TipName(base=self.name, side=self.side, descriptor='rootGroup', suffix='1')
        return pm.PyNode(name.name)

    @property
    def attachGroup(self):
        name = naming.TipName(base=self.name, side=self.side, descriptor='attachGroup', suffix='1')
        return pm.PyNode(name.name)
