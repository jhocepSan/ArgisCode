import arcpy,os
import pythonaddins

class ButtonDesable(object):
    """Implementation for metodo2_addin.desactivar (Button)"""
    def __init__(self):
        self.enabled = False
        self.checked = False
        
    def onClick(self):
        moveMause.enabled=False

class ButtonActive(object):
    def __init__(self):
        self.enabled=False
        self.checked=False
    def onClick(self):
        moveMause.enabled=True

class ButtonDirName(object):
    def __init__(self):
        self.enabled=True
        self.checked=False
        self.filename=""
    def onClick(self): 
        directorio = pythonaddins.OpenDialog(r"c://", filter=MyValidator())
        print(directorio)
        arcpy.env.workspace=os.path.dirname(directorio)
        self.filename=os.path.basename(directorio)
        moveMause.enabled=True
        activar.enabled=True
        desactivar.enabled=True
        

class MyValidator(object):
    def __str__(self):
        return "Text files(*.*)"
    def __call__(self, filen):
        if os.path.isfile(filen) and filen.lower().endswith(".shp"):
            return True
        return False

class EventoMoveMause(object):
    """Implementation for metodo2_addin.moveMause (Tool)"""
    def __init__(self):
        self.enabled = False
        self.shape = "NONE" # Can set to "Line", "Circle" or "Rectangle" for interactive shape drawing and to activate the onLine/Polygon/Circle event sinks.
    def onMouseDown(self, x, y, button, shift):
        pass
    def onMouseDownMap(self, x, y, button, shift):
        print("x : "+str(round(x,3)))
        print("y : "+str(round(y,3)))
        px=round(x,3)
        py=round(y,3)
        filenm=dataInput.filename
        filenm=filenm[:filenm.find(".")]
        if button==1:
            try:
                consulta=""""POINT_X">=%s AND "POINT_X"<=%s AND "POINT_Y">=%s AND "POINT_Y"<=%s"""%(px-0.2,px+0.2,py-0.2,py+0.2)
                consultaa='"POINT_X">=%s AND "POINT_X"<=%s AND "POINT_Y">=%s AND "POINT_Y"<=%s'%(px-0.2,px+0.2,py-0.2,py+0.2)
                arcpy.SelectLayerByAttribute_management(filenm,"NEW_SELECTION",consultaa)
                arcpy.DeleteFeatures_management(filenm)
            except OSError as err:
                print(err)
                pythonaddins.MessageBox ("Intente nuevamente genero los campos necesarios\npara realizar la operacion", "No Tienes los campos")
                arcpy.AddXY_management(filenm)
        else:
            cursor=arcpy.da.InsertCursor(filenm,"*")
            datos=cursor.fields
            if ("POINT_X" in datos) and ("POINT_Y" in datos):
                cursor=arcpy.da.InsertCursor(filenm,["POINT_X","POINT_Y","SHAPE@XY"])
                cursor.insertRow([px,py,(px, py)])
                print("correcto")
                arcpy.RefreshActiveView()
            else:
                pythonaddins.MessageBox ("Intente nuevamente genero los campos necesarios\npara realizar la operacion", "No Tienes los campos")
                arcpy.AddXY_management(filenm)

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
        self.enabled = False
        pass
    def onCircle(self, circle_geometry):
        pass
    def onLine(self, line_geometry):
        pass
    def onRectangle(self, rectangle_geometry):
        pass
