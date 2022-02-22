import arcpy,math,os
import pythonaddins 


print(os.path)
class BusquedaPuntoParalelo(object):
    def __init__(self):
        self.fileArboles="1065_san_jorge_arboles_merge"
        self.fileAuxi="auxiliar"
        self.fileCamino="1065_san_jorge_caminos"
        self.fileNoCultivable="1065_san_jorge_area_nocultivable"
        self.fileDesechos="1065_san_jorge_desechos_depurados"
        self.fileEjecucion=""
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
            with arcpy.da.SearchCursor(self.fileArboles,["SHAPE@XY","nro_linea","valido"],""""FID"={}""".format(fid)) as cursor:
                for row in cursor:
                    if row[1]!=-1 and row[2]!=1:
                        listaPuntos.append((fid,row[0],row[1],row[2]))
                    elif (row[1]!=self.nrLinea or row[1]==self.nrLinea) and row[2]==1 and row[1]!=-1:
                        otroP=True
        if(nroPuntos>=2 and len(listaPuntos)==1 and otroP==True):
            print("Encontre puntos que ya son visitados")
            nroPuntos=0
        else:
            nroPuntos=len(listaPuntos)
        print("Los Puntos Son: {}".format(listaPuntos))
        return listaPuntos,nroPuntos
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
        print("alfa nuevo: {}, alfa antiguo {}".format(anguloNuevo,self.angulo))
        if abs(anguloNuevo-self.angulo)<=0.2:
            print("..... Nos quedamos con el nuevo angulo")
            self.angulo=anguloNuevo
    def anguloCorrecto(self):
        anguloNuevo=self.getAngulo(self.punto1[1],self.punto2[1])
        if abs(anguloNuevo-self.angulo)>0.2:
            return False
        else:
            return True
    def busquedaLineal(self):
        #formato puntos [fid,punto,nro_linea,valido]
        n=0
        distancia=0
        angulo=0
        while self.runProg:
            puntos,np=self.getSeleccion()
            if np==2:
                distancia=self.getDistancia(puntos[0][1],puntos[1][1])
                if distancia<self.distancia and distancia>1:
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
                    self.validarAngulo()
                    self.setNroLine(self.punto2[0],-1,1)
                    self.setNroLine(self.punto1[0],0,2)
                    self.punto2=self.punto1
                    self.valido=True
            elif np==1:
                distancia+=0.2
                self.valido=True
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
                if self.estaEnArea()==True:
                    self.setNroLine(self.punto2[0],self.nrLinea,1)
                    self.runProg=False
                    self.limpiarAux()
                    self.clearProg()
        self.limpiarAux()
    def busquedaParalela(self):
        while self.runPara:
            puntosP,npP=self.getSeleccion()
            if npP==2:
                self.clearProg()
                self.runProg=True
                #busqueda derecha
                self.setNroLine(puntosP[0][0],0,2)
                self.setNroLine(puntosP[1][0],0,0)
                self.distancia=self.getAngulo(puntosP[0][1],puntosP[1][1])
                self.angulo=self.getAngulo(puntosP[0][1],puntosP[1][1])
                try:
                    print("....Busqueda De un lado ........")
                    self.busquedaLineal()
                except Exception as err:
                    pythonaddins.MessageBox ("ocurrio un Error: {}".format(err), "Informacion")
                    self.runPara=False
                '''#busqueda izquierda
                self.clearProg()
                self.runProg=True
                self.colocarPunto(puntosP[1][1],puntosP[0][1])
                puntosP,npP=self.getSeleccion()
                self.setNroLine(puntosP[1][0],0,2)
                self.setNroLine(puntosP[0][0],0,0)
                self.distancia=self.getAngulo(puntosP[1][1],puntosP[0][1])
                self.angulo=self.getAngulo(puntosP[1][1],puntosP[0][1])
                try:
                    print("....Busqueda De otro lado ........")
                    self.busquedaLineal()
                except Exception as err:
                    pythonaddins.MessageBox ("ocurrio un Error: {}".format(err), "Informacion")
                    self.runPara=False'''
                busco=True
                distancia=self.getDistancia(puntosP[0][1],puntosP[1][1])
                angulo=self.getAngulo(puntosP[0][1],puntosP[1][1])
                m=self.getPendiente(puntosP[0][1],puntosP[1][1])
                distaP=distancia
                while not self.estaEnArea() and busco:
                    punto=self.getPuntoParalelo(puntosP[0][1],distaP,m,0)
                    self.agregarPunto(punto)
                    disP=distancia
                    p,npG=self.getSeleccion()
                    if npG==1:
                        busco2=True
                        while busco2 and not self.estaEnArea():
                            pb=self.aumentarDpunto(p[0][1],disP,angulo)
                            self.agregarPunto(pb)
                            ppp,npp=self.getSeleccion()
                            if npp==1:
                                busco2=False
                                busco=False
                                self.colocarPunto(ppp[0][1],p[0][1])
                                self.nrLinea+=1
                            elif npp==2:
                                self.setNroLine(ppp[0][0],-1,1)
                            else:
                                disP+=0.2
                    elif npG==2:
                        self.setNroLine(p[0][0],-1,1)
                    else:
                        distaP+=0.2
            elif npP==3:
                self.runPara=False
                self.limpiarAux()
            elif npP==0:
                self.runPara=False
                self.limpiarAux()

    def aumentarDpunto(self,punto,distancia,angulo):
        xa=punto[0]+distancia*math.cos(angulo)
        ya=punto[1]+distancia*math.sin(angulo)
        return (xa,ya)
    def agregarPunto(self,punto):
        arcpy.DeleteFeatures_management(self.fileAuxi)
        with arcpy.da.InsertCursor(self.fileAuxi,"SHAPE@XY") as cursor:
            cursor.insertRow([punto])
        arcpy.RefreshActiveView()
    def getPuntoParalelo(self,punto,distancia,pendiente,tipo):
        #x=punto[0]+distancia*math.cos(angulo)
        if tipo==0:
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

'''
class BusquedaPunto(object):
    def __init__(self):
        self.filename="arboles"
        self.fileAuxi="auxiliar"
        self.fileCamino="709_caminos3"
        self.fileNoCultivable="709_nocultivable3"
        self.fileDesechos="709_caminos3"
        self.nrLinea=0
        self.runPara=False
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
    def maxNroLine(self):
        nroLinea=0
        try:
            with arcpy.da.SearchCursor(self.filename,['nro_linea'],'"nro_linea">0',None,None,sql_clause=("TOP 1","ORDER BY MAX(nro_linea) DESC")) as cursor:
                nroLinea=max(cursor)[0]+1
        except:
            nroLinea=1
        self.nrLinea=nroLinea
    def getDistancia(self,pa,pb):
        res=math.sqrt(math.pow(pa[1]-pb[1],2)+math.pow(pa[0]-pb[0],2))
        return res
    def getAngulo(self,pa,pb,tipo):
        alfa=math.atan2(pa[1]-pb[1],pa[0]-pb[0])
        if tipo==0 and alfa<0:
            return alfa
        elif tipo==0 and alfa>=0:
            print("cambio de angulo :")
            self.cambioPuntos()
            return self.getAngulo(pb,pa,tipo)
        elif tipo==1 and alfa>=0:
            return alfa
        elif tipo==1 and alfa<0:
            print("cambio de angulo :")
            self.cambioPuntos()
            return self.getAngulo(pb,pa,tipo)
    def cambioPuntos(self):
        aux=self.punto1
        self.punto1=self.punto2
        self.punto2=aux
    def getSeleccion(self):
        listaPuntos=list()
        dato=arcpy.SelectLayerByLocation_management(self.filename,"WITHIN_A_DISTANCE",self.fileAuxi,"100 Centimeters","NEW_SELECTION")
        nroPuntos=int(arcpy.GetCount_management(self.filename)[0])
        print("total Seleccionados: {}".format(arcpy.GetCount_management(self.filename)[0]))
        for i in range(nroPuntos):
            fid=dato.getOutput(0).getSelectionSet()[i]
            if self.esValidoPunto(fid):
                listaPuntos.append(fid)
        print("Los Puntos Son: {}".format(listaPuntos))
        return listaPuntos,len(listaPuntos)
    def esValidoPunto(self,fid):
        valor=True
        with arcpy.da.SearchCursor(self.filename,["SHAPE@XY","nro_linea"],""""FID"={}""".format(fid)) as cursor:
            for row in cursor:
                if row[1]==-1:
                    print("punto no valido: "+str(fid))
                    valor=False 
        return valor
    def dentroDeArea(self,capa1,capa2):
        arcpy.SelectLayerByLocation_management(capa1,"INTERSECT",capa2,"","NEW_SELECTION")
        nroPuntos=int(arcpy.GetCount_management(capa1)[0])
        if nroPuntos==0:
            return  False
        else:
            return True
    def runBusquedaParalela(self):
        dIn=100000
        n=0
        while self.runPara:
            puntos,nroP=self.getSeleccion()
            print("Nuevo numero de linea : "+str(self.nrLinea))
            n+=1
            if nroP>0:
                _,_,valorPs=self.getPuntos(puntos,0)
                print(valorPs)
                if len(valorPs)>=2:
                    #self.setNroLine(valorPs[0][0],self.nrLinea)
                    #self.setNroLine(valorPs[1][0],self.nrLinea)
                    di=self.getDistancia(valorPs[0][1],valorPs[1][1])
                    if di<dIn:
                        dIn=di
                    else:
                        di=dIn
                    alfa=self.getAngulo(valorPs[0][1],valorPs[1][1],0)
                    m=self.getPendiente(valorPs[0][1],valorPs[1][1])
                    print("Distanica: {}, alfa: {}, pendiente: {}".format(di,alfa,m))
                    try:
                        self.runProg=True
                        self.runBusqueda(0)
                        #self.busquedaLineal(valorPs,1,nroP)
                        #print("Busqueda lineal Activado")
                        #self.busquedaLin(0,puntos[0])
                        self.clearProg()
                    except Exception as err:
                        print("Problema:: {}".format(err))
                        pythonaddins.MessageBox ("Error: {}".format(err), "Error")
                    cont=0
                    diP=di
                    while cont<=8:
                        a=self.getPuntoParalelo(valorPs[1][1],diP,m,1)
                        self.agregarPunto(a)
                        if self.dentroDeArea(self.fileCamino,self.fileAuxi) or self.dentroDeArea(self.fileDesechos,self.fileAuxi) or self.dentroDeArea(self.fileNoCultivable,self.fileAuxi):
                            cont=10
                            n=100
                            self.runPara=False
                            self.limpiarAux()
                            pythonaddins.MessageBox ("Termino de Ejecutar", "Finalizo")
                        else:
                            dat,nd=self.getSeleccion()
                            cont+=1
                            b=()
                            if nd!=0:
                                i=0
                                dis=di-2
                                _,_,newP=self.getPuntos(dat,0)
                                while i<=5:
                                    b=self.aumentarDpunto(newP[0][1],dis,alfa)
                                    self.agregarPunto(b)
                                    dat,e=self.getSeleccion()
                                    dis+=0.2
                                    if e!=0:
                                        i=100
                            else:
                                diP+=0.4
                            if len(b)!=0 and len(a)!=0:
                                self.nrLinea+=1
                                cont=100
                                self.limpiarAux()
                                self.colocarPunto(a,b)                       
    def getPendiente(self,punto1,punto2):
        m= (punto2[1]-punto1[1])/(punto2[0]-punto1[0])
        return m
    def agregarPunto(self,punto):
        arcpy.DeleteFeatures_management(self.fileAuxi)
        arcpy.RefreshActiveView()
        with arcpy.da.InsertCursor(self.fileAuxi,"SHAPE@XY") as cursor:
            cursor.insertRow([punto])
    def getPuntoParalelo(self,punto,distancia,pendiente,tipo):
        #x=punto[0]+distancia*math.cos(angulo)
        if tipo==0:
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
    def aumentarDpunto(self,punto,distancia,angulo):
        xa=punto[0]+distancia*math.cos(angulo)
        ya=punto[1]+distancia*math.sin(angulo)
        return (xa,ya)
    def runBusqueda(self,tipo):
        n=0
        puntosAntiguos=[]
        print("Seteo de linea nro: {}".format(self.nrLinea))
        while self.runProg:
            puntos,nroP=self.getSeleccion()
            if nroP>2:
                if nroP==3:
                    puntoFID,valorPs=self.getPuntosFID(puntos,self.nrLinea)
                    print("puntoFid: {}".format(puntoFID))
                    print("puntos: {}".format(valorPs))
                    if len(valorPs)==2:
                        disab=self.getDistancia(puntoFID[0][1],valorPs[0][1])
                        disac=self.getDistancia(puntoFID[0][1],valorPs[1][1])
                        print("distancias 1 {}, 2 {}".format(disab,disac))
                        if disab-self.distancia<disac-self.distancia:
                            self.setNroLine(valorPs[1][0],-1)
                            valorPs.pop(1)
                        else:
                            self.setNroLine(valorPs[0][0],-1)
                            valorPs.pop(0)
                        self.punto1=puntoFID[0][1]
                        self.punto2=valorPs[0][1]
                        self.setNroLine(puntoFID[0][0],self.nrLinea)
                        self.setNroLine(valorPs[0][0],self.nrLinea)
                        if len(puntosAntiguos)>=2:
                            puntosAntiguos.clear()
                        puntosAntiguos.append(puntoFID[0][0])
                        puntosAntiguos.append(valorPs[0][0])
                        self.valido=True
                        self.validarAngulo(tipo)
                    else:
                        self.punto1=puntoFID[0][1]
                        self.punto2=valorPs[0][1]
                        self.setNroLine(puntoFID[0][0],self.nrLinea)
                        self.setNroLine(valorPs[0][0],self.nrLinea)
                        if len(puntosAntiguos)>=2:
                            puntosAntiguos.clear()
                        puntosAntiguos.append(puntoFID[0][0])
                        puntosAntiguos.append(valorPs[0][0])
                        self.valido=True
                        self.validarAngulo(tipo)
                else:
                    puntoFID,valorPs=self.getPuntosFID(puntos,self.nrLinea)
                    if len(puntoFID)!=0:
                        print("punto:::fid   {}".format(puntoFID[0][1]))
                        if len(valorPs)==3:
                            lista=[]
                            for p in valorPs:
                                d1=self.getDistancia(puntoFID[0][1],p[1])
                                lista.append(abs(d1-self.distancia))
                            vv=lista.index(min(lista))
                            for p in valorPs:
                                if p[0]!=valorPs[vv][0]:
                                    self.setNroLine(p[0],-1)
                            valorPs=valorPs[vv]
                            self.punto1=puntoFID[0][1]
                            self.punto2=valorPs[1]
                            self.setNroLine(puntoFID[0][0],self.nrLinea)
                            self.setNroLine(valorPs[0],self.nrLinea)
                            if len(puntosAntiguos)>=2:
                                puntosAntiguos.clear()
                            puntosAntiguos.append(puntoFID[0][0])
                            puntosAntiguos.append(valorPs[0][0])
                            self.runProg=True   
                            self.validarAngulo(tipo)
                    else:
                        self.runProg=False
                        self.limpiarAux()
            elif nroP==2:
                if not self.Iguales(puntosAntiguos,puntos):
                    self.valido=True
                    _,_,valorPs=self.getPuntos(puntos,1)
                    if len(valorPs)==2:
                        self.punto1=valorPs[0][1]
                        self.punto2=valorPs[1][1]
                        self.setNroLine(valorPs[0][0],self.nrLinea)
                        self.setNroLine(valorPs[1][0],self.nrLinea)
                        self.area=0.5
                        if self.distancia==0:
                            self.distancia=self.getDistancia(self.punto1,self.punto2)
                            self.angulo=self.getAngulo(self.punto1,self.punto2,tipo)
                        if len(puntosAntiguos)>=2:
                            puntosAntiguos.clear()
                        puntosAntiguos.append(valorPs[0][0])
                        puntosAntiguos.append(valorPs[1][0])
                        self.validarAngulo(tipo)
                    else:
                        self.runProg=False
                        self.limpiarAux()
                else:
                    pythonaddins.MessageBox ("Se tuvo un book", "Error")
                    self.runProg=False
                    self.limpiarAux()
            elif nroP==1:
                    self.valido=False
                    if self.area<=10:
                        self.aumentarDistancia(self.distancia+self.area,self.angulo)
                        self.area+=0.5
                    else:
                        self.area=0.5
                        n=1000
                        self.limpiarAux()
                        self.runProg=False
            if self.valido:
                print("D = {} alfa= {}".format(self.distancia,self.angulo))
                puntoNew,puntoAntiguo=self.getPuntoSugerido(self.distancia,self.angulo)
                self.colocarPunto(puntoNew,puntoAntiguo)
                if self.dentroDeArea(self.fileCamino,self.fileAuxi) or self.dentroDeArea(self.fileDesechos,self.fileAuxi) or self.dentroDeArea(self.fileNoCultivable,self.fileAuxi):
                    print("dentro de un area no ejecutable")
                    self.limpiarAux()
                    n=10000
                    self.runProg=False
                n+=1
           
        print("termino la ejecucion")
    def Iguales(self,puntosA,puntos):
        if len(puntosA)==0:
            return False
        else:
            if (puntosA[0]==puntos[0] and puntosA[1]==puntos[1]) or (puntosA[0]==puntos[1] and puntosA[1]==puntos[0]):
                return True
            else:
                return False
    def busquedaLin(self,sentido,puntoOrigen):
        n=0
        while self.runProg:
            puntos,nroP=self.getSeleccion()
            if nroP>2:
                self.valido=False
                
            elif nroP==2:
                self.valido=True
                _,_,valorPs=self.getPuntos(puntos)
                print("Los puntos son {}".format(valorPs))
                if len(valorPs)==2:
                    for i in valorPs:
                        print(i)
                        if i[0]==puntoOrigen:
                            self.punto1=i
                            self.setNroLine(self.punto1[0],self.nrLinea)
                        else:
                            self.punto2=i
                    if self.distancia==0:
                        self.distancia=self.getDistancia(self.punto1[1],self.punto2[1])
                        self.angulo=self.getAngulo2(self.punto1[1],self.punto2[1])
                    #self.validarAngulo2()
                    self.runProg=True
                else:
                    self.punto1=valorPs[0]
                    self.runProg=False
                self.area=0.5
            elif nroP==1:
                self.valido=False
                if self.area<=5:
                    self.aumentarDistancia(self.distancia+self.area,self.angulo)
                    self.area+=0.5
                else:
                    self.area=0.5
                    n=1000
                    self.runProg=False
            if self.valido:
                self.setNroLine(self.punto1[0],self.nrLinea)
                print("Punto1: {} , Punto2: {}".format(self.punto1,self.punto2))
                print("D = {} alfa= {}".format(self.distancia,self.angulo))
                puntoNew,puntoAntiguo=self.getPuntoSugerido2(self.punto2,self.distancia,self.angulo)
                print("PuntoNew: {} , PuntoOld: {}".format(puntoNew,puntoAntiguo))
                self.colocarPunto(puntoNew,puntoAntiguo)
                if self.dentroDeArea("1065_san_jorge_desechos_depurados","auxiliar") or self.dentroDeArea("1065_san_jorge_caminos","auxiliar") or self.dentroDeArea("1065_san_jorge_area_nocultivable","auxiliar"):
                    print("dentro de un area no ejecutable")
                    self.limpiarAux()
                    n=10000
                    self.runProg=False
                n+=1
        print("termino la ejecucion")

    def busquedaLineal(self,puntos,sentido,nroPo):
        puntosSel=puntos
        self.punto1=puntos[0]
        self.punto2=puntos[1]
        nroP=nroPo
        offset=0
        d=self.getDistancia(self.punto1[1],self.punto2[1])
        alfa=self.getAngulo2(self.punto1[1],self.punto2[1])
        while self.runProg:
            print("punto1: {}, punto2: {}".format(self.punto1,self.punto2))
            print("distancia: {} , angulo: {}".format(d,alfa))
            if nroP==2:
                self.setNroLine(self.punto1[0],self.nrLinea)
                self.valido=True
            if self.valido:
                puntoNew,puntoAn=self.getPuntovalido(self.punto1[1],self.punto2[1],d+offset,alfa)
                print("new p: {} , punto An: {}".format(puntoNew,puntoAn))
                self.colocarPunto(puntoNew,puntoAn)
                if self.dentroDeArea("1065_san_jorge_desechos_depurados","auxiliar") or self.dentroDeArea("1065_san_jorge_caminos","auxiliar") or self.dentroDeArea("1065_san_jorge_area_nocultivable","auxiliar"):
                    print("Esta dentro de un area")                     
                    self.limpiarAux()
                    self.runProg=False
                else:
                    puntosA,nroP=self.getSeleccion()
                    _,_,puntosSel=self.getPuntos(puntosA)
                    if nroP==1:
                        offset+=0.3
                    elif nroP==2:
                        offset=0
                        if len(puntosSel)==2:
                            for i in puntosSel:
                                print(i)
                                if i[1][0]==self.punto2[1][0] and i[1][1]==self.punto2[1][1]:
                                    print("Ya es igual")
                                    self.punto1=self.punto2
                                else:
                                    self.punto2=i
                            alfan=self.getAngulo2(self.punto1[1],self.punto2[1])
                            if abs(alfan-alfa)<=0.2:
                                alfa=alfan
                        else:
                            self.setNroLine(self.punto1[0],0)
                            alfa=self.getAngulo2(self.punto2[1],self.punto1[1])
                            puntoNew,puntoAn=self.getPuntovalido(self.punto1[1],self.punto2[1],d+offset,alfa)
                            print("new p: {} , punto An: {}".format(puntoNew,puntoAn))
                            self.colocarPunto(puntoNew,puntoAn)
                            puntosA,nroP=self.getSeleccion()
                            _,_,puntosSel=self.getPuntos(puntosA)
                            for i in puntosSel:
                                print(i)
                                if i[1][0]==self.punto2[1][0] and i[1][1]==self.punto2[1][1]:
                                    print("Ya es igual")
                                    self.punto1=self.punto2
                                else:
                                    self.punto2=i
                            alfan=self.getAngulo2(self.punto1[1],self.punto2[1])
                            if abs(alfan-alfa)<=0.2:
                                alfa=alfan
                            self.runProg=True
                    elif nroP>=3:
                        self.runProg=False
                        print("Son tres puntos")
                    
    def getPuntoSugerido2(self,punto,d,alfa):
        xa=punto[1][0]+d*math.cos(alfa)
        ya=punto[1][1]+d*math.sin(alfa)
        self.agregarPunto((xa,ya))
        puntos,nrp=self.getSeleccion()
        for i in puntos:
            if i==punto[0]:
                tita=self.getAngulo2(self.punto2,self.punto1)
                xa=punto[1][0]+d*math.cos(tita)
                ya=punto[1][1]+d*math.sin(tita)
        return (xa,ya),self.punto2[1]

    def getPuntovalido(self,punto1,punto2,d,alfa):
        xa=punto2[0]+d*math.cos(alfa)
        ya=punto2[1]+d*math.sin(alfa)
        if (int(xa),int(ya))==(int(punto1[0]),int(punto1[1])):
            print("Nuevo angulo inverso")
            alfa=self.getAngulo2(punto2,punto1)
            xa=punto2[0]+d*math.cos(alfa)
            ya=punto2[1]+d*math.sin(alfa)
            return (xa,ya),punto2
        else:
            return (xa,ya),punto2
    def getAngulo2(self,pa,pb):
        alfa=math.atan2(pb[1]-pa[1],pb[0]-pa[0])
        return alfa
    def limpiarAux(self):
        arcpy.DeleteFeatures_management("auxiliar")
    def validarAngulo2(self):
        anguloNuevo=self.getAngulo2(self.punto1[1],self.punto2[1])
        if abs(anguloNuevo-self.angulo)<=0.2:
            print("cambie de angulo")
            self.angulo=self.getAngulo2(self.punto1[1],self.punto2[1])
    def validarAngulo(self,tipo):
        anguloNuevo=self.getAngulo(self.punto1,self.punto2,tipo)
        print("alfa nuevo: {}, alfa antiguo {}".format(anguloNuevo,self.angulo))
        if abs(anguloNuevo-self.angulo)<=1.2:
            self.angulo=self.getAngulo(self.punto1,self.punto2,tipo)
    def aumentarDistancia(self,distancia,angulo):
        xa=self.punto1[0]+distancia*math.cos(angulo)
        ya=self.punto1[1]+distancia*math.sin(angulo)
        print("puntoNuevo segun1 aumentado distancia= {}".format((xa,ya)))
        self.colocarPunto((xa,ya),self.punto1)
    def colocarPunto(self,puntoNew,puntoAntiguo):
        arcpy.DeleteFeatures_management(self.fileAuxi)
        arcpy.RefreshActiveView()
        with arcpy.da.InsertCursor(self.fileAuxi,"SHAPE@XY") as cursor:
            cursor.insertRow([puntoNew])
        with arcpy.da.InsertCursor(self.fileAuxi,"SHAPE@XY") as cursor:
            cursor.insertRow([puntoAntiguo])
        del cursor
    def getPuntoSugerido(self,distancia,angulo):
        puntoV=self.punto1
        xa=self.punto1[0]+distancia*math.cos(angulo)
        ya=self.punto1[1]+distancia*math.sin(angulo)
        diferencia=(self.punto2[0]-xa,self.punto2[1]-ya)
        print("puntoNuevo segun1 = {} dif={}".format((xa,ya),diferencia))
        if diferencia[0]==0 and diferencia[1]==0:
            xa=self.punto2[0]+distancia*math.cos(angulo)
            ya=self.punto2[1]+distancia*math.sin(angulo)
            diferencia=(self.punto1[0]-xa,self.punto1[1]-ya)
            print("puntoNuevo segun2 = {} dif={}".format((xa,ya),diferencia))
            puntoV=self.punto2
            self.punto1=[]
        else:
            self.punto2=[]
        return (xa,ya),puntoV
    def setNroLine(self,fid,num):
        with arcpy.da.UpdateCursor(self.filename, "nro_linea",""""FID"={}""".format(fid)) as curs:
            for row in curs:
                row[0] = num
                curs.updateRow(row)
    def getPuntos(self,lista,tipo):
        fidl,datos,newp=[],[],[]
        for i in lista:
            with arcpy.da.SearchCursor(self.filename,["SHAPE@XY","nro_linea"],""""FID"={}""".format(i)) as cursor:
                if tipo==1:
                    for row in cursor:
                        if row[1]==-1:
                            fidl.append([i,row[0]])
                        elif row[1]==self.nrLinea or row[1]==0:
                            newp.append([i,row[0]])
                        else:
                            datos.append([i,row[0]])
                elif tipo==0:
                    for row in cursor:
                        if row[1]==-1:
                            fidl.append([i,row[0]])
                        elif row[1]==0:
                            newp.append([i,row[0]])
                        else:
                            datos.append([i,row[0]])
        return fidl,datos,newp
    def getPuntosFID(self,lista,num):
        fidl,datos=[],[]
        for i in lista:
            with arcpy.da.SearchCursor(self.filename,["SHAPE@XY","nro_linea"],""""FID"={}""".format(i)) as cursor:
                for row in cursor:
                    if row[1]==num:
                        fidl.append([i,row[0]])
                    elif row[1]==0:
                        datos.append([i,row[0]])
        return fidl,datos'''