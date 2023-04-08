#!/usr/bin/env python
# encoding: utf-8
# Revisión 2019 (a Python 3 y base64): Pablo Ventura
# Revisión 2014 Carlos Bederián
# Revisión 2011 Nicolás Wolovick
# Copyright 2008-2010 Natalia Bidart y Daniel Moisset
# $Id: server.py 656 2013-03-18 23:49:11Z bc $

import optparse
import socket
import sys
import connection
from constants import *
import os
import threading
import time


class Server(object):
    """
    El servidor, que crea y atiende el socket en la dirección y puerto
    especificados donde se reciben nuevas conexiones de clientes.
    """
 
    # (hasta ahora) cada instancia del objeto Server tendrá cuatro campos :
    # el socket, el puerto, la direccion y el directorio
    def __init__(self, addr=DEFAULT_ADDR, port=DEFAULT_PORT,
                 directory=DEFAULT_DIR):
        print("Serving %s on %s:%s." % (directory, addr, port))
        # FALTA: Crear socket del servidor, configurarlo, asignarlo
        # a una dirección y puerto, etc.
        try:
            self.listening_socket = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            self.listening_socket.bind((addr, port))
            if not os.path.exists(directory):
                os.makedirs(directory)
            self.directory = directory
            self.port = port
            self.addr = addr
        except:
            raise Exception("Error al crear el socket")

    def handle_new_connection(self, client_socket, client_address):
        """
        Maneja una nueva conexión entrante. Se crea un objeto Connection
        para manejar la comunicación con el cliente.
        """
        connect = connection.Connection(client_socket, self.directory)
        connect.handle()

    def serve(self):
        """
        Loop principal del servidor. Se acepta una conexión a la vez
        y se espera a que concluya antes de seguir.
        """

        # escucha conexiones entrantes
        self.listening_socket.listen(MAX_CONNECTIONS)

        active_threads = []
        while True:
            if len(active_threads) < MAX_CONNECTIONS:
                # Accept a new connection
                client_socket, client_address = self.listening_socket.accept()
                # Start a new thread to handle the connection
                thread = threading.Thread(
                    target=self.handle_new_connection, args=(client_socket, client_address))
                thread.start()

                # Add the thread to the list of active threads
                active_threads.append(thread)

            else:
                # Wait for a thread to finish before accepting a new connection
                for thread in active_threads:
                    if not thread.is_alive():
                        active_threads.remove(thread)
                        break
                time.sleep(0.1)


def main():
    """Parsea los argumentos y lanza el server"""

    parser = optparse.OptionParser()
    parser.add_option(
        "-p", "--port",
        help="Número de puerto TCP donde escuchar", default=DEFAULT_PORT)
    parser.add_option(
        "-a", "--address",
        help="Dirección donde escuchar", default=DEFAULT_ADDR)
    parser.add_option(
        "-d", "--datadir",
        help="Directorio compartido", default=DEFAULT_DIR)

    options, args = parser.parse_args()
    if len(args) > 0:
        parser.print_help()
        sys.exit(1)
    try:
        port = int(options.port)
    except ValueError:
        sys.stderr.write(
            "Numero de puerto invalido: %s\n" % repr(options.port))
        parser.print_help()
        sys.exit(1)

    server = Server(options.address, port, options.datadir)
    server.serve()


if __name__ == '__main__':
    main()
