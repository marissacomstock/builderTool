#*******************************************************************************
# $Id: buildInfo.py 52150 2017-03-09 20:36:19Z marissa $
#*******************************************************************************

import json

'''this module will be used in maya and katana, so no maya-specific stuff in here
in particular reading and writing maya attributes
'''

#############################################

'''strategies for storing build information for each component

mesh is the shape node in maya, a mesh location in katana

grandparent: traditional face set locations
parent: maya transform of mesh'''

GUIDE_ROOT_LOCATIONS = ['grandparent', 'parent']


#############################################

class BuildInfo(object):
    '''per-mesh info for furator

    currently:
        a list of guide types
        how to find related guides in a hierarchy
    '''

    def __init__(self):
        # strings for each curve type
        self.curveTypes = set()

        # one of the above guideRootLocations
        # TODO: relative path
        self.compType = None
        self.startJoint = None
        self.name = None
        self.side = None
        self.endList = None
        self.style = 'eye'
        self.controlStyle = 1
        self.aimJoints = None
        self.aimSockets = None
        self.inverseTop = None
        self.inversePivot = None
        self.inversePrefix = None
        self.parentSwitchLabel = None
        self.parentSwitchTarget = None
        self.controlScale = 1
        self.pvOffset = 1
        self.controlOffset = 1.2
        self.controlIndex = [0, 2, 4]
        self.controlShapes = ['hipShape', 'splitShape', 'chestShape']
        self.nodeList = ['faceSplit_bnd', 'faceBotRt_bnd', 'faceBotLf_bnd', 'faceMidLf_bnd', 'faceMidRt_bnd',
                         'faceTopLf_bnd', 'faceTopRt_bnd']


    def toJson(self):
        ''''''

        jsonStruct = dict()
        jsonStruct['compType'] = self.compType
        jsonStruct['startJoint'] = self.startJoint
        jsonStruct['name'] = self.name
        jsonStruct['side'] = self.side
        jsonStruct['endList'] = self.endList
        jsonStruct['style'] = self.style
        jsonStruct['controlStyle'] = self.controlStyle
        jsonStruct['aimJoints'] = self.aimJoints
        jsonStruct['aimSockets'] = self.aimSockets
        jsonStruct['inverseTop'] = self.inverseTop
        jsonStruct['inversePivot'] = self.inversePivot
        jsonStruct['inversePrefix'] = self.inversePrefix
        jsonStruct['parentSwitchLabel'] = self.parentSwitchLabel
        jsonStruct['parentSwitchTarget'] = self.parentSwitchTarget
        jsonStruct['controlScale'] = self.controlScale
        jsonStruct['pvOffset'] = self.pvOffset
        jsonStruct['controlOffset'] = self.controlOffset
        jsonStruct['controlIndex'] = self.controlIndex
        jsonStruct['controlShapes'] = self.controlShapes
        jsonStruct['nodeList'] = self.nodeList

        return json.dumps(jsonStruct)

    def fromJson(self, s):
        '''read from JSON string

        some validation'''
        jsonStruct = json.loads(s)
        if 'compType' in jsonStruct:
            self.compType = jsonStruct['compType']
            print self.compType
        if 'startJoint' in jsonStruct:
            self.startJoint = jsonStruct['startJoint']
        if 'name' in jsonStruct:
            self.name = jsonStruct['name']
        if 'side' in jsonStruct:
            self.side = jsonStruct['side']
        if 'endList' in jsonStruct:
            self.endList = jsonStruct['endList']
        if 'style' in jsonStruct:
            self.style = jsonStruct['style']
        if 'controlStyle' in jsonStruct:
            self.controlStyle = jsonStruct['controlStyle']
        if 'aimSockets' in jsonStruct:
            self.aimSockets = jsonStruct['aimSockets']
        if 'inverseTop' in jsonStruct:
            self.inverseTop = jsonStruct['inverseTop']
        if 'inversePivot' in jsonStruct:
            self.inversePivot = jsonStruct['inversePivot']
        if 'inversePrefix' in jsonStruct:
            self.inversePrefix = jsonStruct['inversePrefix']
        if 'parentSwitchLabel' in jsonStruct:
            self.parentSwitchLabel = jsonStruct['parentSwitchLabel']
        if 'parentSwitchTarget' in jsonStruct:
            self.parentSwitchTarget = jsonStruct['parentSwitchTarget']
        if 'controlScale' in jsonStruct:
            self.controlScale = jsonStruct['controlScale']
        if 'pvOffset' in jsonStruct:
            self.pvOffset = jsonStruct['pvOffset']
        if 'controlOffset' in jsonStruct:
            self.controlOffset = jsonStruct['controlOffset']
        if 'controlIndex' in jsonStruct:
            self.controlIndex = jsonStruct['controlIndex']
        if 'controlShapes' in jsonStruct:
            self.controlShapes = jsonStruct['controlShapes']
        if 'nodeList' in jsonStruct:
            self.nodeList = jsonStruct['nodeList']

    def setBuildValues(self, compType = None,
                        startJoint = None,
                        name = None,
                        side = None,
                        endList = None,
                        style = None,
                        controlStyle = None,
                        aimJoints = None,
                        aimSockets = None,
                        inverseTop = None,
                        inversePivot = None,
                        inversePrefix = None,
                        parentSwitchLabel = None,
                        parentSwitchTarget = None,
                        controlScale = None,
                        pvOffset = None,
                        controlOffset = None,
                        controlIndex = None,
                        controlShapes = None,
                        nodeList = None):

        if compType:
            self.compType = compType
        if startJoint:
            self.startJoint = startJoint
        if name:
            self.name = name
        if side:
            self.side = side
        if endList:
            self.endList = endList
        if style:
            self.style = style
        if controlStyle:
            self.controlStyle = controlStyle
        if aimJoints:
            self.aimJoints = aimJoints
        if aimSockets:
            self.aimSockets = aimSockets
        if inverseTop:
            self.inverseTop = inverseTop
        if inversePivot:
            self.inversePivot = inversePivot
        if inversePrefix:
            self.inversePrefix = inversePrefix
        if parentSwitchLabel:
            self.parentSwitchLabel = parentSwitchLabel
        if parentSwitchTarget:
            self.parentSwitchTarget = parentSwitchTarget
        if controlScale:
            self.controlScale = controlScale
        if pvOffset:
            self.pvOffset = pvOffset
        if controlOffset:
            self.controlOffset = controlOffset
        if controlIndex:
            self.controlIndex = controlIndex
        if controlShapes:
            self.controlShapes = controlShapes
        if nodeList:
            self.nodeList = nodeList

    def getBuildDict(self):

        buildDict = {'compType': self.compType,
                     'startJoint': self.startJoint,
                     'endList': self.endList,
                     'name': self.name,
                     'side': self.side}

        if self.compType == 'AimComponent':
            buildDict['aimJoints'] = self.aimJoints
            buildDict['aimSockets'] = self.aimSockets
            buildDict['style'] = self.style
            buildDict['controlScale'] = self.controlScale
            buildDict['controlOffset'] = self.controlOffset

        if self.compType == 'LimbComponent':
            buildDict['inverseTop'] = self.inverseTop
            buildDict['inversePivot'] = self.inversePivot
            buildDict['inversePrefix'] = self.inversePrefix
            buildDict['parentSwitchLabel'] = self.parentSwitchLabel
            buildDict['parentSwitchTarget'] = self.parentSwitchTarget
            buildDict['controlScale'] = self.controlScale
            buildDict['controlOffset'] = self.controlOffset

        if self.compType == 'SpineComponent':
            buildDict['controlScale'] = self.controlScale
            buildDict['controlOffset'] = self.controlOffset
            buildDict['controlIndex'] = self.controlIndex
            buildDict['controlShapes'] = self.controlShapes

        if self.compType == 'FaceComponent':
            del buildDict['endList']
            buildDict['nodeList'] = self.nodeList

        return buildDict
