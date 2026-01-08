'''
Created on 01-01-2022

@author: Marcin Kutrzynski
'''
from scripting import *
import random

# get a CityEngine instance
ce = CE()

#viewport = ce.get3DViews()[0]

#filename= '/' + 'test_snapshot_1.png'  
#viewport.snapshot(ce.toFSPath('images') + filename, 300, 300)

dome = ce.getObjectsFrom(ce.scene, ce.isViewDome)[0]
ce.setObserverPoint(dome, [30, 40, 50])    

#if __name__ == '__main__':
"""
objects = ce.getObjectsFrom(ce.scene,  ce.withName('main_road'))
for o in objects:
    print('object')
    #ce.setAttributeSource(block, '/ce/block/shapeCreation', "USER")
    #ce.setAttribute(block,'/ce/block/shapeCreation',True)
    #ce.setAttributeSource(o, '/ce/street/streetWidth', "USER")
    ce.setAttribute(o,'/ce/street/streetWidth',random.randint(8, 24))
    ce.setAttributeSource(o,'/ce/street/sidewalkWidthRight',"USER")
    ce.setAttribute(o,'/ce/street/sidewalkWidthRight',random.randint(2, 15))
    ce.setAttributeSource(o,'/ce/street/sidewalkWidthLeft',"USER")
    ce.setAttribute(o,'/ce/street/sidewalkWidthLeft',random.randint(2, 15))
    
ce.waitForUIIdle() 

objects = ce.getObjectsFrom(ce.scene,  ce.withName('street'))
for street in objects:
    print(ce.getStartRule(street))
    if ce.getStartRule(street) == 'Default$Sidewalk':
        print(ce.getAttributeList(street))
        ce.setAttributeSource(street, '/ce/rule/Plantings', "USER")
        ce.setAttribute(street,'/ce/rule/Plantings',True if random.randint(0,10)>5 else False)
        ce.setAttributeSource(street, '/ce/rule/Sidewalk_Texture', "USER")
        ce.setAttribute(street,'/ce/rule/Sidewalk_Texture','Cement Block Grey Running Bond')
        ce.setAttributeSource(street, '/ce/rule/Sidewalk_Texture_Scale', "USER")
        ce.setAttribute(street,'/ce/rule/Sidewalk_Texture_Scale',5)
        ce.setAttributeSource(street, '/ce/rule/People_percentage', "USER")
        ce.setAttribute(street,'/ce/rule/People_percentage',random.randint(0, 15))
        ce.setAttributeSource(street, '/ce/rule/Tree.Name', "USER")
        ce.setAttribute(street,'/ce/rule/Tree.Name','Yew')
    
    #ce.setAttributeSource(block,'/ce/block/subdivisionRecursive',"USER")
    #ce.setAttribute(block,'/ce/block/type','Offset Subdivision')    
"""