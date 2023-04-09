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

        # quitando la condicion del largo del buffer se puede recibir filenames largos para procesarlos
        while not EOL in buffer:
            buffer += self.socket.recv(BUFFER_SIZE).decode("ascii")

        if EOL in buffer:
            line, buffer = buffer.split(EOL, 1)
            line = line.strip()
            return line, buffer
        else:
            return "", buffer

    def send_code_message(self, code):
        """
        Solamente envia el codigo y el mensaje correspondiente al cliente.
        """
        code_msg = get_code_message(code)
        code = str(code) + ' ' + code_msg + EOL
        self.socket.sendall(code.encode())

    def send(self, code, response):
        """"
        Envia un codigo y un mensaje al cliente.
        Ademas envia una respuesta al cliente.
        """
        # if response encoding is base64, get the code message and encode it together with the code
        if not response.startswith("base64"):
            self.send_code_message(code)
            response += EOL
            self.socket.sendall(response.encode())

        # if response encoding is base64, get the code message and encode it together with the code
        else:
            code_msg = get_code_message(code)
            code = str(code) + ' ' + code_msg + EOL
            code = b64encode(code.encode())
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

        print("Request:", line)

        # chequeamos que el comando exista en las keys del diccionario
        if args[0] not in commands:
            code = INVALID_COMMAND
            args = []

        # chequeamos que la cantidad de argumentos sea correcta
        else:
            if args[0] == list(commands.keys())[0] or args[0] == list(commands.keys())[3]:
                # ni get_file_listing ni quit reciben argumentos
                if len(args) != 1:
                    code = INVALID_ARGUMENTS
                    args = []

            elif args[0] == list(commands.keys())[1]:
                # get_metadata recibe un argumento
                if len(args) != 2:
                    code = INVALID_ARGUMENTS
                    args = []

            elif args[0] == list(commands.keys())[2]:

                # si el argumento filename no es un string o el offset o size no son enteros
                # o si recibimos una cantidad de argumentos distinta a 4
                if len(args) != 4:
                    code = INVALID_ARGUMENTS
                    args = []

                elif not (isinstance(args[1], str) and args[2].isdigit() and args[3].isdigit()):
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

        self.send(CODE_OK, response)

    def is_valid_filename(self, filename):
        """
        Chequea que el nombre del archivo sea valido.
        """
        is_valid = True
        # verificamos que el nombre del archivo no sea muy largo, que sea un string y que no sea vacio
        if len(filename) > MAX_FILENAME or not isinstance(filename, str) or len(filename) == 0:
            is_valid = False

        # verificamos que no haya caracteres prohibidos
        elif not all(c.isalnum() or c in '-._' for c in filename):
            is_valid = False

        return is_valid

    def get_metadata(self, filename):
        """
        Este comando recibe un argumento FILENAME especificando un
        nombre de archivo del cual se pretende averiguar el tamaño. El
        servidor responde con una cadena indicando su valor en bytes
        """

        # chequeamos si el archivo existe
        if not os.path.isfile(os.path.join(self.directory, filename)):
            self.send_code_message(FILE_NOT_FOUND)

        # validamos el filename
        elif not self.is_valid_filename(filename):
            self.send_code_message(INVALID_ARGUMENTS)

        # si llegamos hasta aca, el archivo existe y el filename  es valido
        else:
            response = ""
            # obtenemos el tamaño del archivo
            file_size = os.path.getsize(os.path.join(self.directory, filename))
            response = str(file_size)
            self.send(CODE_OK, response)

    def get_slice(self, filename, offset, size):
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

        # validamos el filename
        elif not self.is_valid_filename(filename):
            self.send_code_message(INVALID_ARGUMENTS)

        # si llegamos hasta aca, el archivo existe y el filename  es valido
        else:
            # verificamos que el offset y el length no sean mayores al tamaño del archivo
            # y que el offset no sea negativo
            file_size = os.path.getsize(os.path.join(self.directory, filename))
            if offset + size > file_size or offset < 0:
                self.send_code_message(BAD_OFFSET)

            # obtenemos el slice del archivo
            with open(os.path.join(self.directory, filename), "rb") as file:
                file.seek(offset)
                slice = file.read(size)

            # codificamos el slice en base64
            encoded_slice = b64encode(slice).decode("ascii")
            self.send(CODE_OK, encoded_slice)

    def quit(self):
        """
        Este comando no recibe argumentos y busca terminar la
        conexión. El servidor responde con un resultado exitoso(0 OK) y
        luego cierra la conexión.
        """
        self.send_code_message(CODE_OK)
        print("Closing connection...")
        self.is_connected = False

    def handle(self):
        """
        Atiende eventos de la conexión hasta que termina.
        """
        buffer = ""
        while self.is_connected:
            # En line: una linea que termina con EOL, en buffer: resto del byte stream
            line, buffer = self.read_line(buffer)

            # chequeamos que no haya un '\n' en la linea, si lo hay, generar un BAD_EOL
            if '\n' in line:
                self.send_code_message(BAD_EOL)
                self.is_connected = False
                print("Closing connection...")

            else:

                # Envolvemos en un try/except para terminar el proceso del cliente si hay un error
                try:
                    # Parseamos la linea, obtenemos el codigo y los argumentos
                    code, args = self.parse_command(line)

                    # Si el codigo es OK, ejecutamos el comando
                    if code == CODE_OK:
                        # Ejecutamos el comando con los argumentos si es que los tiene
                        # si el comando es get_slice, casteamos los argumentos a int
                        if args[0] == "get_slice":
                            commands[args[0]](
                                self, args[1], int(args[2]), int(args[3]))
                        else:
                            commands[args[0]](self, *args[1:])

                    # Si el codigo no es OK, enviamos el mensaje de error ya que los codigos
                    # empezados por 2 no terminan la conexion
                    else:
                        self.send_code_message(code)

                except Exception:
                    self.send_code_message(INTERNAL_ERROR)
                    self.is_connected = False
                    print("Closing connection...")

        # salimos porque se seteo is_connected a False
        self.socket.close()


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
