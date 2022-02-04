import arcpy
import pythonaddins
arcpy.env.workspace=r"D:/ArcGisTrabajo/1065_agregado_arboles"
class ButtonClass5(object):
    """Implementation for myAddIn_addin.button1 (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
        self.entrada="1065_san_jorge_arboles_merge.shp"
        self.salida="arbolesRadio001m.shp"
        self.distancia="1 Meters"
    def onClick(self):
        arcpy.Buffer_analysis(self.entrada,self.salida,self.distancia)
        print("EjecutoCodigo")
        pass