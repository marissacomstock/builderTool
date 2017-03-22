#*******************************************************************************
# Copyright (c) 2013 Tippett Studio. All rights reserved.
#
# $Id$
#*******************************************************************************

import pymel.core as pm
from maya import cmds

import os, sys, subprocess

from tip.qt.pkg import QtCore, QtGui, uic
import json

from tip.maya.studio.core import *
from tip.db import studio

#Builder Widgets
from tip.maya.puppet.tools.builderTool.builderGUI import editFKComponentWidget
from tip.maya.puppet.tools.builderTool.builderGUI import editLimbComponentWidget
from tip.maya.puppet.tools.builderTool.builderGUI import editSpineComponentWidget
from tip.maya.puppet.tools.builderTool.builderGUI import editAimComponentWidget
from tip.maya.puppet.tools.builderTool.builderGUI import editFaceComponentWidget

from tip.maya.puppet.tools.builderTool.defaultBuilderFiles import baseBuilder
from tip.maya.puppet.tools.builderTool.defaultBuilderFiles import buildPuppet
from tip.maya.puppet.tools.builderTool.builderUtils import buildInfo
from tip.maya.puppet.tools.builderTool.builderUtils import hierInfo
from tip.maya.puppet.tools.builderTool.builderUtils import attachInfo
from tip.maya.puppet.tools.builderTool.builderUtils import componentInfo
from tip.maya.puppet.puptypes import newHier
from tip.maya.puppet.components import component
from tip.maya.puppet.rigging import attach
from tip.maya.studio.nodetypes import dependNode
from tip.maya.studio.core import *

from tip.maya.studio.workcontext import MayaWorkContext

FILEPATH = os.path.dirname(__file__) + "/builderUI"

DEFBUILDERPATH = os.path.dirname(__file__) + "/defaultBuilderFiles"

editorPath = os.path.join(FILEPATH, "builderWidget.ui")
windowPath = os.path.join(FILEPATH, "builderWidgetMainWindow.ui")
assignPath = os.path.join(FILEPATH, "editFKComponentWidget.ui")

defaultBuilderJson = os.path.dirname(__file__) + "/builderUtils/defaultComponents.json"

QtCore.QCoreApplication.setOrganizationName("Tippett")
QtCore.QCoreApplication.setOrganizationDomain("tippett.com")

form_class, base_class = uic.loadUiType('%s/builderWidget.ui' % FILEPATH)


class BonesWidget(form_class, base_class):

    closeSignal = QtCore.Signal()
    refreshSignal = QtCore.Signal()

class BuilderWidget(form_class, base_class):

    def __init__(self):
        super(BuilderWidget, self).__init__()
        self.setupUi(self)
        self.setObjectName('CreateBuilder')
        self.setWindowTitle('Create Builder')

        self.setMinimumSize(870, 340)
        self.setMaximumSize(870, 340)

        #init builderGUI
        #self.initBuilderGui()
        self.Dict = dict()
        self.deleteDict = dict()

        self.wc = MayaWorkContext()
        self.wcShow = self.wc.show

        self.initWindow()

        #connect gui
        #FILE MENU
        #self.menuWidget.actionNewBuilder.triggered.connect(self.createNewBuilder)
        #self.menuWidget.actionOpenBuilder.triggered.connect(self.openBuilder)

        #show toggle
        #self.show_comboBox.currentIndexChanged.connect(self.getCreatures)

        #NEW LIMB
        self.addNewComponent_pushButton.clicked.connect(self.assign)
        self.addDefaultComponent_pushButton.clicked.connect(self.assign)

        #BUILDER COMPONENTS
        self.editComponent_pushButton.clicked.connect(self.assign)
        self.removeComponent_pushButton.clicked.connect(self.assign)
        self.buildComponent_pushButton.clicked.connect(self.assign)
        self.buildAllComponents_pushButton.clicked.connect(self.assign)
        self.deleteComponent_pushButton.clicked.connect(self.assign)

        #ANIM FILES
        self.addFile_pushButton.clicked.connect(self.assign)
        self.removeFile_pushButton.clicked.connect(self.assign)
        self.newFile_listWidget.currentItemChanged.connect(self.assign)

        #DELETE LISTS
        self.addDeleteItems_pushButton.clicked.connect(self.assign)
        self.removeDeleteItems_pushButton.clicked.connect(self.assign)

        self.loadPuppetFromScene_pushButton.clicked.connect(self.assign)

        #TIP MENu
        #self.menuWidget.actionHelpOnUsage.triggered.connect(self._tipMenuHandler)
        #self.menuWidget.actionTipWeb.triggered.connect(self._tipMenuHandler)
        #self.menuWidget.actionTipWiki.triggered.connect(self._tipMenuHandler)
        #self.menuWidget.actionTipSite.triggered.connect(self._tipMenuHandler)

    def initWindow(self):
        self.show_label.setText(self.wcShow)

        '''
        ## populate show and creatures
        self.getCreatures()

        ## init the anim file and delete dict that comes with it
        self.newFile_listWidget.addItem('anim')
        self.deleteDict['anim'] = list()
        '''

        #load the default
        ##STORE AS A JSON FILE
        defaultFile = open(defaultBuilderJson, 'r')
        djdata = json.load(defaultFile)
        defaultFile.close()

        for default in sorted(djdata.keys()):
            self.default_Component_listWidget.addItem(default)

    def getCreatures(self):
        #get show
        self.show = self.show_comboBox.currentText()

        #clear creatures
        self.creature_comboBox.clear()

        #get show creatures
        creatures = studio.getShots(self.show, 'creature')

        #add show creatures to the creature combo box
        for creature in creatures:
            wholeCreature = str(creature.name)
            creatName = wholeCreature.split('creature1')[-1]
            self.creature_comboBox.addItem(creatName)

    def createNewBuilder(self):
        #this should clear the component node of any json strings

        self.Dict = dict()
        self.component_listWidget.clear()
        self.newFile_listWidget.clear()
        self.deleteItems_listWidget.clear()

    def openBuilder(self):
        print 'save some basic Json files with default behavior'

    def assign(self):
        sender = self.sender()

        #NEW LIMB
        if sender == self.addDefaultComponent_pushButton:
            self.addDefaultComponent()
        elif sender == self.addNewComponent_pushButton:
            self.addNewComponent()
        #BUILDER COMPONENTS
        elif sender == self.editComponent_pushButton:
            self.editComponent()
        elif sender == self.removeComponent_pushButton:
            self.removeComponent()
        elif sender == self.buildComponent_pushButton:
            items = [item.text() for item in self.component_listWidget.selectedItems()]

            self.buildComponent(items)
        elif sender == self.buildAllComponents_pushButton:
            items = list()
            for index in reversed(range(0, self.component_listWidget.count())):
                items.append(self.component_listWidget.item(index).text())
            self.buildComponent(items)
        elif sender == self.deleteComponent_pushButton:
            self.deleteComponent()
        #ANIM FILES
        elif sender == self.addFile_pushButton:
            if self.newFile_lineEdit.text():
                self.newFile_listWidget.addItem(self.newFile_lineEdit.text())
                self.deleteDict[self.newFile_lineEdit.text()] = list()
                self.newFile_lineEdit.clear()
        elif sender == self.removeFile_pushButton:
            for item in self.newFile_listWidget.selectedItems():
                self.newFile_listWidget.takeItem(self.newFile_listWidget.row(item))
                del self.deleteDict[item]
        #DELETE LISTS
        elif sender == self.addDeleteItems_pushButton:
            ##adjust builder dictionaries
            sel = pm.ls(selection=True)
            if sel:
                for item in sel:
                    self.deleteItems_listWidget.addItem(checks.pyNodeToString(item))
                    self.deleteDict[self.newFile_listWidget.currentItem().text()].append(item)
        elif sender == self.removeDeleteItems_pushButton:
            ##adjust builder dictionaries
            for item in self.deleteItems_listWidget.selectedItems():
                self.deleteItems_listWidget.takeItem(self.deleteItems_listWidget.row(item))
                self.deleteDict[self.newFile_listWidget.currentItem().text()].remove(item.text())
        #APPLY BUILDER
        elif sender == self.exportBuilder_pushButton:
            self.exportBuilder()
        elif sender == self.exportSelectedFiles_pushButton:
            self.exportSelectedFiles()
        elif sender == self.exportAllFiles_pushButton:
            self.exportAllFiles()
        elif sender == self.newFile_listWidget:
            #clear delete list
            self.deleteItems_listWidget.clear()
            curItem = self.newFile_listWidget.currentItem()
            if not curItem.text() in self.deleteDict.keys():
                self.deleteDict[curItem.text()] = list()
            for item in self.deleteDict[curItem.text()]:
                self.deleteItems_listWidget.addItem(checks.pyNodeToString(item))
        elif sender == self.loadPuppetFromScene_pushButton:
            nodes = pm.ls(assemblies=True)
            for node in nodes:
                if node.hasAttr('componentGroup'):
                    self.puppet = node
                    self.puppet_label.setText(str(self.puppet))

            #add buildComponent attr
            if not self.puppet.hasAttr('buildComponents'):
                self.puppet.addTag('buildComponents')

            #create component info object
            compInfo = self.puppet.buildComponents.get()
            self.compObj = componentInfo.ComponentInfo()

            #get components from json file
            self.compObj.fromJson(compInfo)
            components = self.compObj.getComponents()

            #load components
            self.loadComponents(components=components)

    def loadComponents(self, components):
        self.component_listWidget.clear()
        self.Dict = dict()

        for component in components:
            buildDict, hierDict, attachDict = buildPuppet.loadComponent(self.puppet, component)

            #add component
            self.addComponent(limb='%s%s' % (buildDict['name'], naming.noneToBlank(naming.getSideName(buildDict['side']))),
                              compType=buildDict['compType'],
                              buildDict=buildDict,
                              hierDict=hierDict,
                              attachDict=attachDict,
                              openBuilder=True)

            #add to builder component menu
            self.component_listWidget.addItem('%s%s' % (buildDict['name'], naming.noneToBlank(naming.getSideName(buildDict['side']))))

    def deleteComponent(self):
        curItems = self.component_listWidget.selectedItems()

        compGrp = checks.pyNodeToString('componentGroup_1')

        if curItems:
            for item in curItems:
                compType = self.Dict[item.text()].compType
                comp = self.Dict[item.text()].component
                attachGroup = self.Dict[item.text()].attachGroup
                limb, compAttrList, hierAttrList, attachAttrList = self.Dict[item.text()][0].returnGroupAttrObjects()

                compName = naming.TipName(base=compAttrList[1], side=compAttrList[2], descriptor='Component', suffix='1')

                attach.findAndDetach(name=compName.base,
                              side=compName.side,
                              attachGroup=attachGroup,
                              followNode='followControl_1',
                              comp=comp,
                              compGrp=compGrp)

    def addDefaultComponent(self):
        curItem = self.default_Component_listWidget.selectedItems()

        ##STORE AS A JSON FILE
        defaultFile = open(defaultBuilderJson, 'r')
        djdata = json.load(defaultFile)
        defaultFile.close()

        if curItem:
            curItem = str(curItem[0].text())

            self.addComponent(limb=curItem,
                              compType=djdata[curItem]["compType"],
                              buildDict=djdata[curItem]["component"],
                              hierDict=djdata[curItem]["hier"],
                              attachDict=djdata[curItem]["attach"])

    def addNewComponent(self):
        curItem = self.newComponent_listWidget.selectedItems()
        if curItem:
            compType = str(curItem[0].text())

        self.addComponent(compType=compType)

    def addComponent(self,
                     limb=None,
                     compType='FKComponent',
                     buildDict=None,
                     hierDict=None,
                     attachDict=None,
                     openBuilder=False):
        '''add new component to builder widget'''

        if compType == 'SpineComponent':
            self.curWidget = editSpineComponentWidget.AssignNewComponentWidget(limb=limb,
                                            compType=compType,
                                            componentDict=self.Dict,
                                            componentWidget=self.component_listWidget,
                                            puppet=self.puppet,
                                            compObj=self.compObj)
        elif compType == 'NeckIkComponent' or compType == 'FKComponent' or compType == 'SplineComponent':
            self.curWidget = editFKComponentWidget.AssignNewComponentWidget(limb=limb,
                                            compType=compType,
                                            componentDict=self.Dict,
                                            componentWidget=self.component_listWidget,
                                            puppet=self.puppet,
                                            compObj=self.compObj)
        elif compType == 'LimbComponent':
            self.curWidget = editLimbComponentWidget.AssignNewComponentWidget(limb=limb,
                                            compType=compType,
                                            componentDict=self.Dict,
                                            componentWidget=self.component_listWidget,
                                            puppet=self.puppet,
                                            compObj=self.compObj)
        elif compType == 'AimComponent':
            self.curWidget = editAimComponentWidget.AssignNewComponentWidget(limb=limb,
                                            compType=compType,
                                            componentDict=self.Dict,
                                            componentWidget=self.component_listWidget,
                                            puppet=self.puppet,
                                            compObj=self.compObj)
        elif compType == 'FaceComponent':
            self.curWidget = editFaceComponentWidget.AssignNewComponentWidget(limb=limb,
                                            compType=compType,
                                            componentDict=self.Dict,
                                            componentWidget=self.component_listWidget,
                                            puppet=self.puppet,
                                            compObj=self.compObj)

        self.curWidget.initWindow(buildDict=buildDict, hierDict=hierDict, attachDict=attachDict)
        self.Dict[limb] = self.curWidget

        if not openBuilder:
            self.curWidget.show()
            self.curWidget.raise_()

    def editComponent(self):
        curItem = self.component_listWidget.selectedItems()[0]

        if curItem:
            curItem = str(curItem.text())
            self.Dict[curItem].show()
            self.Dict[curItem].show()
            self.Dict[curItem].raise_()

    def removeComponent(self):
        curItem = self.component_listWidget.selectedItems()[0]

        #unlock build component attr
        self.puppet.buildComponents.setLocked(False)
        if curItem:
            self.component_listWidget.takeItem(self.component_listWidget.row(curItem))
            self.compObj.removeComponent(curItem.text())
            del self.Dict[curItem]

        #update build component string
        self.puppet.buildComponents.set(self.compObj.toJson(), type='string')
        self.puppet.buildComponents.setLocked(True)

    def buildComponent(self, components):
        '''Builds Puppet components either all at once or individually, attach
            ran at the end which will love for anything with an attach node that's not checked'''

        ##Initialize the puppet hierarchy so that items can be commited
        buildPuppet.BuildPuppet(puppet=self.puppet, compList=components)

        '''
        base.Base(name=self.creature.split('1')[-1],
                       dbShow=self.show,
                       dbShot=self.creature,
                       items=items,
                       widgetDict=self.Dict)
        '''
    def _tipMenuHandler(self):
        ''' These are links attached in many puppet tools. Needs to be updated
         Placeholder for now'''

        sender = self.sender()

        if sender is self.menuWidget.actionHelpOnUsage:
            subprocess.call(('firefox', 'http://wiki.tippett.com/index.php/Correctives_Utility'))
        elif sender is self.menuWidget.actionTipWeb:
            subprocess.call(('firefox', 'http://web.tippett.com/'))
        elif sender is self.menuWidget.actionTipWiki:
            subprocess.call(('firefox', 'http://wiki.tippett.com/index.php/Main_Page'))
        elif sender is self.menuWidget.actionTipSite:
            subprocess.call(('firefox', 'http://www.tippett.com'))

class BuilderMainWindow(QtGui.QMainWindow):

    closeSignal = QtCore.Signal()

    def __init__(self):
        super(BuilderMainWindow, self).__init__()
        #parent.__init__(self)
        self.settings = QtCore.QSettings()
        self.setObjectName('dockControl_correctives')
        self = BuilderWidget()
        self.setWindowTitle(self.windowTitle())
        self.setMinimumSize(870, 330)
        self.setMaximumSize(870, 330)
        self.setCentralWidget(self.menuWidget)
        # connect close signal & dock close
        self.closeSignal.connect(self.close)
        self.menuWidget.actionClose.triggered.connect(self.close)
        self.show()


    def closeEvent(self, event):
        self.settings.beginGroup("correctiveDockWidget")
        self.settings.setValue("size", self.size())
        self.settings.setValue("pos", self.pos())
        self.settings.endGroup()
        self.closeSignal.emit()
        #cmds.scriptJob(kill=self.sceneImportedScriptJobID)
        #cmds.scriptJob(kill=self.sceneOpenedScriptJobID)
        self.deleteLater()


    def showEvent(self, event):
        if event.spontaneous():
            return

        screenWidth, screenHeight = self.screenCenter()
        defaultSize = QtCore.QSize(284, 643)
        defaultPos = QtCore.QPoint(screenWidth, screenHeight)
        self.settings.beginGroup("correctiveDockWidget")
        #QVariant no longer used in pyside
        self.resize(self.settings.value("size", defaultSize))
        #self.resize(defaultSize)
        self.move(defaultPos)
        self.settings.endGroup()


    def screenCenter(self):
        '''Center tool in the screen'''
        resolution = QtGui.QDesktopWidget().screenGeometry()
        width = (resolution.width() / 2) - (self.frameSize().width() / 2)
        height = (resolution.height() / 2) - (self.frameSize().height() / 2)
        return width, height


def builderGui():
    ''' Create and show a corrective utility window.  Works in maya 2009+. '''

    if cmds.about(apiVersion=True) >= 201100:

        dialog = mayaQtUi.getMayaWindow('builder')

        if not dialog:
            # global __dialogs
            dialog = BuilderMainWindow()
            dialog.show()
            # __dialogs.append(dialog)
        else:
            dialog.showNormal()
            dialog.raise_()

        return dialog

    else:
        import tip.maya.qtBridge
        tip.maya.qtBridge.init()
        #dialog = CommitCorrectiveDialog()
        #tip.maya.qtBridge.show(dialog)



