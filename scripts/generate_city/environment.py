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
    