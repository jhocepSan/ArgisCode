import arcpy,math

class BusquedaPuntoParalelo(object):
    def __init__(self):
        self.fileArboles="1065_san_jorge_arboles_merge"
        self.fileAuxi="auxiliar"
        self.fileCamino="1065_san_jorge_caminos"
        self.fileNoCultivable="1065_san_jorge_area_nocultivable"
        self.fileDesechos="1065_san_jorge_desechos_depurados"
        self.nrLinea=0
        self.clearProg()
    def clearProg(self):
        self.distancia=0
        self.punto1=[]
        self.punto2=[]
        self.angulo=0
        self.fileNo=[]
        self.area=0.5
        self.valido=False
        self.runProg=False
    def getAngulo(self,punto1,punto2):
        alfa=math.atan2(punto2[1]-punto1[1],punto2[0]-punto1[0])
        return alfa
    def getDistancia(self,punto1,punto2):
        res=math.sqrt(math.pow(punto2[1]-punto1[1],2)+math.pow(punto2[0]-punto1[0],2))
        return res
    def getPendiente(self,punto1,punto2):
        m= (punto2[1]-punto1[1])/(punto2[0]-punto1[0])
        return m
    def esValidoPunto(self,fid):
        valor=True
        with arcpy.da.SearchCursor(self.fileArboles,["SHAPE@XY","nro_linea"],""""FID"={}""".format(fid)) as cursor:
            for row in cursor:
                if row[1]==-1:
                    print("punto no valido: "+str(fid))
                    valor=False 
        return valor
    def getSeleccion(self):
        listaPuntos=list()
        dato=arcpy.SelectLayerByLocation_management(self.fileArboles,"WITHIN_A_DISTANCE",self.fileAuxi,"100 Centimeters","NEW_SELECTION")
        nroPuntos=int(arcpy.GetCount_management(self.fileArboles)[0])
        print("total Seleccionados: {}".format(arcpy.GetCount_management(self.fileArboles)[0]))
        for i in range(nroPuntos):
            fid=dato.getOutput(0).getSelectionSet()[i]
            if self.esValidoPunto(fid):
                with arcpy.da.SearchCursor(self.fileArboles,["SHAPE@XY","nro_linea"],""""FID"={}""".format(fid)) as cursor:
                    for row in cursor:
                        listaPuntos.append((fid,row[0],row[1]))
        print("Los Puntos Son: {}".format(listaPuntos))
        return listaPuntos,len(listaPuntos)
    def dentroDeArea(self,capa1,capa2):
        arcpy.SelectLayerByLocation_management(capa1,"INTERSECT",capa2,"","NEW_SELECTION")
        nroPuntos=int(arcpy.GetCount_management(capa1)[0])
        if nroPuntos==0:
            return  False
        else:
            return True
    def estaEnArea(self):
        datos=list()
        if self.fileCamino!='':
            datos.append(self.dentroDeArea(self.fileCamino,self.fileAuxi))
        if self.fileDesechos!='':
            datos.append(self.dentroDeArea(self.fileDesechos,self.fileAuxi))
        if self.fileNoCultivable!='':
            datos.append(self.dentroDeArea(self.fileNoCultivable,self.fileAuxi))
        d=False
        for i in datos:
            d=d or i
        return d
    def maxNroLine(self):
        nroLinea=0
        try:
            with arcpy.da.SearchCursor(self.fileArboles,['nro_linea'],'"nro_linea">0',None,None,sql_clause=("TOP 1","ORDER BY MAX(nro_linea) DESC")) as cursor:
                nroLinea=max(cursor)[0]+1
        except:
            nroLinea=1
        self.nrLinea=nroLinea
        