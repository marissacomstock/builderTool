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

# __dialogs = list()

FILEPATH = os.path.dirname(__file__).replace('builderGUI', 'builderUI')
ASSIGNPATH = os.path.join(FILEPATH, "editSpineComponentWidget.ui")

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
                 compType='spine',
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
        #COMPONENT SENDERS
        self.compWidget.startJoint_pushButton.clicked.connect(self.assignObject)
        self.compWidget.endListAdd_pushButton.clicked.connect(self.assignObject)
        self.compWidget.endListRemove_pushButton.clicked.connect(self.assignObject)
        self.compWidget.controlAdd_pushButton.clicked.connect(self.assignObject)
        self.compWidget.controlRemove_pushButton.clicked.connect(self.assignObject)

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
                    self.compWidget.left_radioButton.setChecked(True)
                elif buildDict['side'] == 'right':
                    self.compWidget.right_radioButton.setChecked(True)
                else:
                    self.compWidget.center_radioButton.setChecked(True)
                self.side = buildDict['side']
            if 'endList' in buildDict and buildDict['endList']:
                for i, item in enumerate(buildDict['endList']):
                    self.compWidget.endList_listWidget.insertItem(i, item)
            if 'controlOffset' in buildDict:
                self.compWidget.controlOffset_doubleSpinBox.setValue(buildDict['controlOffset'])
            if 'controlScale' in buildDict:
                self.compWidget.controlScale_doubleSpinBox.setValue(buildDict['controlScale'])

            if 'controlShapes' in buildDict and buildDict['controlShapes']:
                numRows = self.compWidget.controlIndex_tableWidget.rowCount()
                for x in range(0, numRows):
                    self.compWidget.controlIndex_tableWidget.removeRow(x)

                for i, item in enumerate(buildDict['controlShapes']):
                    self.compWidget.controlIndex_tableWidget.insertRow(i)
                    self.compWidget.controlIndex_tableWidget.setItem(i, 0,
                                                          QtGui.QTableWidgetItem(str(item)))
                    if 'controlIndex' in buildDict:
                        self.compWidget.controlIndex_tableWidget.setItem(i, 1,
                                                          QtGui.QTableWidgetItem(str(buildDict['controlIndex'][i])))

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
                    self.compWidget.left_radioButton.setChecked(True)
                    self.side == 'left'
                elif name.isSideRight():
                    self.compWidget.right_radioButton.setChecked(True)
                    self.side = 'right'
                else:
                    self.compWidget.center_radioButton.setChecked(True)
                    self.side = None
                #Get limb Name
                self.limb = self.compWidget.name_lineEdit.text() + naming.getSideName(self.side)
                self.attachWidget.attrPrefix_lineEdit.setText(self.limb)
        #endList
        elif sender is self.compWidget.endListAdd_pushButton:
            sel = pm.ls(selection=True)

            if sel:
                for item in pm.ls(selection=True):
                    self.compWidget.endList_listWidget.addItem(str(item))
            else:
                self.compWidget.endList_listWidget.addItem()
        elif sender is self.compWidget.endListRemove_pushButton:
            for item in self.compWidget.endList_listWidget.selectedItems():
                self.compWidget.endList_listWidget.takeItem(self.compWidget.endList_listWidget.row(item))
        #aim List
        elif sender is self.compWidget.controlAdd_pushButton:
            sel = pm.ls(selection=True)
            numRows = self.compWidget.controlIndex_tableWidget.rowCount()
            for i, s in enumerate(sel):
                self.compWidget.controlIndex_tableWidget.insertRow(numRows + i)
                self.compWidget.controlIndex_tableWidget.setItem(numRows + i, 0, QtGui.QTableWidgetItem(str(s)))
                self.compWidget.controlIndex_tableWidget.setItem(numRows + i, 1, QtGui.QTableWidgetItem(str(numRows + i)))
        elif sender is self.compWidget.controlRemove_pushButton:
            for item in self.compWidget.controlIndex_tableWidget.selectedItems():
                self.attachWidget.controlIndex_tableWidget.removeRow(item.row())

        #also excute overridden assign object
        super(AssignNewComponentWidget, self).assignObject(sender)

        #update
        self.update()

    def slotReset(self):
        ''' not sure why it didnt let me override this method'''

        self.compWidget.startJoint_lineEdit.clear()
        self.compWidget.center_radioButton.setChecked(True)
        self.compWidget.name_lineEdit.clear()
        self.compWidget.endList_listWidget.clear()
        self.compWidget.controlOffset_doubleSpinBox.setValue(1)
        self.compWidget.controlScale_doubleSpinBox.setValue(1)
        numRows = self.compWidget.controlIndex_tableWidget.rowCount()
        for row in range(0, numRows):
            self.compWidget.controlIndex_tableWidget.setItem(row, 0, None)
            self.compWidget.controlIndex_tableWidget.setItem(row, 1, None)

        super(AssignNewComponentWidget, self).slotReset()

    def update(self):
        '''update dict with latest edits'''
        #COMPONENT DICT

        #get endlist
        endList = list()
        for index in xrange(0, self.compWidget.endList_listWidget.count()):
            endList.append(self.compWidget.endList_listWidget.item(index).text())

        #get control shapes and indeces
        controlShapes = list()
        controlIndexes = list()
        numRows = self.compWidget.controlIndex_tableWidget.rowCount()
        for x in range(0, numRows):
            if self.compWidget.controlIndex_tableWidget.item(x, 0):
                controlIndexes.append(int(self.compWidget.controlIndex_tableWidget.item(x, 1).text()))
                controlShapes.append(self.compWidget.controlIndex_tableWidget.item(x, 0).text())

        #get side
        if self.compWidget.center_radioButton.isChecked():
            self.side = None
        elif self.compWidget.left_radioButton.isChecked():
            self.side = 'left'
        else:
            self.side = 'right'

        #set component attrs
        self._componentAttrList = [str(self.compWidget.startJoint_lineEdit.text()),
                           str(self.compWidget.name_lineEdit.text()),
                           self.side,
                           endList,
                           self.compWidget.controlOffset_doubleSpinBox.value(),
                           self.compWidget.controlScale_doubleSpinBox.value(),
                           controlIndexes,
                           controlShapes]

        #Get limb Name
        self.limb = self.compWidget.name_lineEdit.text() + naming.getSideName(self.side)

        #set hier and attach attrs
        self.updateHierarchyAttrs()
        self.updateAttachAttrs()


    def showEvent(self, event):
        '''override showEvent, fill form with saved values
        super(AssignNewComponentWidget, self).showEvent(event)
        self.settings.beginGroup("AssignNewGroupWidget")
        #restore previous values'''
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
                                    controlScale=self._componentAttrList[5],
                                    controlOffset=self._componentAttrList[4],
                                    controlIndex=self._componentAttrList[6],
                                    controlShapes=self._componentAttrList[7])

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
