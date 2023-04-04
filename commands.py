"""No recibe argumentos y busca obtener la lista de
archivos que están actualmente disponibles. El servidor responde
con una secuencia de líneas terminadas en \r\n, cada una con el
nombre de uno de los archivos disponible. Una línea sin texto
indica el fin de la lista. """
def get_file_listing():
    pass

"""Recibe un argumento FILENAME especificando un
nombre de archivo del cual se pretende averiguar el tamaño . El2
servidor responde con una cadena indicando su valor en bytes."""

def get_metadata(FILENAME):
    pass

"""Recibe en el argumento FILENAME el nombre de
archivo del que se pretende obtener un slice o parte. La parte se
especifica con un OFFSET (byte de inicio) y un SIZE (tamaño de la
parte esperada, en bytes), ambos no negativos . El servidor3
responde con el fragmento de archivo pedido codificado en
base64 y un \r\n"""
def get_slice(FILENAME, OFFSET, SIZE):
    pass

"""No recibe argumentos y busca terminar la
conexión. El servidor responde con un resultado exitoso (0 OK) y
luego cierra la conexión"""
def quit():
    pass

commands = {
    "get_file_listing": get_file_listing,
    "get_metadata": get_metadata,
    "get_slice": get_slice,
    "quit": quit
}