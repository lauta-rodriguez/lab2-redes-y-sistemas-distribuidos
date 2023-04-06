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
        self.socket = socket
        self.directory = directory
        self.is_connected = True
        # Print the client's address and port like this: Connected by: ('127.0.0.1', 44639)
        print(
            f"Connected by: ('{socket.getpeername()[0]}', {socket.getpeername()[1]})")

    def read_line(self, buffer):
        """
        Lee una línea del socket, y se queda con el segmento del buffer hasta EOL.
        """

        while (not EOL in buffer) or (len(buffer) > MAX_BUFFER):
            buffer += self.socket.recv(BUFFER_SIZE).decode("ascii")

        if len(buffer) > MAX_BUFFER:
            return None, buffer

        line, buffer = buffer.split(EOL, 1)
        return line, buffer

    def send(self, code, response):
        # encode the code message to base64 and send it,
        # first convert it to string, add the EOL and encode it b64
        # if it has no EOL at the end, append it

        if not code.endswith(EOL):
            code += EOL
        self.socket.sendall(code.encode())

        # encode the response and send it
        if not response.endswith(EOL):
            response += EOL
        self.socket.sendall(response.encode())

    def parse_command(self, line):
        """
        Parsea la linea (string) y devuelve un codigo y una lista de argumentos en donde 
        el primer elemento es el comando y el resto son los argumentos.
        """
        code = CODE_OK
        args = line.split(" ")

        # chequeamos que el comando exista en las keys del diccionario
        if args[0] not in commands:
            code = INVALID_COMMAND
            args = []

        # chequeamos que la cantidad de argumentos sea correcta
        else:
            # check if the command has the correct number of arguments (except for the command itself)
            if args[0] == list(commands.keys())[0]:
                # get_file_listing no recibe argumentos
                if len(args) != 1:
                    print("Invalid number of arguments for command: ", args[0])
                    code = INVALID_ARGUMENTS
                    args = []

            elif args[0] == list(commands.keys())[1]:
                # get_metadata recibe un argumento
                if len(args) != 2:
                    code = INVALID_ARGUMENTS
                    args = []

            elif args[0] == list(commands.keys())[2]:
                # get_slice recibe 3 argumentos
                if len(args) != 4:
                    code = INVALID_ARGUMENTS
                    args = []

        # si llegamos hasta aca, el comando es valido
        # y la cantidad de argumentos tambien
        return code, args

    def get_file_listing(self):
        """
        Este comando no recibe argumentos y busca obtener la lista de
        archivos que están actualmente disponibles. El servidor responde
        con una secuencia de líneas terminadas en \r\n, cada una con el
        nombre de uno de los archivos disponible. Una línea sin texto
        indica el fin de la lista.
        """
        response = ""
        for file in os.listdir(self.directory):
            response += file + EOL

        # if the response is empty, send the empty message
        if response == "":
            response = "Empty directory"

        print("Sending:", response)
        self.send(get_code_message(CODE_OK), response)

    def get_metadata(self, filename):
        """
        Este comando recibe un argumento FILENAME especificando un
        nombre de archivo del cual se pretende averiguar el tamaño. El
        servidor responde con una cadena indicando su valor en bytes
        """
        pass

    def get_slice(self, filename, offset, length):
        """
        Este comando recibe en el argumento FILENAME el nombre de
        archivo del que se pretende obtener un slice o parte. La parte se
        especifica con un OFFSET (byte de inicio) y un SIZE (tamaño de la
        parte esperada, en bytes), ambos no negativos . El servidor responde 
        con el fragmento de archivo pedido codificado en base64 y un \r\n.
        """
        pass

    def quit(self):
        """
        Este comando no recibe argumentos y busca terminar la
        conexión. El servidor responde con un resultado exitoso (0 OK) y
        luego cierra la conexión.
        """
        pass

    def handle(self):
        """
        Atiende eventos de la conexión hasta que termina.
        """
        buffer = ""
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

            # Parseamos la linea, obtenemos el codigo y los argumentos
            code, args = self.parse_command(line)

            # Si el codigo es OK, ejecutamos el comando
            if code == CODE_OK:
                # Ejecutamos el comando con los argumentos si es que los tiene
                print("Executing command: ", args[0], " with args: ", args[1:])
                commands[args[0]](self)

            if buffer == "":
                # No hay mas datos en el buffer, cerramos la conexión
                print("Buffer is empty, closing connection...")
                self.socket.close()
                self.is_connected = False


# Diccionario de comandos
commands = {
    "get_file_listing": Connection.get_file_listing,
    "get_metadata": Connection.get_metadata,
    "get_slice": Connection.get_slice,
    "quit": Connection.quit
}


def get_code_message(code):
    """
    Devuelve el mensaje asociado al codigo de respuesta.
    """
    msg = str(code) + " " + error_messages[code]
    return msg
