#*******************************************************************************
# $Id: componentInfo.py 52160 2017-03-11 00:34:35Z marissa $ 
#*******************************************************************************

import json

'''this module will be used in maya and katana, so no maya-specific stuff in here
in particular reading and writing maya attributes
'''

#############################################

'''strategies for storing the different components of a puppet'''

GUIDE_ROOT_LOCATIONS = ['grandparent', 'parent']


#############################################

class ComponentInfo(object):
    '''per-mesh info for furator

    currently:
        a list of guide types
        how to find related guides in a hierarchy
    '''

    def __init__(self):
        # strings for each curve type
        self.components = set() 

        # one of the above guideRootLocations
        # TODO: relative path
        self.guideRootLocation = 'parent' 

    def toJson(self):
        ''''''

        jsonStruct = dict()
        jsonStruct['components'] = list(self.components)

        return json.dumps(jsonStruct)

    def fromJson(self, s):
        '''read from JSON string

        some validation'''
        if s:
            jsonStruct = json.loads(s)
            if 'components' in jsonStruct:
                for comp in jsonStruct['components']:
                    self.components.add(comp)

    def addComponent(self, component):
        ''''''
        if component in self.components:
            raise ValueError
        self.components.add(component)

    def removeComponent(self, component):
        ''''''
        if component in self.components:
            self.components.remove(component)

    def getComponents(self):
        ''''''
        components = set()
        for s in self.components:
            components.add(s)
        return components
