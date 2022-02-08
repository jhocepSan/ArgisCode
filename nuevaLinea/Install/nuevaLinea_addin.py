import arcpy,os,math
import pythonaddins

class NumeroLinea(object):
    def __init__(self):
        self.mxd = arcpy.mapping.MapDocument("CURRENT")
        lyrs = [i.name for i in arcpy.mapping.ListLayers(self.mxd) if i.isFeatureLayer == True]
        self.items = lyrs
        self.dropdownWidth = 'WWWWWWWWWWWWWWWWWWWW'
        self.width = 'WWWWWWW'
        self.target=""
    def onSelChange(self, selection):
        print(selection)
        self.target=selection
    def onEditChange(self, text):
        print(text)
        self.target=text
        self.selection=text
    def onFocus(self, focused):
        #Adjust as new layers are added to dataframe
        lyrs = [i.name for i in arcpy.mapping.ListLayers(self.mxd) if i.isFeatureLayer == True]
        self.items = lyrs
        if len(lyrs) > 0:
            self.target = lyrs[0]
            try:
                if not self.target == self.selection:
                    self.target = self.selection
            except AttributeError:
                pass
    def onEnter(self):
        print("se eligio eso")
    def refresh(self):
        pass

class CapaDesechos(object):
    def __init__(self):
        self.mxd = arcpy.mapping.MapDocument("CURRENT")
        lyrs = [i.name for i in arcpy.mapping.ListLayers(self.mxd) if i.isFeatureLayer == True]
        self.items = lyrs
        self.dropdownWidth = 'WWWWWWWWWWWWWWWWWWWW'
        self.width = 'WWWWWWW'
        self.target=""
    def onSelChange(self, selection):
        print(selection)
        self.target=selection
    def onEditChange(self, text):
        print(text)
        self.target=text
        self.selection=text
    def onFocus(self, focused):
        lyrs = [i.name for i in arcpy.mapping.ListLayers(self.mxd) if i.isFeatureLayer == True]
        self.items = lyrs
        if len(lyrs) > 0:
            self.target = lyrs[0]
            try:
                if not self.target == self.selection:
                    self.target = self.selection
            except AttributeError:
                pass
    def onEnter(self):
        print("se eligio eso")
    def refresh(self):
        pass

class CapaNoCultivable(object):
    def __init__(self):
        self.mxd = arcpy.mapping.MapDocument("CURRENT")
        lyrs = [i.name for i in arcpy.mapping.ListLayers(self.mxd) if i.isFeatureLayer == True]
        self.items = lyrs
        self.dropdownWidth = 'WWWWWWWWWWWWWWWWWWWW'
        self.width = 'WWWWWWW'
        self.target=""
    def onSelChange(self, selection):
        print(selection)
        self.target=selection
    def onEditChange(self, text):
        self.target=text
        self.selection=text
    def onFocus(self, focused):
        lyrs = [i.name for i in arcpy.mapping.ListLayers(self.mxd) if i.isFeatureLayer == True]
        self.items = lyrs
        if len(lyrs) > 0:
            self.target = lyrs[0]
            try:
                if not self.target == self.selection:
                    self.target = self.selection
            except AttributeError:
                pass
    def onEnter(self):
        print("se eligio eso")
    def refresh(self):
        pass

class CapaCamino(object):
    def __init__(self):
        self.mxd = arcpy.mapping.MapDocument("CURRENT")
        lyrs = [i.name for i in arcpy.mapping.ListLayers(self.mxd) if i.isFeatureLayer == True]
        self.items = lyrs
        self.dropdownWidth = 'WWWWWWWWWWWWWWWWWWWW'
        self.width = 'WWWWWWW'
        self.target=""
    def onSelChange(self, selection):
        self.target=selection
    def onEditChange(self, text):
        self.target=text
        self.selection=text
    def onFocus(self, focused):
        lyrs = [i.name for i in arcpy.mapping.ListLayers(self.mxd) if i.isFeatureLayer == True]
        self.items = lyrs
        if len(lyrs) > 0:
            self.target = lyrs[0]
            try:
                if not self.target == self.selection:
                    self.target = self.selection
            except AttributeError:
                pass
    def onEnter(self):
        print("se eligio eso")
    def refresh(self):
        pass
class CapaAuxiliar(object):
    def __init__(self):
        self.mxd = arcpy.mapping.MapDocument("CURRENT")
        lyrs = [i.name for i in arcpy.mapping.ListLayers(self.mxd) if i.isFeatureLayer == True]
        self.items = lyrs
        self.dropdownWidth = 'WWWWWWWWWWWWWWWWWWWW'
        self.width = 'WWWWWWW'
        self.target=""
    def onSelChange(self, selection):
        print(selection)
        self.target=selection
    def onEditChange(self, text):
        self.target=text
        self.selection=text
    def onFocus(self, focused):
        lyrs = [i.name for i in arcpy.mapping.ListLayers(self.mxd) if i.isFeatureLayer == True]
        self.items = lyrs
        if len(lyrs) > 0:
            self.target = lyrs[0]
            try:
                if not self.target == self.selection:
                    self.target = self.selection
            except AttributeError:
                pass
    def onEnter(self):
        print("se eligio eso")
    def refresh(self):
        pass
class ButtonEjecutar(object):
    """Implementation for nuevaLinea_addin.activar (Button)"""
    def __init__(self):
        self.enabled = False
        self.checked = False
    def onClick(self):
        if(busqueda.nrLinea!=0):
            busqueda.runProg=True
            busqueda.distancia=0
            busqueda.runBusqueda()
        else:
            pythonaddins.MessageBox ("Primero Elija el numero de linea", "Error")

class ButtonActivar(object):
    """Implementation for nuevaLinea_addin.activar (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        if capaArbol.target!="" and capaDesechos.target!="" and capaNoCultivable.target!="" and capaCamino.target!="" and capaAuxiliar.target!="":
            selecPunto.enabled=True
            descartivar.enabled=True
            ejecutar.enabled=True
        else:
            pythonaddins.MessageBox("Seleccione las capas de trabajo","Error")
            selecPunto.enabled=False
        

class ButtonDesactivar(object):
    """Implementation for nuevaLinea_addin.descartivar (Button)"""
    def __init__(self):
        self.enabled = False
        self.checked = False
    def onClick(self):
        selecPunto.enabled=False
        
class ButtonClearAuxiliar(object):
    def __init__(self):
        self.enabled=True
        self.checked=False
        self.filename=""
    def onClick(self): 
        arcpy.DeleteFeatures_management(capaAuxiliar.target);
        '''directorio = pythonaddins.OpenDialog(r"c://", filter=MyValidator())
        print(directorio)
        arcpy.env.workspace=os.path.dirname(directorio)
        self.filename=os.path.basename(directorio)'''

class SelectPunto(object):
    """Implementation for nuevaLinea_addin.selecPunto (Tool)"""
    def __init__(self):
        self.enabled = False
        self.shape = "Rectangle" #  "Line", "Circle" or "Rectangle"
        self.cont=0
    def onMouseDown(self, x, y, button, shift):
        pass
    def onMouseDownMap(self, x, y, button, shift):
        filenm=capaAuxiliar.target
        if(filenm!=""):
            with arcpy.da.InsertCursor(filenm,"SHAPE@XY") as cursor:
                cursor.insertRow([(x,y)])
                self.cont+=1
            del cursor
            arcpy.RefreshActiveView()
            if(self.cont==2):
                #busqueda.runProg=True
                self.enabled=False
                self.cont=0
        else:
            pythonaddins.MessageBox ("Intente nuevamente \n Seleccione el shapefile", "Error")
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