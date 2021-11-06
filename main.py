import json
import xlrd, sys
import requests
import pandas as pd
import numpy as nm
import urllib
import shutil
import logging


from PyQt5.QtWidgets import (QApplication, QMessageBox, QMainWindow)

from PyQt5.QtGui import QPixmap

from rover import Ui_MainWindow

#Crea el log
logging.basicConfig(filename='mars_log.log', format='%(asctime)s : %(levelname)s : %(message)s', datefmt='%d/%m/%y %H:%M:%S', filemode='w')



class Ventana(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.datos()
        self.connexionSenalesRanuras()


    def datos(self):

        #cargamos el contenido del xls que hemos creado con todas las cámaras
        df = pd.read_excel(io="cameras.xls", sheet_name="Hoja1")
        self.camarasRover = df.to_numpy()
        cameras = []

        #creamos un array para introducir las siete cámaras (con sus códigos)
        for i in range(0, 6):
            cameras.append(self.camarasRover[i][0])
        self.comboCamera.addItems(cameras)

        #abre y lee el registro para "recordar" que cámara se eligió la última vez
        f = open('registro.txt')
        camara = int(f.read())
        f.close()


        self.comboCamera.setCurrentIndex(camara)

        #mostrar resultado cuando se cambia la fecha o la cámara
        self.comboCamera.currentIndexChanged.connect(self.cargarDatos)
        self.earthDate.dateChanged.connect(self.cargarDatos)

    def cargarDatos(self):

        #establecemos los strings para pasarlos como parámetros en la url de conexión con la API
        cam = self.camarasRover[self.comboCamera.currentIndex()][1]

        #pasamos fecha a string
        date = self.earthDate.dateTime()
        dt_string: str = date.toString(self.earthDate.displayFormat())

        #url de la API de la NASA pasando los parámetros de fecha y cámara
        url = 'https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos?earth_date=' + dt_string + '&camera=' + str(cam) + '&api_key=DEMO_KEY'
        self.favorito()


        try:
            resp = requests.get(url=url)
            self.data = resp.json()

        except:
            self.mensajeError();
            logging.warning('No ha podido conectar con la url')

        try:

            self.lcdSol.display(self.data['photos'][0]['sol'])

            #pasamos la url como string
            urlPic = (self.data['photos'][0]['img_src'])

            #obtenemos la imagen a partir de la url
            response = requests.get(urlPic, stream=True)
            with open('my_image.png', 'wb') as file:
                shutil.copyfileobj(response.raw, file)
            del response

            #mostramos la imagen capturada en el qlabel
            self.im=QPixmap('my_image.png')
            self.imagen.setPixmap(self.im)



        except:
            self.mensajeNoFoto(); #no hay fotos todos los días con todas las cámaras
            logging.warning('No se ha encontrado foto')

    #muestra mensaje de error de conexión (internet ko)
    def mensajeError(self):
        mensaje = QMessageBox()
        mensaje.setIcon(QMessageBox.Warning)
        mensaje.setInformativeText("Ha habido un problema con la conexión, inténtalo de nuevo más tarde")
        mensaje.setWindowTitle("Error")
        mensaje.exec_()

    #avisa que no hay foto ese día
    def mensajeNoFoto(self):
        mensaje = QMessageBox()
        mensaje.setIcon(QMessageBox.Warning)
        mensaje.setInformativeText("El Curiosity no tomó una foto con la cámara elegida en la fecha señalada.")
        mensaje.setWindowTitle("Aviso")
        mensaje.exec_()

    #guardamos la cámara elegida
    def favorito(self):
        f = open("registro.txt", "w")
        f.write(str(self.comboCamera.currentIndex()))
        f.close()

    def connexionSenalesRanuras(self):
        self.action_AcercaDe.triggered.connect(self.acercaDe)

    #definimos el ayuda/acerca de
    def acercaDe(self):
        mensaje = QMessageBox()
        mensaje.setIcon(QMessageBox.Information)
        mensaje.setInformativeText("<p>Mars Control: < / p > < p > - PyQt < / p > < p > - QtDesigner < / p > < p > - Python < / p > < p > - Mars Rover Photos API < / p >")
        mensaje.setWindowTitle("Acerca de Mars Control")
        mensaje.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = Ventana()
    gui.show()
    sys.exit(app.exec())
