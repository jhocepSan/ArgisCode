import arcpy
import pythonaddins
import math,os
class genLineaMause():
    def __init__(self):
        self.fileArboles="1065_san_jorge_arboles_merge"
        self.fileAuxi="auxiliar"
        self.fileCamino="1065_san_jorge_caminos"
        self.fileNoCultivable="1065_san_jorge_area_nocultivable"
        self.fileDesechos="1065_san_jorge_desechos_depurados"
        self.fileEjecucion=""
        self.nrLinea=0
    def maxNroLinea(self):
        nroLinea=0
        try:
            with arcpy.da.SearchCursor(self.fileArboles,['nro_linea'],'"nro_linea">0',None,None,sql_clause=("TOP 1","ORDER BY MAX(nro_linea) DESC")) as cursor:
                nroLinea=max(cursor)[0]+1
        except Exception as err:
            print("Problema:: {}".format(err))
            nroLinea=1
        print(nroLinea)
        self.nrLinea=nroLinea
    def completarCampos(self):
        nro_linea=arcpy.ListFields(self.fileArboles,"nro_linea")
        valido=arcpy.ListFields(self.fileArboles,"valido")
        if not nro_linea:
            arcpy.AddField_management(self.fileArboles,"nro_linea","LONG")
        if not valido:
            arcpy.AddField_management(self.fileArboles,"valido","LONG")
        if not valido or not nro_linea:
            pythonaddins.MessageBox ("Creado el campo necesario", "Correcto")
        else:
            pythonaddins.MessageBox ("Ya tiene los campos necesarios", "Informacion")
    def setNroLinea(self,fid,nro_linea,visitado):
        with arcpy.da.UpdateCursor(self.fileArboles, ["nro_linea","valido"],""""FID"={}""".format(fid)) as curs:
            for row in curs:
                row[0] = nro_linea
                row[1] = visitado
                curs.updateRow(row)
    def colocarPunto(self,puntoNew):
        with arcpy.da.InsertCursor(self.fileAuxi,"SHAPE@XY") as cursor:
            cursor.insertRow([puntoNew])
        del cursor
        arcpy.RefreshActiveView()
    def getDistancia(self,punto1,punto2):
        res=math.sqrt(math.pow(punto2[1]-punto1[1],2)+math.pow(punto2[0]-punto1[0],2))
        return res
    def limpiarAux(self):
        arcpy.DeleteFeatures_management(self.fileAuxi)
    def getSeleccion(self):
        listaPuntos=list()
        dato=arcpy.SelectLayerByLocation_management(self.fileArboles,"WITHIN_A_DISTANCE",self.fileAuxi,"100 Centimeters","NEW_SELECTION")
        nroPuntos=int(arcpy.GetCount_management(self.fileArboles)[0])
        for i in range(nroPuntos):
            fid=dato.getOutput(0).getSelectionSet()[i]
            with arcpy.da.SearchCursor(self.fileArboles,["SHAPE@XY","nro_linea","valido"],'"FID"={} AND "nro_linea"={}'.format(fid,0)) as cursor:
                for row in cursor:
                    listaPuntos.append((fid,row[0],row[1],row[2]))
        print("Los Puntos Validos Son: {}".format(listaPuntos))
        return listaPuntos,nroPuntos
prueba=genLineaMause()

class ToolLineMause(object):
    """Implementation for genLineaMause_addin.tool (Tool)"""
    def __init__(self):
        self.activar=False
        self.enabled = True
        self.shape = "NONE" # Can set to "Line", "Circle" or "Rectangle" for interactive shape drawing and to activate the onLine/Polygon/Circle event sinks.
        self.cont=0
        self.distancia=0
        self.endPunto=()
    def onMouseDown(self, x, y, button, shift):
        if button==1:
            if self.cont<2:
                prueba.maxNroLinea()
                prueba.colocarPunto([x,y])
                self.cont+=1
            elif self.cont==2:
                print("activado la herramienta")
                self.activar=True
                p,np=prueba.getSeleccion()
                self.distancia=prueba.getDistancia(p[0][1],p[1][1])
                self.endPunto=p[1][1]
        else:
            self.activar=False
    def onMouseDownMap(self, x, y, button, shift):
        pass
    def onMouseUp(self, x, y, button, shift):
        pass
    def onMouseUpMap(self, x, y, button, shift):
        pass
    def onMouseMove(self, x, y, button, shift):
        pass
    def onMouseMoveMap(self, x, y, button, shift):
        if self.activar:
            distancia=prueba.getDistancia(self.endPunto,(x,y))
            if self.distancia>=distancia:
                prueba.colocarPunto([x,y])
                puntos,np=prueba.getSeleccion()
                if np>0:
                    for i in puntos:
                        prueba.setNroLinea(i[0],prueba.nrLinea,1)
        else:
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