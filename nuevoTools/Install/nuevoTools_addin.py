import arcpy
import os
import pythonaddins

arcpy.env.workspace=r"D:/ArcGisTrabajo/1065_agregado_arboles"
arboles = r"D:/ArcGisTrabajo/1065_agregado_arboles/1065_san_jorge_arboles_merge.shp"
class ActionCursor(object):
    """Implementation for nuevoTools_addin.tool (Tool)"""
    def __init__(self):
        self.enabled = True
        self.shape = "NONE" # Can set to "Line", "Circle" or "Rectangle" for interactive shape drawing and to activate the onLine/Polygon/Circle event sinks.
    def onMouseDown(self, x, y, button, shift):
        pass
    def onMouseDownMap(self, x, y, button, shift):
        pass
    def onMouseUp(self, x, y, button, shift):
        pass
    def onMouseUpMap(self, x, y, button, shift):
        pass
    def onMouseMove(self, x, y, button, shift):
        print("x: "+str(x)+"   "+"y: "+str(y))
        pass
    def onMouseMoveMap(self, x, y, button, shift):
        edit=arcpy.da.Editor(os.path.dirname(arboles))
        edit.startEditing(True,True)
        edit.startOperation()
        for row in arcpy.da.SearchCursor('1065_san_jorge_arboles_merge.shp',["SHAPE@XY"]):
            px,py=row[0]
            print("{}, {}".format(px,py))
        pass
    def onDblClick(self):
        pass
    def onKeyDown(self, keycode, shift):
        pass
    def onKeyUp(self, keycode, shift):
        pass
    def deactivate(self):
        pass
    def onCircle(self, circle_geometry):
        pass
    def onLine(self, line_geometry):
        pass
    def onRectangle(self, rectangle_geometry):
        pass

class ButtonActivar(object):
    """Implementation for nuevoTools_addin.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        pass