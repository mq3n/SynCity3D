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
