# encoding: utf-8
# Revisión 2019 (a Python 3 y base64): Pablo Ventura
# Copyright 2014 Carlos Bederián
# $Id: connection.py 455 2011-05-01 00:32:09Z carlos $

import socket
from constants import *
from base64 import b64encode

class Connection(object):
    """
    Conexión punto a punto entre el servidor y un cliente.
    Se encarga de satisfacer los pedidos del cliente hasta
    que termina la conexión.
    """

    def __init__(self, socket, directory):
        # FALTA: Inicializar atributos de Connection
        self.socket = socket
        self.directory = directory
    
    def send(self, estado, mensaje):
        """
        Envía un mensaje al cliente.
        """
        try:
            self.socket.sendall(estado.encode())
            self.socket.sendall(mensaje.encode())
            return True
        except:
            self.socket.close()
            raise Exception("Error al enviar el mensaje")

    def handle(self):
        """
        Atiende eventos de la conexión hasta que termina.
        """
        try:
            while True:
                data = self.socket.recv(DEFAULT_PORT)
                if not data:
                    break
                self.socket.sendall(data)
                self.socket.close()
                return True
        except:
            self.socket.close()
            raise Exception("Handle error")
