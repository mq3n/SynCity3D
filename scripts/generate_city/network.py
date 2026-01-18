'''
Created on 24-04-2021

@author: Marcin Kutrzynski
'''
from cityengine import *
ce = CE()

import random

def clear_city():
    pass

def _normalize_cfg_name(name):
    if name is None:
        return None
    if not isinstance(name, str):
        try:
            name = str(name)
        except Exception:
            return None
    return "".join(ch for ch in name.strip().lower() if ch.isalnum())


def _safe_get_name(obj):
    if hasattr(ce, "getName"):
        try:
            return ce.getName(obj)
        except Exception:
            pass
    if hasattr(obj, "getName"):
        try:
            return obj.getName()
        except Exception:
            pass

    # Many non-scene objects in newer CityEngine builds don't respond to getName(),
    # but still expose a '/ce/name' attribute.
    if hasattr(ce, "getAttribute"):
        for attr_path in (
            "/ce/name",
            "/ce/asset/name",
            "/ce/streetconfiguration/name",
            "/ce/streetConfiguration/name",
        ):
            try:
                value = ce.getAttribute(obj, attr_path)
                if isinstance(value, str) and value:
                    return value
            except Exception:
                pass

    # Some wrappers expose a plain 'name' field.
    for field in ("name", "Name", "label", "Label"):
        try:
            value = getattr(obj, field)
            if isinstance(value, str) and value:
                return value
        except Exception:
            pass

    return None


def _safe_get_identity(obj):
    """Return something human-readable for debugging/listing."""
    name = _safe_get_name(obj)
    if name:
        return name
    for fn in (str, repr):
        try:
            s = fn(obj)
            if isinstance(s, str) and s and s != object.__repr__(obj):
                return s
        except Exception:
            pass
    return None


def getStreetConfigurationByName(cfg_name=None):
    """Best-effort lookup of an existing Street Configuration.

    In newer CityEngine versions, `createStreetConfiguration()` may create an object that is
    NOT part of the Street Configurations gallery yet, so applying it can have no visible effect.
    This function tries to retrieve an existing configuration (as visible in the UI) by name.

    Returns:
        A StreetConfiguration-like object, or None if nothing could be found.
    """

    # 1) Newer APIs sometimes provide a direct getter/list.
    candidates = []

    if hasattr(ce, "getStreetConfigurations"):
        try:
            candidates = list(ce.getStreetConfigurations())
        except Exception:
            candidates = []

    # 2) Some versions expose StreetConfigurations as scene objects.
    if not candidates and hasattr(ce, "isStreetConfiguration"):
        try:
            candidates = list(ce.getObjectsFrom(ce.scene, ce.isStreetConfiguration))
        except Exception:
            candidates = []

    if candidates:
        if cfg_name is None:
            print("StreetConfigurations available:", len(candidates))
            return candidates[0]

        wanted_norm = _normalize_cfg_name(cfg_name)

        for cfg in candidates:
            cfg_name_raw = _safe_get_name(cfg)
            if cfg_name_raw == cfg_name:
                print("Using existing StreetConfiguration:", cfg_name)
                return cfg

            # Fuzzy match: Inspector names sometimes differ by spaces/underscores/case.
            if wanted_norm and _normalize_cfg_name(cfg_name_raw) == wanted_norm:
                print("Using existing StreetConfiguration (normalized match):", cfg_name_raw)
                return cfg

            # Fallback: some API wrappers only expose the label in str()/repr().
            ident = _safe_get_identity(cfg)
            if isinstance(ident, str) and cfg_name in ident:
                print("Using existing StreetConfiguration (string match):", ident)
                return cfg

            if wanted_norm and isinstance(ident, str) and _normalize_cfg_name(ident) == wanted_norm:
                print("Using existing StreetConfiguration (normalized string match):", ident)
                return cfg

        print(
            "StreetConfiguration not found by name:",
            cfg_name,
            "available:",
            [_safe_get_identity(c) for c in candidates],
        )
        return None

    print(
        "No StreetConfigurations could be listed via Python API in this CityEngine version. "
        "Try creating/saving a configuration in the Street Designer UI first, then rerun."
    )
    return None


def createStreetConfigurationExample():
    """Legacy/example creator. Kept for reference; may not affect segments in 2025+ unless registered."""
    cfg = ce.createStreetConfiguration()
    if hasattr(cfg, "setName"):
        cfg.setName("My_2L_1S")

    # NOTE: Exact API for lanes differs between versions.
    if hasattr(ce, "addLane"):
        ce.addLane(cfg, laneType="DRIVING", width=3.25)
        ce.addLane(cfg, laneType="DRIVING", width=3.25)
        ce.addLane(cfg, laneType="SIDEWALK", width=2.0)
    return cfg

def create_random_city():
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
    
    #konfiguracja ulic
    streetCfg = getStreetConfigurationByName("Neighborhood_Alley_1Way_1VL_10m")

    # Collect ALL graph segments in the scene (streets)
    if hasattr(ce, "isGraphSegment"):
        segments = ce.getObjectsFrom(ce.scene, ce.isGraphSegment)
    elif hasattr(ce, "isSegment"):
        segments = ce.getObjectsFrom(ce.scene, ce.isSegment)
    else:
        segments = []

    print("Total segments found:", len(segments))

    if streetCfg is None:
        print("No StreetConfiguration applied (not found).")
    else:
        for seg in segments:
            ce.applyStreetConfigurationToSegment(seg, streetCfg)

    objects = ce.getObjectsFrom(ce.scene,  ce.withName('Block'))
    for block in objects:
        ce.setAttributeSource(block, '/ce/block/shapeCreation', "USER")
        ce.setAttribute(block,'/ce/block/subdivisionRecursive',False)
        ce.setAttributeSource(block,'/ce/block/subdivisionRecursive',"USER")
        ce.setAttribute(block,'/ce/block/type','Offset Subdivision')
        ce.setAttributeSource(block,'/ce/block/cornerWidth',"USER")
        ce.setAttribute(block,'/ce/block/cornerWidth', random.randint(90, 200))
    
    objects = ce.getObjectsFrom(ce.scene,  ce.withName("'Lot*'"))
    print("Shapes available:", len(objects))
    for shape in objects:
        if ce.getStartRule(shape) == 'Default$Lot':
            ce.setName(shape, 'lot')
            ce.setRuleFile(shape, 'rules/paris.cga')  
        elif ce.getStartRule(shape) == 'Lot':
            ce.setName(shape, 'lot')
            ce.setRuleFile(shape, 'rules/paris.cga')           
        elif ce.getStartRule(shape) == 'Default$LotInner':
            ce.setName(shape, 'lot')
            ce.setRuleFile(shape, 'rules/paris.cga')
        elif ce.getStartRule(shape) == 'Default$LotCorner':
            ce.setName(shape, 'LotCorner')
            ce.setRuleFile(shape, 'rules/paris.cga')     
        else:
            ce.setName(shape, 'street')
            ce.setRuleFile(shape, 'rules/Streets_Advanced/Advanced_Street.cga')
        
    objects = ce.getObjectsFrom(ce.scene,  ce.withName('street'))
    for street in objects:
        #print( ce.getAttribute(street))
        ce.setAttributeSource(street, '/ce/rule/Vehicles_per_km', "USER")
        ce.setAttribute(street,'/ce/rule/Vehicles_per_km',random.randint(20,50))
        #ce.setAttributeSource(block,'/ce/block/subdivisionRecursive',"USER")
        #ce.setAttribute(block,'/ce/block/type','Offset Subdivision')
    
    objects = ce.getObjectsFrom(ce.scene,  ce.withName('lot'))
    for buildings in objects:
        ce.setAttributeSource(buildings,'/ce/rule/High_LoD',"USER")
        ce.setAttribute(buildings,'/ce/rule/High_LoD',True)
        
    objects = ce.getObjectsFrom(ce.scene,  ce.withName('LotCorner'))
    for green in objects:
        ce.setAttributeSource(green,'/ce/rule/High_LoD',"USER")
        ce.setAttribute(green,'/ce/rule/High_LoD',True)
        ce.setAttributeSource(green,'/ce/rule/ShowTrees',"USER")
        ce.setAttribute(green,'/ce/rule/ShowTrees',"Realistic")       
    
    #chodnik     
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
            ce.setAttribute(street,'/ce/rule/People_percentage',random.randint(0, 35))
            ce.setAttributeSource(street, '/ce/rule/Tree.Name', "USER")
            ce.setAttribute(street,'/ce/rule/Tree.Name','Yew')         

    print("czekanie na rendering")     
    ce.generateModels(ce.getObjectsFrom(ce.scene))
    views = ce.getObjectsFrom(ce.get3DViews())
    views[0].frame()
    ce.waitForUIIdle()    
    print("koniec")