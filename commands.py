from constants import *
import os
from base64 import b64encode

"""No recibe argumentos y busca obtener la lista de
archivos que están actualmente disponibles. El servidor responde
con una secuencia de líneas terminadas en \r\n, cada una con el
nombre de uno de los archivos disponible. Una línea sin texto
indica el fin de la lista. """


def get_file_listing(*args):
    code = CODE_OK
    # arguments are: CMD
    if len(args) != 1:
        code = INVALID_ARGUMENTS

    return (code, 'hola desde get_file_listing\n')


"""Recibe un argumento FILENAME especificando un
nombre de archivo del cual se pretende averiguar el tamaño . El2
servidor responde con una cadena indicando su valor en bytes."""


def get_metadata(*args):
    code = CODE_OK
    # arguments are: CMD, FILENAME
    if len(args) != 2:
        code = INVALID_ARGUMENTS
        metadata = b''
    else:   
            directory = args[0]
            file_name = args[1]

            file_path = directory + file_name

            metadata = str(os.path.getsize(file_path))+EOL
     
    return (code,metadata)


"""Recibe en el argumento FILENAME el nombre de
archivo del que se pretende obtener un slice o parte. La parte se
especifica con un OFFSET (byte de inicio) y un SIZE (tamaño de la
parte esperada, en bytes), ambos no negativos . El servidor3
responde con el fragmento de archivo pedido codificado en
base64 y un \r\n"""


def get_slice(*args):
    code = CODE_OK
    # arguments are: CMD, FILENAME, OFFSET, SIZE
    if len(args) != 4:
        code = INVALID_ARGUMENTS
        content_sliced_b64 = b''
        
    else:
        directory = args[0]
        filename = args[1]
        offset = args[2]
        size = args[3]

        file_path = directory+filename
        file_size = os.path.getsize(file_path)


        if not os.path.exists(file_path):
            code = FILE_NOT_FOUND
            content_sliced_b64 = b''

        elif offset > size or offset < 0 or size < 0 or offset+size > file_size:
            code = BAD_OFFSET
            content_sliced_b64 = b''
        else:
            # abro el archivo en modo lectura binaria, leo el contenido y lo codifico en base64
            with open(file_path, "rb") as file:
                content = file.read(BUFFER_SIZE)
                # if content == -1:
                    # code = FILE_EMPTY no se si esto es necesario
                file.close()
                content_sliced = content[offset:offset+size]

                # codifico el contenido en base64, lo paso a cadena de bytes y le agrego el \r\n
                slice= b64encode(content_sliced).encode("ascii") + EOL

    
    return (code,slice)


"""No recibe argumentos y busca terminar la
conexión. El servidor responde con un resultado exitoso (0 OK) y
luego cierra la conexión"""


def quit():
    code = CODE_OK
    return (code,)


commands = {
    "get_file_listing": get_file_listing,
    "get_metadata": get_metadata,
    "get_slice": get_slice,
    "quit": quit
}
