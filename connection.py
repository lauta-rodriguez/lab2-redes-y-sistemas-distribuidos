# encoding: utf-8
# Revisión 2019 (a Python 3 y base64): Pablo Ventura
# Copyright 2014 Carlos Bederián
# $Id: connection.py 455 2011-05-01 00:32:09Z carlos $

import socket
from constants import *
from base64 import b64encode
from commands import *

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
        buffer = b""
        while self.is_connected:
            # En line: una linea que termina con EOL, en buffer: resto del byte stream
            line, buffer = self.read_line(buffer)
            if not line:
                # El line es muy largo (más que MAX_BUFFER), (i.e., no pudimos leer una linea valida)
                # Antes de cerrar la conexión, enviamos un mensaje de error
                self.send(BAD_REQUEST, error_messages[BAD_REQUEST])
                self.socket.close()
                self.is_connected = False
                break

            # Parseamos la linea y extraemos un codigo y una lista de argumentos
            # code, args = parse_command(line)
            args = line.decode().split()

            # TODO: si no se encuentra el comando return INVALID_COMMAND
            code, response = commands[args[0]](args)
            self.send(code, response.encode())
