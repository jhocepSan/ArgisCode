import arcpy,os,math
import pythonaddins

class NumeroLinea(object):
    def __init__(self):
        self.target = 0
        self.editable = True
        self.enabled = True
        self.items=[1,2,3,4,5,6]
        self.dropdownWidth = '   WWWWW'
        self.width = 'WWWWW'
    def onSelChange(self, selection):
        print(selection)
        self.target=selection
        busqueda.nrLinea=selection
    def onEditChange(self, text):
        print(text)
        self.target=int(text)
    def onFocus(self, focused):
        #Adjust as new layers are added to dataframe
        print(self.items)
    def onEnter(self):
        print("se eligio eso")
        if self.noExiste(self.target):
            self.items.append(self.target)
            busqueda.nrLinea=self.target
        else:
            pythonaddins.MessageBox ("Intente nuevamente \n Existe el numero", "Error")
    def refresh(self):
        pass
    def noExiste(self,item):
        res=True
        for i in self.items:
            if i==item:
                res=False
                break
        return res

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
        self.enabled = False
        self.checked = False
    def onClick(self):
        selecPunto.enabled=True
        

class ButtonDesactivar(object):
    """Implementation for nuevaLinea_addin.descartivar (Button)"""
    def __init__(self):
        self.enabled = False
        self.checked = False
    def onClick(self):
        selecPunto.enabled=False
        
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
        selecPunto.enabled=True
        activar.enabled=True
        descartivar.enabled=True
        ejecutar.enabled=True

class MyValidator(object):
    def __str__(self):
        return "Text files(*.*)"
    def __call__(self, filen):
        if os.path.isfile(filen) and filen.lower().endswith(".shp"):
            return True
        return False

class SelectPunto(object):
    """Implementation for nuevaLinea_addin.selecPunto (Tool)"""
    def __init__(self):
        self.enabled = False
        self.shape = "Rectangle" #  "Line", "Circle" or "Rectangle"
        self.cont=0
    def onMouseDown(self, x, y, button, shift):
        pass
    def onMouseDownMap(self, x, y, button, shift):
        filenm=dataInput.filename
        filenm=filenm[:filenm.find(".")]
        busqueda.filename=filenm
        print(busqueda.filename)
        if(filenm!=""):
            with arcpy.da.InsertCursor("auxiliar","SHAPE@XY") as cursor:
                cursor.insertRow([(x,y)])
                self.cont+=1
            del cursor
            arcpy.RefreshActiveView()
            if(self.cont==2):
                busqueda.runProg=True
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