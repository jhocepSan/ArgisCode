import arcpy,os
import pythonaddins

class ExtensionClass9(object):
    """Implementation for positionCursor_addin.extension10 (Extension)"""
    def __init__(self):
        # For performance considerations, please remove all unused methods in this class.
        self.enabled = True
    def onStartEditing(self):
        print("Hola Edicion")
        pass


class ToolClass2(object):
    """Implementation for positionCursor_addin.tool (Tool)"""
    def __init__(self):
        self.enabled = True
        self.shape = "NONE" # Can set to "Line", "Circle" or "Rectangle" for interactive shape drawing and to activate the onLine/Polygon/Circle event sinks.
        self.workpace=os.path.dirname(r'D:/ArcGisTrabajo/1065_agregado_arboles/1065_san_jorge_arboles_merge.shp')
        self.edit=arcpy.da.Editor(self.workpace)
    def onMouseDown(self, x, y, button, shift):
        pass
    def onMouseDownMap(self, x, y, button, shift):
        self.edit.startEditing(True,True)
        self.edit.startOperation()
        print("px : "+str(round(x,3)))
        print("py : "+str(round(y,3)))
        px=round(x,3)
        py=round(y,3)
        consulta=""""POINT_X">=%s AND "POINT_X"<=%s AND "POINT_Y">=%s AND "POINT_Y"<=%s"""%(px-1.3,px+1.3,py-1.3,py+1.3)
        with arcpy.da.SearchCursor("1065_san_jorge_arboles_merge",["POINT_X","POINT_Y"],consulta) as cursor:
            for row in cursor:
                print("{} datos x".format(row[0]))
                print("{} datos y".format(row[1]))
                #cursor.deleteRow()
            #del cursor
        #arcpy.RefreshActiveView()

    def onMouseUp(self, x, y, button, shift):
        pass
    def onMouseUpMap(self, x, y, button, shift):
        pass
    def onMouseMove(self, x, y, button, shift):
        pass
    def onMouseMoveMap(self, x, y, button, shift):
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