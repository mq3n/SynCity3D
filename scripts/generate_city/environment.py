from cityengine import *

ce = CE()


def showPanorama():
    panoramaSettings = ce.getPanorama()
    panoramaSettings.setVisible(True)
    ce.setPanorama(panoramaSettings)


def hidePanorama():
    panoramaSettings = ce.getPanorama()
    panoramaSettings.setVisible(False)
    ce.setPanorama(panoramaSettings)


def setGrid(visible: bool):
    view = ce.get3DViews()[0]
    rs = view.getRenderSettings()
    rs.setGridVisible(visible)
    rs.setAxesVisible(visible)
    rs.setCompassVisible(visible)
    view.setRenderSettings(rs)


def showGrid():
    setGrid(True)


def hideGrid():
    setGrid(False)


def set_shadows(value):
    view = ce.getObjectsFrom(ce.get3DViews(), ce.isViewport)[0]
    renderSettings = view.getRenderSettings()
    renderSettings.setShadows(value)
    view.setRenderSettings(renderSettings)


def set_street_visibility(visible: bool, scene_name):
    l = ce.getObjectsFrom(ce.scene, ce.isLayer, ce.withName(f"{scene_name}"))[0]
    ce.setLayerPreferences(l, "Show Network", visible)


# These settings produce (almost) clean, white environment/space around and ON a building, 
# we could let it pass as it was - with heterogenous grays everywhere and then cut them off with channels manipulation
def set_scene_env_for_mask(mask_on):
    lightSettings = ce.getLighting()
    if mask_on: 
        lightSettings.setSolarElevationAngle(90)
        #lightSettings.setAmbientIntensity(1.0) # creates overexposured photos
        lightSettings.setAmbientIntensity(0.825) # !!!!
        lightSettings.setSolarIntensity(1.0)
        lightSettings.setAmbientOcclusionAttenuation(0.0)
    else:
        lightSettings.setAmbientIntensity(0.5)  # return to default settings
        lightSettings.setSolarIntensity(0.5)
        lightSettings.setAmbientOcclusionAttenuation(0.4)
    ce.setLighting(lightSettings)


def set_environment_config(config):
    '''Change Scenery: panorama and sun positioning'''
    env_map =  "ce.lib/maps/panoramas/" + config["sky"] + ".env.jpg"
    refl_map = "ce.lib/maps/panoramas/" + config["sky"] + ".refl.jpg"

    panoramaSettings = ce.getPanorama()
    panoramaSettings.setEnvironmentMap(env_map)
    panoramaSettings.setReflectionMap(refl_map)
    ce.setPanorama(panoramaSettings)
    
    lightSettings = ce.getLighting()
    lightSettings.setSolarAzimuthAngle(config["azimuth"])
    lightSettings.setSolarElevationAngle(config["elevation"])
    ce.setLighting(lightSettings)
    # OTHER? these are options customizing scene: sun and shadows, rendering etc
    