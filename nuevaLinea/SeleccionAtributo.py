import arcpy
import math

class SeleccionAtributo(object):
    def __init__(self):
        self.fileArbol="454_arboles"
        self.fileAuxi="auxiliar"
        self.fileBuffer="c454_arboles_Buffer1_Multipa"
        self.nroLinea=0
        self.distancia=0
        self.alfa=0
    def getSeleccion(self):
        otroP=False
        listaPuntos=list()
        dato=arcpy.SelectLayerByLocation_management(self.fileArbol,"WITHIN_A_DISTANCE",self.fileAuxi,"100 Centimeters","NEW_SELECTION")
        nroPuntos=int(arcpy.GetCount_management(self.fileArbol)[0])
        print("total Seleccionados: {}".format(arcpy.GetCount_management(self.fileArbol)[0]))
        for i in range(nroPuntos):
            fid=dato.getOutput(0).getSelectionSet()[i]
            with arcpy.da.SearchCursor(self.fileArbol,["SHAPE@XY","nro_linea","valido"],""""FID"={}""".format(fid)) as cursor:
                for row in cursor:
                    if row[1]!=-1 and row[2]!=1:
                        listaPuntos.append((fid,row[0],row[1],row[2]))
                    elif (row[1]!=self.nrLinea and row[1]!=0) and row[2]==1 and row[1]!=-1:
                        otroP=True
        if(nroPuntos>=2 and len(listaPuntos)==1 and otroP==True):
            print("Encontre puntos que ya son visitados")
            nroPuntos=0
        else:
            nroPuntos=len(listaPuntos)
        print("Los Puntos Son: {}".format(listaPuntos))
        return listaPuntos,nroPuntos
    def busquedaLineal(self):
        pass