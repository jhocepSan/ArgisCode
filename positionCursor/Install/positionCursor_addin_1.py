import arcpy
import pythonaddins,os
arcpy.env.workspace="D:/ArcGisTrabajo/1065_agregado_arboles"
class ToolClass2(object):
    """Implementation for positionCursor_addin.tool (Tool)"""
    def __init__(self):
        self.workpace=os.path.dirname(r'D:/ArcGisTrabajo/1065_agregado_arboles/1065_san_jorge_arboles_merge.shp')
        self.edit=arcpy.da.Editor(self.workpace)
        self.enabled = True
        self.shape = "NONE" # Can set to "Line", "Circle" or "Rectangle" for interactive shape drawing and to activate the onLine/Polygon/Circle event sinks.
    def onMouseDown(self, x, y, button, shift):
        pass
    def onMouseDownMap(self, x, y, button, shift):
        message = "Se hizo clic con el mouse:" + str (x) + "," + str (y) 
        #pythonaddins.MessageBox (message, "Mis coordenadas")
        arcpy.AddXY_management(in_features="1065_san_jorge_arboles_merge")
        print("x : "+str(round(x,3)))
        print("y : "+str(round(y,3)))
        px=round(x,3)
        py=round(y,3)
        consulta='"POINT_X">=%s AND "POINT_X"<=%s AND "POINT_Y">=%s AND "POINT_Y"<=%s'%(px-2.0,px+2.0,py-2.0,py+2.0)#arcpy.AddFieldDelimiters(self.workpace,"POINT_X")+'>=%s'%x
        print(consulta)
        xser=0
        yser=0
        with arcpy.da.SearchCursor('1065_san_jorge_arboles_merge.shp',["POINT_X","POINT_Y"],consulta) as cursor:
            cont=0
            for row in cursor:
                print(row[0])
                print(row[1])
                print("diff x: "+str(abs(row[0]-x)))
                print("diff Y: "+str(abs(row[1]-y)))
                if abs(row[0]-x)<=1.5 and abs(row[1]-y)<=1.5:
                    xser=row[0]
                    yser=row[1]
                    #cursor.deleteRow()
                    break
        if xser!=0 and yser!=0:
            consulta1='"POINT_X"={} AND "POINT_Y"={}'.format(xser,yser)
            print(consulta1)
            arcpy.SelectLayerByAttribute_management('1065_san_jorge_arboles_merge',"NEW_SELECTION",consulta1)
        #arcpy.UDeleteFeatures_management('1065_san_jorge_arboles_merge.shp')
        #self.enabled=False
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