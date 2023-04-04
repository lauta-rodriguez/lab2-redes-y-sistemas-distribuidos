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
        pass

    def read_line(self, buffer):
        """
        Lee una línea del socket, y se queda con el segmento del buffer hasta EOL.
        """

        while (not EOL in buffer) or (len(buffer) > MAX_BUFFER):
            buffer += self.socket.recv(BUFFER_SIZE)

        if len(buffer) > MAX_BUFFER:
            return "None", buffer

        line, buffer = buffer.split(EOL, 1)
        return line, buffer

    def handle(self):
        """
        Atiende eventos de la conexión hasta que termina.
        """
        pass
