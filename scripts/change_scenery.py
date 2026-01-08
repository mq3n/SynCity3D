'''
Created on 07-02-2021

@author: Marcin Kutrzynski
'''
from scripting import *

# get a CityEngine instance
ce = CE()

# ce.getObjectsFrom(ce.scene, ce. .withName("start_point"))
p = ce.getObjectsFrom(ce.scene, ce.withName("lot*"))
print p