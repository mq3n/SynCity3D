'''
Created on 24-04-2021

@author: Marcin Kutrzynski
'''
#from scripting import *

# get a CityEngine instance
#import cityengine as ce
#ce = CE()
from cityengine import *
ce = CE()

#if __name__ == '__main__':
    #pass

import sys
from pathlib import Path

BASE_DIR = Path(
    r"C:\Users\Marcin Kutrzynski\Documents\CityEngine\Default Workspace\moving_camera"
)

SCRIPTS_DIR = BASE_DIR / "scripts"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

# import sys
# sys.path.append('scripts')
# sys.path.append(r"scripts/generate_city")
from generate_city.create_network import *
from generate_city.create_photo_EQR import *


#TODO: dodac jako procedure
#wlaczenie nieba

panoramaSettings = ce.getPanorama()
panoramaSettings.setVisible(True)
ce.setPanorama(panoramaSettings)

    
# create_random_city()

#create_photo_set()

#zmiana rol
#niebieskie

#wylaczenie nieba
panoramaSettings = ce.getPanorama()
panoramaSettings.setVisible(False)
ce.setPanorama(panoramaSettings)

objects = ce.getObjectsFrom(ce.scene,  ce.withName('street'))
for o in objects:
    ce.setAttributeSource(o,'/ce/rule/Display_Textures',"USER")
    ce.setAttribute(o,'/ce/rule/Display_Textures',False)

objects = ce.getObjectsFrom(ce.scene,  ce.withName('lot'))
for buildings in objects:
    ce.setRuleFile(buildings, 'rules/dilatation_street.cga')
    
objects = ce.getObjectsFrom(ce.scene,  ce.withName('LotCorner'))
for o in objects:
    ce.setRuleFile(o, 'none')


#generowanie obrazow

# print "czekanie na rendering 2"
# ce.generateModels(ce.getObjectsFrom(ce.scene))
# views = ce.getObjectsFrom(ce.get3DViews())
# views[0].frame()
# ce.waitForUIIdle()    
# print "koniec 2"
# """
# #create_photo_set(main_road = 'main_road', prefix = 'z')
# """
# objects = ce.getObjectsFrom(ce.scene,  ce.withName('street'))
# for o in objects:
#     ce.setRuleFile(o, 'none')    
        
# print "czekanie na rendering 3"     
# ce.generateModels(ce.getObjectsFrom(ce.scene))
# views = ce.getObjectsFrom(ce.get3DViews())
# views[0].frame()
# ce.waitForUIIdle()    
# print "koniec 3"
# """
# #create_photo_set(main_road = 'main_road', prefix = 'y')
# """
   

