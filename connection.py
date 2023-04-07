# encoding: utf-8
# Revisión 2019 (a Python 3 y base64): Pablo Ventura
# Copyright 2014 Carlos Bederián
# $Id: connection.py 455 2011-05-01 00:32:09Z carlos $

import socket
from constants import *
from base64 import b64encode
import os


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

    def send_code_message(self, code):
        """
        Solamente envia el codigo y el mensaje correspondiente al cliente.
        """
        code_msg = get_code_message(code)
        code = str(code) + ' ' + code_msg
        if not code.endswith(EOL):
            code += EOL
        print("Sending code: ", code)
        self.socket.sendall(code.encode())

    def send(self, code, response):
        """"
        Envia un codigo y un mensaje al cliente.
        Ademas envia una respuesta al cliente.
        """
        # if response encoding is base64, get the code message and encode it together with the code
        if not response.startswith("base64"):
            self.send_code_message(code)
            if not response.endswith(EOL):
                response += EOL
            self.socket.sendall(response.encode())

        # if response encoding is base64, get the code message and encode it together with the code
        else:
            code_msg = get_code_message(code)
            code = str(code) + ' ' + code_msg
            if not code.endswith(EOL):
                code += EOL
            code = b64encode(code.encode())

            if not response.endswith(EOL):
                response += EOL

            self.socket.sendall(code)
            self.socket.sendall(response)

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

        print("Sending:", response)
        self.send(CODE_OK, response)

    def get_metadata(self, filename):
        """
        Este comando recibe un argumento FILENAME especificando un
        nombre de archivo del cual se pretende averiguar el tamaño. El
        servidor responde con una cadena indicando su valor en bytes
        """
        # chequeamos si el archivo existe
        if not os.path.isfile(os.path.join(self.directory, filename)):
            self.send_code_message(FILE_NOT_FOUND)

        # obtenemos el tamaño del archivo
        file_size = os.path.getsize(os.path.join(self.directory, filename))
        response = str(file_size)
        print("Sending:", response)
        self.send(CODE_OK, response)

    def get_slice(self, filename, offset, length):
        """
        Este comando recibe en el argumento FILENAME el nombre de
        archivo del que se pretende obtener un slice o parte. La parte se
        especifica con un OFFSET(byte de inicio) y un SIZE(tamaño de la
        parte esperada, en bytes), ambos no negativos . El servidor responde
        con el fragmento de archivo pedido codificado en base64 y un \r\n.
        """
        # chequeamos si el archivo existe
        if not os.path.isfile(os.path.join(self.directory, filename)):
            self.send_code_message(FILE_NOT_FOUND)

        # chequeamos que el offset y el length sean no negativos
        if int(offset) < 0:
            self.send_code_message(INVALID_ARGUMENTS)

        if int(length) < 0:
            self.send_code_message(INVALID_ARGUMENTS)

        # verificamos que el offset y el length no sean mayores al tamaño del archivo
        file_size = os.path.getsize(os.path.join(self.directory, filename))
        if int(offset) + int(length) > file_size:
            self.send_code_message(BAD_OFFSET)

        # obtenemos el slice del archivo
        with open(os.path.join(self.directory, filename), "rb") as file:
            file.seek(int(offset))
            slice = file.read(int(length))

        # codificamos el slice en base64
        encoded_slice = b64encode(slice).decode("ascii")
        print("Sending:", encoded_slice)
        self.send(CODE_OK, encoded_slice)

    def quit(self):
        """
        Este comando no recibe argumentos y busca terminar la
        conexión. El servidor responde con un resultado exitoso(0 OK) y
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
                # Ejecutamos el comando con los argumentos si es que los tiene
                commands[args[0]](self, *args[1:])

            # Si el codigo no es OK, enviamos el mensaje de error ya que los codigos
            # empezados por 2 no terminan la conexion
            else:
                self.send_code_message(code)

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
    return str(error_messages[code])
