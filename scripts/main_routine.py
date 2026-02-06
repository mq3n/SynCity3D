'''
Created on 24-04-2021

@author: Marcin Kutrzynski
'''
#from scripting import *

# get a CityEngine instance
#import cityengine as ceF
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

from generate_city.network import *
from generate_city.snapshot import *
from generate_city.environment import *
from generate_city.objects import *

#pamiętaj o ustawieniu w CE visibility setting wyłączenia Shapes i Graph Network (klawisze F10 i F11) - inaczej zdjęcia będą renderowane z widocznymi liniami podziału działek i sieci ulicznej
#clear scene
ce.delete(ce.getObjectsFrom(ce.scene))

showPanorama()
hideGrid()

create_random_city()
ce.setSelection(None)
create_photo_set(cameraStep = 10, cameraHeight=5, prefix="x")

#zmiana rol
#niebieskie

#wylaczenie nieba
hidePanorama()

removeRulesFromCornerLots()
setRuleFileForBuildings('rules/dilatation_street.cga')
setStreetVisibility(False)

ce.waitForUIIdle()
create_photo_set(cameraStep = 10, cameraHeight=5, prefix="y")


# set full view options
#showGrid()
#showPanorama()

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
   

