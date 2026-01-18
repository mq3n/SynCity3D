from cityengine import *

ce = CE()


def setRuleFileForObjectsByName(object_name, rule_files):
    normalized_rules = [rule_files] if isinstance(rule_files, str) else list(rule_files)
    objects = ce.getObjectsFrom(ce.scene, ce.withName(object_name))
    for o in objects:
        for rule in normalized_rules:
            ce.setRuleFile(o, rule)


def setRuleFileForBuildings(rule_files):
    setRuleFileForObjectsByName('lot', rule_files)

def removeRulesFromBuildings():
    setRuleFileForObjectsByName('lot', {'none'})

def setRuleFileForCornerLots(rule_files):
    setRuleFileForObjectsByName('LotCorner', rule_files)

def removeRulesFromCornerLots():
    setRuleFileForObjectsByName('LotCorner', {'none'})

def setAttributeForObjectsByName(object_name, attribute_path, values):
    normalized_values = [values] if not isinstance(values, (list, tuple, set)) else list(values)
    objects = ce.getObjectsFrom(ce.scene, ce.withName(object_name))
    for o in objects:
        for value in normalized_values:
            ce.setAttributeSource(o, attribute_path, "USER")
            ce.setAttribute(o, attribute_path, value)

def setAttributeForBuildings(attribute_path, values):
    setAttributeForObjectsByName('lot', attribute_path, values)

def setAttributeForCornerLots(attribute_path, values):
    setAttributeForObjectsByName('LotCorner', attribute_path, values)

def setAttributeForStreets(attribute_path, values):
    setAttributeForObjectsByName('street', attribute_path, values)
