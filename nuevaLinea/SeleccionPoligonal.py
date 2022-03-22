import arcpy
import math
class SeleccionPoligonal(object):
    def __init__(self):
        self.fileArbol="454_arboles"
        self.fileAuxi="auxiliar"
        self.fileBuffer="c454_arboles_Buffer1_Multipa"
        self.nroLinea=0
        self.distancia=0
        self.alfa=0
        self.beta=0
        self.ultimoAngulo=0
        self.puntoPivot=[]
    def getSeleccion(self):
        listaPuntos=[]
        dat=arcpy.SelectLayerByLocation_management(self.fileBuffer,"WITHIN_A_DISTANCE",self.fileAuxi,"100 Centimeters","NEW_SELECTION")
        nro=arcpy.GetCount_management(self.fileBuffer)
        print("Numero de poligonos {}".format(nro))
        if nro!=0:
            print("Entro")
            puntos=arcpy.SelectLayerByLocation_management(self.fileArbol,"WITHIN_A_DISTANCE",self.fileBuffer,"100 Centimeters","NEW_SELECTION")
            nroP=int(arcpy.GetCount_management(self.fileArbol)[0])
            print("Numero de Arboles {}".format(nroP))
            for i in range(nroP):
                fid=puntos.getOutput(0).getSelectionSet()[i]
                with arcpy.da.SearchCursor(self.fileArbol,["SHAPE@XY","nro_linea","valido"],""""FID"={}""".format(fid)) as cursor:
                    for row in cursor:
                        if row[1]!=-1 and row[2]!=1:
                            listaPuntos.append((fid,row[0],row[1],row[2]))  

        datoFiltrado=sorted(listaPuntos,key=lambda px:px[1][0])
        print(datoFiltrado)
        return datoFiltrado 
    def setNroLine(self,fid,nro_linea,visitado):
        with arcpy.da.UpdateCursor(self.fileArbol, ["nro_linea","valido"],""""FID"={}""".format(fid)) as curs:
            for row in curs:
                row[0] = nro_linea
                row[1] = visitado
                curs.updateRow(row)
    def getAngulo(self,punto1,punto2):
        alfa=math.atan2(punto2[1]-punto1[1],punto2[0]-punto1[0])
        return alfa
    def getDistancia(self,punto1,punto2):
        res=math.sqrt(math.pow(punto2[1]-punto1[1],2)+math.pow(punto2[0]-punto1[0],2))
        return res
    def getPendiente(self,punto1,punto2):
        m= (punto2[1]-punto1[1])/(punto2[0]-punto1[0])
        return m
    def maxNroLine(self):
        nroLinea=0
        try:
            with arcpy.da.SearchCursor(self.fileArbol,['nro_linea'],'"nro_linea">0',None,None,sql_clause=("TOP 1","ORDER BY MAX(nro_linea) DESC")) as cursor:
                nroLinea=max(cursor)[0]+1
        except Exception as err:
            print("Problema:: {}".format(err))
            nroLinea=1
        print(nroLinea)
        self.nroLinea=nroLinea
    def puntoOrigen(self):
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
        print("Los Puntos Son: {}".format(listaPuntos))
        if nroPuntos==2:
            self.distancia=self.getDistancia(listaPuntos[0][1],listaPuntos[1][1])
            self.alfa=self.getAngulo(listaPuntos[0][1],listaPuntos[1][1])
            if self.alfa<0:
                self.beta=self.getAngulo(listaPuntos[0][1],listaPuntos[1][1])
                self.alfa=self.getAngulo(listaPuntos[1][1],listaPuntos[0][1])
            else:
                self.beta=self.getAngulo(listaPuntos[1][1],listaPuntos[0][1])
            print("Datos de origen son d :{} a :{} b:{}".format(self.distancia,self.alfa,self.beta))
    def getPuntoSugerido(self,p,angulo,distancia):
        xa=p[0]+distancia*math.cos(angulo)
        ya=p[1]+distancia*math.sin(angulo)
        return(xa,ya)
    def agregarPunto(self,punto):
        arcpy.DeleteFeatures_management(self.fileAuxi)
        with arcpy.da.InsertCursor(self.fileAuxi,"SHAPE@XY") as cursor:
            cursor.insertRow([punto])
        arcpy.RefreshActiveView()
    def modificarPunto(self,punto):
        with arcpy.da.UpdateCursor(self.fileAuxi,"SHAPE@XY") as cursor:
            for row in cursor:
                row[0]=(punto[0],punto[1])
                cursor.updateRow(row)
        del(cursor)
        arcpy.RefreshActiveView()
    def busquedaLineal(self):
        n=0
        d=self.distancia
        #self.maxNroLine()
        while n<20:
            puntos=self.getSeleccion()
            if len(puntos)>=2:
                cont=0
                for i in puntos:
                    print(cont)
                    if cont==0: 
                        self.puntoPivot=i[1]
                        self.setNroLine(i[0],self.nroLinea,1)    
                    else:
                        a=self.getAngulo(self.puntoPivot,i[1])
                        if a>0:
                            if abs(a-self.alfa)<1.2:
                                self.puntoPivot=i[1]
                                self.setNroLine(i[0],self.nroLinea,1)
                                if len(puntos)-1==cont:
                                    newP=self.getPuntoSugerido(i[1],self.alfa,self.distancia)
                                    print("punto nuevo {}".format(newP))
                                    self.modificarPunto(newP)
                                    if abs(a-self.alfa)<0.6:
                                        self.alfa=a
                                        self.ultimoAngulo=a
                                    else:
                                        self.ultimoAngulo=self.alfa
                        else:
                            if abs(a-self.beta)<1.2:
                                self.puntoPivot=i[1]
                                self.setNroLine(i[0],self.nroLinea,1)
                                if len(puntos)-1==cont:
                                    newP=self.getPuntoSugerido(i[1],self.beta,self.distancia)
                                    print("punto nuevo {}".format(newP))
                                    self.modificarPunto(newP)
                                    if abs(a-self.beta)<0.6:
                                        self.beta=a
                                        self.ultimoAngulo=a
                                    else:
                                        self.ultimoAngulo=self.beta
                    cont=cont+1
            elif len(puntos)==1:
                self.setNroLine(puntos[0][0],self.nroLinea,1)
                self.puntoPivot=puntos[0][1]
                self.ultimoAngulo=self.getAngulo(self.puntoPivot,puntos[0][1])
                newP=self.getPuntoSugerido(self.puntoPivot,self.ultimoAngulo,self.distancia)
                self.modificarPunto(newP)
            elif len(puntos)==0:
                d=d+0.3
                newP=self.getPuntoSugerido(self.puntoPivot,self.ultimoAngulo,d)
                self.modificarPunto(newP)
                self.puntoPivot=newP
            n+=1
    
        
        