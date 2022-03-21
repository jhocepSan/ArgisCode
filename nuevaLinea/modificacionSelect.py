import arcpy,math,os,time
import pythonaddins 

print(os.path)
class BusquedaPuntoParalelo(object):
    def __init__(self):
        self.fileArboles="31_arboles"
        self.fileAuxi="auxiliar"
        self.fileCamino="31_caminos"
        self.fileNoCultivable="31_no_cultivable"
        self.fileDesechos="31_desechos"
        self.fileEjecucion="ejecuciona"
        self.nrLinea=0
        self.runPara=False
        self.distancia=10000
        self.clearProg()
    def clearProg(self):
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
    def getSeleccion(self):
        otroP=False
        listaPuntos=list()
        dato=arcpy.SelectLayerByLocation_management(self.fileArboles,"WITHIN_A_DISTANCE",self.fileAuxi,"100 Centimeters","NEW_SELECTION")
        nroPuntos=int(arcpy.GetCount_management(self.fileArboles)[0])
        print("total Seleccionados: {}".format(arcpy.GetCount_management(self.fileArboles)[0]))
        for i in range(nroPuntos):
            fid=dato.getOutput(0).getSelectionSet()[i]
            with arcpy.da.SearchCursor(self.fileArboles,["SHAPE@XY","nro_linea","valido"],'"FID"={} and "nro_linea"={}'.format(fid,0)) as cursor:
                for row in cursor:
                    listaPuntos.append((fid,row[0],row[1],row[2]))
        nroPuntos=len(listaPuntos)
        print("Los Puntos Son: {} tamanio: {}".format(listaPuntos,nroPuntos))
        return listaPuntos,nroPuntos
    def getSelccion3(self):
        otroP=False
        listaPuntos=list()
        dato=arcpy.SelectLayerByLocation_management(self.fileArboles,"WITHIN_A_DISTANCE",self.fileAuxi,"2.5 Meters","NEW_SELECTION")
        nroPuntos=int(arcpy.GetCount_management(self.fileArboles)[0])
        for i in range(nroPuntos):
            fid=dato.getOutput(0).getSelectionSet()[i]
            print(fid)
            with arcpy.da.SearchCursor(self.fileArboles,["SHAPE@XY","nro_linea","valido"],""""FID"={} """.format(fid)) as cursor:
                for row in cursor:
                    if row[1]==0:
                        listaPuntos.append((fid,row[0],row[1],row[2]))
        print("total Seleccionados: {} # puntos: {}".format(listaPuntos,len(listaPuntos)))
        return listaPuntos,len(listaPuntos)
    def areaEnTrabajo(self):
        arcpy.SelectLayerByLocation_management(self.fileAuxi,"INTERSECT",self.fileEjecucion,"","NEW_SELECTION")
        nroPuntos=int(arcpy.GetCount_management(self.fileAuxi)[0])
        print(nroPuntos)
        if nroPuntos<=1:
            return  False
        else:
            return True
    def areaEnTrabajo2(self):
        arcpy.SelectLayerByLocation_management(self.fileAuxi,"INTERSECT",self.fileEjecucion,"","NEW_SELECTION")
        nroPuntos=int(arcpy.GetCount_management(self.fileAuxi)[0])
        print(nroPuntos)
        if nroPuntos==0:
            return  False
        else:
            return True
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
    def setNroLine(self,fid,nro_linea,visitado):
        with arcpy.da.UpdateCursor(self.fileArboles, ["nro_linea","valido"],""""FID"={}""".format(fid)) as curs:
            for row in curs:
                row[0] = nro_linea
                row[1] = visitado
                curs.updateRow(row)
    def getPuntoSugerido(self,distancia,angulo):
        xa=self.punto2[1][0]+distancia*math.cos(angulo)
        ya=self.punto2[1][1]+distancia*math.sin(angulo)
        return(xa,ya)
    def limpiarAux(self):
        arcpy.DeleteFeatures_management(self.fileAuxi)
    def maxNroLine(self):
        nroLinea=0
        try:
            with arcpy.da.SearchCursor(self.fileArboles,['nro_linea'],'"nro_linea">0',None,None,sql_clause=("TOP 1","ORDER BY MAX(nro_linea) DESC")) as cursor:
                nroLinea=max(cursor)[0]+1
        except Exception as err:
            print("Problema:: {}".format(err))
            nroLinea=1
        print(nroLinea)
        self.nrLinea=nroLinea
    def colocarPunto(self,puntoNew,puntoAntiguo):
        arcpy.DeleteFeatures_management(self.fileAuxi)
        with arcpy.da.InsertCursor(self.fileAuxi,"SHAPE@XY") as cursor:
            cursor.insertRow([puntoNew])
        with arcpy.da.InsertCursor(self.fileAuxi,"SHAPE@XY") as cursor:
            cursor.insertRow([puntoAntiguo])
        del cursor
        arcpy.RefreshActiveView()
    def validarAngulo(self):
        anguloNuevo=self.getAngulo(self.punto1[1],self.punto2[1])
        diff=abs(anguloNuevo-self.angulo)
        print("alfa nuevo: {}, alfa antiguo {}, diferencia: {}".format(anguloNuevo,self.angulo,diff))
        if (anguloNuevo<0 and self.angulo<0) or (anguloNuevo>0 and self.angulo>0):
            if diff<=0.29:
                print("..... Nos quedamos con el nuevo angulo")
                self.angulo=anguloNuevo
            elif diff>0.29 and diff<=0.44:
                print("..... Te estas desiviando reduciremos el angulo .....")
                if self.angulo>0:
                    self.angulo=self.angulo-0.1
                else:
                    self.angulo=self.angulo+0.1
        else:
            print("... transicion de angulos ...")
            if anguloNuevo<0:
                self.angulo=anguloNuevo-0.08
            else:
                self.angulo=anguloNuevo+0.08
    def anguloCorrecto(self):
        anguloNuevo=self.getAngulo(self.punto1[1],self.punto2[1])
        if abs(anguloNuevo-self.angulo)>0.6 and ((anguloNuevo<0 and self.angulo<0) or (anguloNuevo>0 and self.angulo>0)):
            return False
        else:
            return True
    def busquedaLineal2(self):
        distancia=self.distancia
        while self.runProg and self.estaEnArea:
            puntos,np=self.getSelccion3()
            if np==1:
                print("hacemos colocar punto")
                self.agregarPunto(puntos[0][1])
                print("fin")
                self.setNroLine(puntos[0][0],self.nrLinea,1)
                self.setNroLine(self.punto2[0],self.nrLinea,2)
                distancia=self.getDistancia(self.punto2[1],puntos[0][1])
                #valido la distancia
                if distancia<self.distancia and distancia>2:
                    self.distancia=distancia
                #valido el angulo
                self.punto1=self.punto2
                self.punto2=puntos[0]
                self.validarAngulo()
                self.valido=True
            elif np==2:
                t1=self.getAngulo(self.punto2[1],puntos[0][1])
                t2=self.getAngulo(self.punto2[1],puntos[1][1])
                print("angulo1:{}---angulo2: {}"(t1,t2))
                d1=self.getDistancia(self.punto2[1],puntos[0][1])
                d2=self.getDistancia(self.punto2[1],puntos[1][1])
                self.setNroLine(self.punto2[0],self.nrLinea,1)
                if abs(d1-self.distancia)<abs(d2-self.distancia):
                    self.agregarPunto(puntos[0][1])
                    self.setNroLine(puntos[0][0],self.nrLinea,2)
                    self.setNroLine(puntos[1][0],-1,1)
                    self.punto1=self.punto2
                    self.punto2=puntos[0]
                else:
                    self.agregarPunto(puntos[1][1])
                    self.setNroLine(puntos[0][0],-1,1)
                    self.setNroLine(puntos[1][0],self.nrLinea,2)
                self.valido=True
            elif np==0:
                print("entro cero")
                if distancia<10:
                    print(self.angulo)
                    newP=self.getPuntoSugerido(distancia,self.angulo)
                    self.agregarPunto(newP)
                    distancia=distancia+2
                    self.valido=True
                else:
                    self.setNroLine(puntos[0][0],self.nrLinea,1)
                    self.valido=False
                    self.limpiarAux()
                    self.clearProg()
                    self.runProg=False
            if self.valido:
                print("validamos")
                self.valido=False
                if self.estaEnArea()==True or not self.areaEnTrabajo():
                    self.setNroLine(self.punto2[0],self.nrLinea,1)
                    self.runProg=False
                    self.limpiarAux()
                    self.clearProg()
    def busquedaLineal(self):
        #formato puntos [fid,punto,nro_linea,valido]
        n=0
        distancia=0
        angulo=0
        while self.runProg and self.areaEnTrabajo():
            puntos,np=self.getSeleccion()
            if np==2:
                distancia=self.getDistancia(puntos[0][1],puntos[1][1])
                if distancia<self.distancia and distancia>2:
                    self.distancia=distancia
                else:
                    distancia=self.distancia
                if puntos[0][3]==2:
                    print(puntos[0][1])
                    angulo=self.getAngulo(puntos[0][1],puntos[1][1])
                    self.punto1=puntos[0]
                    self.punto2=puntos[1]
                else:
                    angulo=self.getAngulo(puntos[1][1],puntos[0][1])
                    self.punto1=puntos[1]
                    self.punto2=puntos[0]
                print("angulo: {} , distancia: {}".format(angulo,distancia))
                print("......modificamos valido, nr_linea........")
                if self.anguloCorrecto():
                    self.validarAngulo()
                    self.setNroLine(self.punto1[0],self.nrLinea,1)
                    self.setNroLine(self.punto2[0],0,2)
                    self.valido=True
                    n+=1
                else:
                    print("---no valido ---")
                    self.validarAngulo()
                    self.setNroLine(self.punto2[0],-1,1)
                    self.setNroLine(self.punto1[0],0,2)
                    self.punto2=self.punto1
                    self.valido=True
            elif np==1:
                if distancia<10:
                    distancia+=1.2
                    self.valido=True
                else:
                    self.setNroLine(puntos[0][0],self.nrLinea,1)
                    self.valido=False
                    self.limpiarAux()
                    self.clearProg()
                    self.runProg=False
            elif np==0:
                self.runProg=False
                self.setNroLine(puntos[0][0],self.nrLinea,1)
                self.limpiarAux()
                self.clearProg()
            elif np==3:
                pivot=[]
                listaP=[]
                for p in puntos:
                    if p[3]==2:
                        pivot=p
                    else:
                        listaP.append(p)
                d1=self.getDistancia(pivot[1],listaP[0][1])
                d2=self.getDistancia(pivot[1],listaP[1][1])
                if abs(d1-self.distancia)<abs(d2-self.distancia):
                    self.setNroLine(listaP[1][0],-1,1)
                    listaP.pop(1)
                else:
                    self.setNroLine(listaP[0][0],-1,1)
                    listaP.pop(0)
                self.punto1=pivot
                self.punto2=listaP[0]
                self.validarAngulo()
                print("---Seteamos los puntos que se visito")
                self.setNroLine(self.punto1[0],self.nrLinea,1)
                self.setNroLine(self.punto2[0],0,2)
                self.runProg=True
                n+=1
            elif np==4:
                self.limpiarAux()
                pythonaddins.MessageBox ("Encontre cuatro puntos seguidos", "Informacion")
                self.runProg=False
            if self.valido:
                newP=self.getPuntoSugerido(distancia,self.angulo)
                self.colocarPunto(self.punto2[1],newP)
                self.valido=False
                if self.estaEnArea()==True or not self.areaEnTrabajo():
                    self.setNroLine(self.punto2[0],self.nrLinea,1)
                    self.runProg=False
                    self.limpiarAux()
                    self.clearProg()
        self.limpiarAux()
    def busquedaParalela(self,arriba):
        while self.runPara and self.areaEnTrabajo2():
            puntosP,npP=self.getSeleccion2()
            if npP==2:
                busco=True
                distancia=self.getDistancia(puntosP[0][1],puntosP[1][1])
                if distancia<self.distancia and distancia>1.9:
                    self.distancia=distancia
                else:
                    distancia=self.distancia
                angulo=self.getAngulo(puntosP[0][1],puntosP[1][1])
                m=self.getPendiente(puntosP[0][1],puntosP[1][1])
                distaP=distancia
                while not self.estaEnArea() and busco and self.areaEnTrabajo2():
                    punto=self.getPuntoParalelo(puntosP[0][1],distaP,m,arriba)
                    self.agregarPunto(punto)
                    disP=distancia
                    p,npG=self.getSeleccion()
                    if npG==1:
                        busco2=True
                        if self.areaEnTrabajo2():
                            while busco2 and not self.estaEnArea():
                                pb=self.aumentarDpunto(p[0][1],disP,angulo)
                                self.agregarPunto(pb)
                                ppp,npp=self.getSeleccion()
                                if npp==1:
                                    busco2=False
                                    busco=False
                                    self.colocarPunto(ppp[0][1],p[0][1])
                                    self.nrLinea+=1
                                    self.runPara=False
                                elif npp==2:
                                    self.setNroLine(ppp[0][0],-1,1)
                                else:
                                    if disP<=10:
                                        disP+=0.9
                                    else:
                                        self.runPara=False
                                        self.limpiarAux()
                        else:
                            self.runPara=False
                            self.limpiarAux()
                    elif npG==2:
                        self.setNroLine(p[0][0],-1,1)
                    else:
                        distaP+=0.9
            elif npP==3:
                self.runPara=False
                self.limpiarAux()
            elif npP==0:
                self.runPara=False
                self.limpiarAux()
    def getSeleccion2(self):
        otroP=False
        listaPuntos=list()
        dato=arcpy.SelectLayerByLocation_management(self.fileArboles,"WITHIN_A_DISTANCE",self.fileAuxi,"100 Centimeters","NEW_SELECTION")
        nroPuntos=int(arcpy.GetCount_management(self.fileArboles)[0])
        print("total Seleccionados: {}".format(arcpy.GetCount_management(self.fileArboles)[0]))
        for i in range(nroPuntos):
            fid=dato.getOutput(0).getSelectionSet()[i]
            with arcpy.da.SearchCursor(self.fileArboles,["SHAPE@XY","nro_linea","valido"],""""FID"={}""".format(fid)) as cursor:
                for row in cursor:
                    if row[1]!=-1:
                        listaPuntos.append((fid,row[0],row[1],row[2]))
        print("Los Puntos Son: {}".format(listaPuntos))
        return listaPuntos,len(listaPuntos)
    def aumentarDpunto(self,punto,distancia,angulo):
        xa=punto[0]+distancia*math.cos(angulo)
        ya=punto[1]+distancia*math.sin(angulo)
        return (xa,ya)
    def agregarPunto(self,punto):
        arcpy.DeleteFeatures_management(self.fileAuxi)
        cursor=arcpy.InsertCursor(self.fileAuxi)
        feature = cursor.newRow()
        vertex = arcpy.CreateObject("Point")
        vertex.X = punto[0]
        vertex.Y = punto[1]
        feature.shape = vertex
        cursor.insertRow(feature)
        #cursor.insertRow([punto])
        del(cursor)
        #arcpy.RefreshActiveView()
    def getPuntoParalelo(self,punto,distancia,pendiente,tipo):
        #x=punto[0]+distancia*math.cos(angulo)
        if tipo==0:
            if pendiente<0:
                x=(distancia/math.sqrt((1/math.pow(pendiente,2))+1))+punto[0]
                y=((-x+punto[0])/pendiente)+punto[1]
                print("nuevo punto paralelo: {}, {} tipo 0".format(x,y))
                #y=punto[1]+distancia*math.sin(angulo)
                return (x,y)
            else:
                x=-(distancia/math.sqrt((1/math.pow(pendiente,2))+1))+punto[0]
                y=((-x+punto[0])/pendiente)+punto[1]
                print("nuevo punto paralelo: {}, {} tipo 0".format(x,y))
                #y=punto[1]+distancia*math.sin(angulo)
                return (x,y)
        else:
            if pendiente<0:
                x=-(distancia/math.sqrt((1/math.pow(pendiente,2))+1))+punto[0]
                y=((-x+punto[0])/pendiente)+punto[1]
                print("nuevo punto paralelo: {}, {} tipo 0".format(x,y))
                #y=punto[1]+distancia*math.sin(angulo)
                return (x,y)
            else:
                x=(distancia/math.sqrt((1/math.pow(pendiente,2))+1))+punto[0]
                y=((-x+punto[0])/pendiente)+punto[1]
                print("nuevo punto paralelo: {}, {} tipo 0".format(x,y))
                #y=punto[1]+distancia*math.sin(angulo)
                return (x,y)

prueba=BusquedaPuntoParalelo()
def onPruebaR():
    prueba.runProg=True
    prueba.maxNroLine()
    pp,p=prueba.getSeleccion()
    prueba.distancia=prueba.getDistancia(pp[0][1],pp[1][1])
    prueba.angulo=prueba.getAngulo(pp[0][1],pp[1][1])    
    prueba.setNroLine(pp[0][0],prueba.nrLinea,2)
    prueba.setNroLine(pp[1][0],prueba.nrLinea,1)
    prueba.agregarPunto(pp[0][1])
    prueba.busquedaLineal2()
def onClick():
    runpp=True
    prueba.maxNroLine()
    if(prueba.nrLinea!=0):
        try:
            while runpp:
                #arcpy.env.workspace=os.path.dirname("D:\ArcGisTrabajo\POR PUBLICAR")
                #edit=arcpy.da.Editor(os.path.dirname("D:\ArcGisTrabajo\POR PUBLICAR\{}.shp".format(prueba.fileArboles)))
                #edit.startEditing(False,True)
                #edit.startOperation()
                pp,np=prueba.getSeleccion()
                prueba.runProg=True
                prueba.distancia=prueba.getDistancia(pp[0][1],pp[1][1])
                prueba.setNroLine(pp[0][0],prueba.nrLinea,3)
                prueba.setNroLine(pp[1][0],prueba.nrLinea,2)
                prueba.angulo=prueba.getAngulo(pp[0][1],pp[1][1])
                prueba.punto1=pp[0]
                prueba.punto2=pp[1]
                print("p1:{}  p2:{}".format(prueba.punto1,prueba.punto2))
                prueba.agregarPunto(pp[1][1])
                #time.sleep(10)
                print("entramos busqueda")
                prueba.busquedaLineal2()
                """#busquedaIzquierda
                prueba.runProg=True
                prueba.distancia=prueba.getDistancia(pp[0][1],pp[1][1])
                prueba.colocarPunto(pp[0][1],pp[1][1])
                prueba.setNroLine(pp[0][0],prueba.nrLinea,1)
                prueba.punto1=pp[1]
                prueba.punto2=pp[0]
                prueba.busquedaLineal2()"""
                #edit.stopOperation()
                #edit.stopEditing(True)
        except Exception as ex:
            pythonaddins.MessageBox (ex, "Error") 
            runpp=False