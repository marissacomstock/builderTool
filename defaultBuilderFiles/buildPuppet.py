# *******************************************************************************
# Copyright (c) 2013 Tippett Studio. All rights reserved.
# $Id: buildPuppet.py 52161 2017-03-11 00:34:56Z marissa $
#*******************************************************************************

import pymel.core as pm

from tip.maya.studio.core import *
from tip.maya.puppet.tools.builderTool.builderUtils import buildInfo
from tip.maya.puppet.tools.builderTool.builderUtils import hierInfo
from tip.maya.puppet.tools.builderTool.builderUtils import attachInfo
from tip.maya.puppet.tools.builderTool.builderUtils import componentInfo

from tip.maya.puppet.puptypes import creature

from tip.maya.puppet.components import aimComponent
from tip.maya.puppet.components import faceComponent
from tip.maya.puppet.components import fkComponent
from tip.maya.puppet.components import limbComponent
from tip.maya.puppet.components import neckIkComponent
from tip.maya.puppet.components import spineComponent
from tip.maya.puppet.components import splineComponent


class BuildPuppet():
    def __init__(self,
                 puppet,
                 compList):

        puppet = checks.stringToPyNode(puppet)

        #get component node
        if puppet.hasAttr('componentGroup'):
            self.puppet = puppet
            self.creature = creature.Creature(node=puppet)
        else:
            pm.error('%s is not a puppet top node' % puppet)

        ##create component info object
        compInfo = self.puppet.buildComponents.get()
        self.compObj = componentInfo.ComponentInfo()

        #get components from json file
        self.compObj.fromJson(compInfo)
        self.components = self.compObj.getComponents()

        self.buildComponents(compList)

    def buildComponents(self, compList):

        for component in self.components:
            if component in compList:
                buildDict, hierDict, attachDict = loadComponent(self.puppet, component)

                print buildDict['compType'], 'compType'

                if buildDict['compType'] == 'AimComponent':
                    comp = aimComponent.AimComponent(startJoint=buildDict['startJoint'],
                                              aimJoints=buildDict['aimJoints'],
                                              aimSockets=buildDict['aimSockets'],
                                              endList=buildDict['endList'],
                                              name=buildDict['name'],
                                              side=buildDict['side'],
                                              style=buildDict['style'],
                                              controlScale=buildDict['controlScale'],
                                              controlOffset=buildDict['controlOffset'],
                                              rootGroup=hierDict['rootGroup'],
                                              localGroup=hierDict['localGroup'],
                                              worldGroup=hierDict['worldGroup'],
                                              localPosition=hierDict['localPosition'],
                                              config=self.creature.getConfigControl())


                elif buildDict['compType'] == 'LimbComponent':
                    comp = aimComponent.AimComponent(startJoint=buildDict['startJoint'],
                                              endList=buildDict['endList'],
                                              name=buildDict['name'],
                                              side=buildDict['side'],
                                              inverseTop=buildDict['inverseTop'],
                                              inversePivot=buildDict['inversePivot'],
                                              inversePrefix=buildDict['inversePrefix'],
                                              parentSwitchLabel=buildDict['parentSwitchLabel'],
                                              parentSwitchTarget=buildDict['parentSwitchTarget'],
                                              controlScale=buildDict['controlScale'],
                                              controlOffset=buildDict['controlOffset'],
                                              rootGroup=hierDict['rootGroup'],
                                              localGroup=hierDict['localGroup'],
                                              worldGroup=hierDict['worldGroup'],
                                              localPosition=hierDict['localPosition'],
                                              config=self.creature.getConfigControl(),
                                              allScale=self.creature.getAllScale())
                elif buildDict['compType'] == 'SpineComponent':
                    print self.creature.getConfigControl(), 'config'
                    comp = spineComponent.SpineComponent(startJoint=buildDict['startJoint'],
                                              endList=buildDict['endList'],
                                              name=buildDict['name'],
                                              side=buildDict['side'],
                                              controlScale=buildDict['controlScale'],
                                              controlOffset=buildDict['controlOffset'],
                                              controlIndex=buildDict['controlIndex'],
                                              controlShapes=buildDict['controlShapes'],
                                              rootGroup=hierDict['rootGroup'],
                                              localGroup=hierDict['localGroup'],
                                              worldGroup=hierDict['worldGroup'],
                                              localPosition=hierDict['localPosition'],
                                              config=self.creature.getConfigControl(),
                                              allScale=self.creature.getAllScale())
                elif buildDict['compType'] == 'FaceComponent':
                    comp = faceComponent.FaceComponent(startJoint=buildDict['startJoint'],
                                              nodeList=buildDict['nodeList'],
                                              name=buildDict['name'],
                                              side=buildDict['side'],
                                              rootGroup=hierDict['rootGroup'],
                                              localGroup=hierDict['localGroup'],
                                              worldGroup=hierDict['worldGroup'],
                                              localPosition=hierDict['localPosition'],
                                              config=self.creature.getConfigControl())
                elif buildDict['compType'] == 'FKComponent':
                    comp = fkComponent.FKComponent(startJoint=buildDict['startJoint'],
                                              endList=buildDict['endList'],
                                              name=buildDict['name'],
                                              side=buildDict['side'],
                                              rootGroup=hierDict['rootGroup'],
                                              localGroup=hierDict['localGroup'],
                                              worldGroup=hierDict['worldGroup'],
                                              localPosition=hierDict['localPosition'],
                                              config=self.creature.getConfigControl())
                elif buildDict['compType'] == 'SplineComponent':
                    comp = splineComponent.SplineComponent(startJoint=buildDict['startJoint'],
                                              endList=buildDict['endList'],
                                              name=buildDict['name'],
                                              side=buildDict['side'],
                                              rootGroup=hierDict['rootGroup'],
                                              localGroup=hierDict['localGroup'],
                                              worldGroup=hierDict['worldGroup'],
                                              localPosition=hierDict['localPosition'],
                                              config=self.creature.getConfigControl())
                elif buildDict['compType'] == 'NeckIkComponent':
                    comp = neckIkComponent.NeckIkComponent(startJoint=buildDict['startJoint'],
                                              endList=buildDict['endList'],
                                              name=buildDict['name'],
                                              side=buildDict['side'],
                                              rootGroup=hierDict['rootGroup'],
                                              localGroup=hierDict['localGroup'],
                                              worldGroup=hierDict['worldGroup'],
                                              localPosition=hierDict['localPosition'],
                                              config=self.creature.getConfigControl())
                '''
                comp.attach(drivers=attachDict['drivers'],
                            driven=attachDict['driven'],
                            labels=attachDict['labels'],
                            prefix=attachDict['prefix'],
                            config=attachDict['config'],
                            point=attachDict['point'],
                            orient=attachDict['orient'],
                            scale=attachDict['scale'],
                            multiAttr=attachDict['multiAttr'],
                            attachPoint=attachDict['attachPoint'],
                            attachOrient=attachDict['attachOrient'],
                            attachScale=attachDict['attachScale'],
                            switch=attachDict['switch'])
                '''

        #run attach on everything again after..
        #get attach working

def loadComponent(puppet, component):
    #create info objs
    buildStr = pm.getAttr('%s.%s_build' % (puppet, component))
    hierStr = pm.getAttr('%s.%s_hier' % (puppet, component))
    attachStr = pm.getAttr('%s.%s_attach' % (puppet, component))

    buildObj = buildInfo.BuildInfo()
    hierObj = hierInfo.HierInfo()
    attachObj = attachInfo.AttachInfo()

    #pass string for parsing
    buildObj.fromJson(buildStr)
    hierObj.fromJson(hierStr)
    attachObj.fromJson(attachStr)

    #get build attr dicts
    buildDict = buildObj.getBuildDict()
    hierDict = hierObj.getHierDict()
    attachDict = attachObj.getAttachDict()

    return buildDict, hierDict, attachDict