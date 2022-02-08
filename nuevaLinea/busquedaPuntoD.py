import arcpy,math

class BusquedaPunto(object):
    def __init__(self):
        self.filename="1065_san_jorge_arboles_merge"
        self.fileAuxi="auxiliar"
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
        self.nrLinea=0
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
        dato=arcpy.SelectLayerByLocation_management(self.filename,"WITHIN_A_DISTANCE",self.fileAuxi,"70 Centimeters","NEW_SELECTION")
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
        n=0
        self.nrLinea=1
        while n<1:
            puntos,nroP=self.getSeleccion()
            print("Nuevo numero de linea : "+str(self.nrLinea))
            n+=1
            if nroP>0:
                _,_,valorPs=self.getPuntos(puntos)
                print(valorPs)
                if len(valorPs)>=1:
                    #self.setNroLine(valorPs[0][0],self.nrLinea)
                    #self.setNroLine(valorPs[1][0],self.nrLinea)
                    di=self.getDistancia(valorPs[0][1],valorPs[1][1])
                    alfa=self.getAngulo(valorPs[0][1],valorPs[1][1],0)
                    m=self.getPendiente(valorPs[0][1],valorPs[1][1])
                    print("Distanica: {}, alfa: {}, pendiente: {}".format(di,alfa,m))
                    #for i in range(2):
                    self.runProg=True
                    self.runBusqueda(0)
                    #self.busquedaLineal(valorPs,1,nroP)
                    #print("Busqueda lineal Activado")
                    self.busquedaLin(0,puntos[0])
                    #self.clearProg()
                    '''cont=0
                    diP=di
                    while cont<=5:
                        a=self.getPuntoParalelo(valorPs[1][1],diP,m,1)
                        self.agregarPunto(a)
                        if self.dentroDeArea("1065_san_jorge_desechos_depurados","auxiliar") or self.dentroDeArea("1065_san_jorge_caminos","auxiliar") or self.dentroDeArea("1065_san_jorge_area_nocultivable","auxiliar"):
                            cont=10
                            n=100
                        else:
                            dat,nd=self.getSeleccion()
                            cont+=1
                            b=()
                            if nd!=0:
                                i=0
                                dis=di
                                _,newP=self.getPuntos(dat)
                                while i<=3:
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
                                self.colocarPunto(a,b)'''
                         
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
        while self.runProg:
            puntos,nroP=self.getSeleccion()
            if nroP>2:
                puntoFID,valorPs=self.getPuntosFID(puntos,1)
                print("puntoFid: {}".format(puntoFID))
                print("puntos: {}".format(valorPs))
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
                self.valido=True
                self.validarAngulo(tipo)
            elif nroP==2:
                self.valido=True
                _,_,valorPs=self.getPuntos(puntos)
                self.punto1=valorPs[0][1]
                self.punto2=valorPs[1][1]
                self.setNroLine(valorPs[0][0],1)
                self.setNroLine(valorPs[1][0],1)
                self.area=0.5
                if self.distancia==0:
                    self.distancia=self.getDistancia(self.punto1,self.punto2)
                    self.angulo=self.getAngulo(self.punto1,self.punto2,tipo)
                self.validarAngulo(tipo)
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
                print("D = {} alfa= {}".format(self.distancia,self.angulo))
                puntoNew,puntoAntiguo=self.getPuntoSugerido(self.distancia,self.angulo)
                self.colocarPunto(puntoNew,puntoAntiguo)
                if self.dentroDeArea("1065_san_jorge_desechos_depurados","auxiliar") or self.dentroDeArea("1065_san_jorge_caminos","auxiliar") or self.dentroDeArea("1065_san_jorge_area_nocultivable","auxiliar"):
                    print("dentro de un area no ejecutable")
                    self.limpiarAux()
                    n=10000
                    self.runProg=False
                n+=1
        print("termino la ejecucion")
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
        if abs(anguloNuevo-self.angulo)<=0.2:
            self.angulo=self.getAngulo(self.punto1,self.punto2,tipo)
    def aumentarDistancia(self,distancia,angulo):
        xa=self.punto1[0]+distancia*math.cos(angulo)
        ya=self.punto1[1]+distancia*math.sin(angulo)
        print("puntoNuevo segun1 aumentado distancia= {}".format((xa,ya)))
        self.colocarPunto((xa,ya),self.punto1)
    def colocarPunto(self,puntoNew,puntoAntiguo):
        arcpy.DeleteFeatures_management(self.fileAuxi)
        arcpy.RefreshActiveView()
        '''with arcpy.da.UpdateCursor("auxiliar","*") as curs:
            for row in curs:
                curs.deleteRow()
        arcpy.RefreshActiveView()'''
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
    def getPuntos(self,lista):
        fidl,datos,newp=[],[],[]
        for i in lista:
            with arcpy.da.SearchCursor(self.filename,["SHAPE@XY","nro_linea"],""""FID"={}""".format(i)) as cursor:
                for row in cursor:
                    if row[1]==-1:
                        fidl.append([i,row[0]])
                    #elif row[1]==0:
                     #   newp.append([i,row[0]])
                    else:
                        newp.append([i,row[0]])
        return fidl,datos,newp
    def getPuntosFID(self,lista,num):
        fidl,datos=[],[]
        for i in lista:
            with arcpy.da.SearchCursor(self.filename,["SHAPE@XY","nro_linea"],""""FID"={}""".format(i)) as cursor:
                for row in cursor:
                    if row[1]==num:
                        fidl.append([i,row[0]])
                    else:
                        datos.append([i,row[0]])
        return fidl,datos
