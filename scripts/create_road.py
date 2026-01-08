'''
Created on 09-10-2020

@author: marci
'''
from scripting import *
import random

# get a CityEngine instance
ce = CE()

#if __name__ == '__main__':
#    pass

graphlayer = ce.addGraphLayer('streets')
vertices = [0,0,-1000,0,0,1000]
graph = ce.createGraphSegments(graphlayer, vertices)
ce.setName(graph,'main_road')

vertices = [100,0,-1000,100,0,1000]
graph = ce.createGraphSegments(graphlayer, vertices)
ce.setName(graph,'right_road')

vertices = [-100,0,-1000,-100,0,1000]
graph = ce.createGraphSegments(graphlayer, vertices)
ce.setName(graph,'left_road')

side = 1
vertices = []
for z in range(-1100,1100,200):
    side = side * -1
    vertices.extend([side * 200, 0, z + random.randint(0, 300)])

graph = ce.createGraphSegments(graphlayer, vertices)
ce.setName(graph,'crossing1_road')

side = -1
vertices = []
for z in range(-1100,1100,200):
    side = side * -1
    vertices.extend([side * 200, 0, z + random.randint(0, 300)])

graph = ce.createGraphSegments(graphlayer, vertices)
ce.setName(graph,'crossing2_road')

cleanupSettings = CleanupGraphSettings()
cleanupSettings.setIntersectSegments(True)
cleanupSettings.setMergeNodes(False)
cleanupSettings.setMergingDist(10)
cleanupSettings.setSnapNodesToSegments(True)
cleanupSettings.setSnappingDist(10)
cleanupSettings.setResolveConflictShapes(True)
graphlayer = ce.getObjectsFrom(ce.scene, ce.isGraphLayer)
ce.cleanupGraph(graphlayer, cleanupSettings)

objects = ce.getObjectsFrom(ce.scene,  ce.withName('Block'))
for block in objects:
    ce.setAttributeSource(block, '/ce/block/shapeCreation', "USER")
    ce.setAttribute(block,'/ce/block/subdivisionRecursive',False)
    ce.setAttributeSource(block,'/ce/block/subdivisionRecursive',"USER")
    ce.setAttribute(block,'/ce/block/type','Offset Subdivision')

objects = ce.getObjectsFrom(ce.scene,  ce.withName('Shape'))
for shape in objects:
    if ce.getStartRule(shape) == 'Default$Lot':
        ce.setName(shape, 'lot')
        ce.setRuleFile(shape, '/Workspace/moving_camera/rules/paris.cga')  
    elif ce.getStartRule(shape) == 'Lot':
        ce.setName(shape, 'lot')
        ce.setRuleFile(shape, '../rules/paris.cga')           
    elif ce.getStartRule(shape) == 'Default$LotInner':
        ce.setName(shape, 'lot')
        ce.setRuleFile(shape, '../rules/paris.cga')   
    else:
        ce.setName(shape, 'street')
        ce.setRuleFile(shape, 'rules/Streets_Advanced/Advanced_Street.cga')
    
objects = ce.getObjectsFrom(ce.scene,  ce.withName('street'))
for street in objects:
    #print( ce.getAttribute(street))
    ce.setAttributeSource(street, '/ce/rule/Vehicles_per_km', "USER")
    ce.setAttribute(street,'/ce/rule/Vehicles_per_km',30)
    #ce.setAttributeSource(block,'/ce/block/subdivisionRecursive',"USER")
    #ce.setAttribute(block,'/ce/block/type','Offset Subdivision')

     
print "czekanie na rendering"     
ce.generateModels(ce.getObjectsFrom(ce.scene))
views = ce.getObjectsFrom(ce.get3DViews())
views[0].frame()
ce.waitForUIIdle()    
print "koniec"
    

#   
#    ['/ce/block/seed', '/ce/block/shapeCreation', '/ce/block/type', '/ce/name', '/ce/variant']
#    
#subdsettings = SubdivideShapesSettings()
#subdsettings.setLotAreaMax(800)
#subdsettings.setLotAreaMin(100)
#subdsettings.setLotSubdivisionMethod('OFFSET')
#subdsettings.setOffsetWidth(10)
#ce.subdivideShapes(shapes, subdsettings)
#
#ce.setAttribute(b[0],'/ce/block/type','Offset Subdivision')
#*/