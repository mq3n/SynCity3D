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

from scripts.generate_city.network import *
from scripts.generate_city.snapshot import *
from scripts.generate_city.environment import *
from scripts.generate_city.objects import *

showPanorama()
    
create_random_city()

#create_photo_set()

#zmiana rol
#niebieskie

#wylaczenie nieba
hidePanorama()


setAttributeForStreets('/ce/rule/Display_Textures', False)
removeRulesFromCornerLots()
setRuleFileForBuildings('rules/dilatation_street.cga')



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
   

