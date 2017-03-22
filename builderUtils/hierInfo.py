#*******************************************************************************
# Copyright (c) 2017 Tippett Studio. All rights reserved.
# $Id: hierInfo.py 52150 2017-03-09 20:36:19Z marissa $
#*******************************************************************************

import json

'''this module will be used in maya and katana, so no maya-specific stuff in here
in particular reading and writing maya attributes
'''

#############################################

'''strategies for storing hier information for each component

mesh is the shape node in maya, a mesh location in katana

grandparent: traditional face set locations
parent: maya transform of mesh'''

GUIDE_ROOT_LOCATIONS = ['grandparent', 'parent']


#############################################

class HierInfo(object):
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
        self.rootGroup = True
        self.localGroup = True
        self.worldGroup = False
        self.localPosition = True

    def toJson(self):
        ''''''

        jsonStruct = dict()
        jsonStruct['rootGroup'] = self.rootGroup
        jsonStruct['localGroup'] = self.localGroup
        jsonStruct['worldGroup'] = self.worldGroup
        jsonStruct['localPosition'] = self.localPosition

        return json.dumps(jsonStruct)

    def fromJson(self, s):
        '''read from JSON string

        some validation'''
        jsonStruct = json.loads(s)
        if 'rootGroup' in jsonStruct:
            self.rootGroup = jsonStruct['rootGroup']
        if 'localGroup' in jsonStruct:
            self.localGroup = jsonStruct['localGroup']
        if 'worldGroup' in jsonStruct:
            self.worldGroup = jsonStruct['worldGroup']
        if 'localPosition' in jsonStruct:
            self.localPosition = jsonStruct['localPosition']

    def setHierValues(self,
                       rootGroup = None,
                       localGroup = None,
                       worldGroup = None,
                       localPosition = None):

        if rootGroup:
            self.rootGroup = rootGroup
        if localGroup:
            self.localGroup = localGroup
        if worldGroup:
            self.worldGroup = worldGroup
        if localPosition:
            self.localPosition = localPosition

    def getHierDict(self):

        hierDict = {'rootGroup': self.rootGroup,
                    'localGroup': self.localGroup,
                    'worldGroup': self.worldGroup,
                    'localPosition': self.localPosition}
        return hierDict
