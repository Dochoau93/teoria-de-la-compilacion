###< 2016-08-28 18:12:00.914305 >###

##
##  grep.py (grep en python)
##
##    implementacion de grep (basico) en python
##    (Adaptacion del codigo de Kernighan y Pike
##    publicado en Dr Dobbs).
##


## librería para leer los argumentos de la línea de comandos
import sys


## la búsqueda se realiza sobre la línea actual de texto
def match_here(re, text):
    '''
    Busca la cadena re al principio de la cadena text
    por eliminación de los caracteres iguales en re y text

    Ejemplo 1:
       matchhere( ‘mundo’, ‘mundo feliz’)  # llamada recursiva en el último if
       matchhere( ‘undo’, ‘undo feliz’)
       matchhere( ‘ndo’, ‘ndo feliz’)
       matchhere( ‘do’, ‘do feliz’)
       matchhere( ‘o’, ‘o feliz’)
       matchhere( ‘’, ‘ feliz’)  ← True  por el primer if

    Ejemplo 2:
       matchhere( ‘mundo$’, ‘mundo’)  # llamada recursiva en el último if
       matchhere( ‘undo$’, ‘undo’)
       matchhere( ‘ndo$’, ‘ndo’)
       matchhere( ‘do$’, ‘do’)
       matchhere( ‘o$’, ‘o’)
       matchhere( ‘$’, ‘’)  ← True  por el tercer if
    '''

    if len(re) == 0:
        return True

    if len(re) > 1 and re[1] == '*':
        return match_star(re[0], re[2:], text)


    if re[0] == '$' and len(re)==1:
        return len(text) == 0

    if len(text)>0 and (re[0]=='.' or re[0] == text[0]):
        return match_here(re[1:], text[1:])

    return False


#
#    busca c*re al principio del texto
#
def match_star(c, re, text):
    '''
    busca c*re al principio del texto

    Ejemplo:
       grep(‘a*bb’, ‘aabbb’)
       matchstar( ‘a’, ‘bb’, ‘aabbb’)
       matchhere( ‘bb’, ‘aabbb’) ← False
       matchhere( ‘bb’, ‘abbb’)  ← False
       matchhere( ‘bb’, ‘bbb’)   ← True
    '''

    while len(text) > 0 and (text[0] == c or c == '.'):
        if match_here(re, text):
            return True
        text = text[1:]
    return match(re, text)






#
#    esta es la funcion de busqueda.
#    busca la ocurrencia de la expresion regular en 'text'
#
def match(re, text):
    '''
    Esta es la funcion de busqueda.
    Busca la ocurrencia de la expresion regular re en text

    Ejemplo:
       match( ‘mundo’, ‘hola mundo feliz’)
       match( ‘mundo’, ‘ola mundo feliz’)
       match( ‘mundo’, ‘la mundo feliz’)
       match( ‘mundo’, ‘a mundo feliz’)
       match( ‘mundo’, ‘ mundo feliz’)
       match( ‘mundo’, ‘mundo feliz’)  ← True

    '''
    if len(re) == 0:
        #
        return True
        #

    if re[0] == '^':
        #
        return match_here(re[1:], text)
        #

    while len(text) > 0:

        if match_here(re, text):
            return True
        text = text[1:]

    return False

def do_search(re, filename, print_header):
    '''
    llama la funcion de busqueda (match) para
    cada una de las lineas del archivo analizado
    '''
    ## abre el archivo y lo lee completamente
    lines = open(filename, 'r').readlines()

    ## lines es una lista de strings donde el último
    ## caracter es un retorno de carro
    for text in lines:

        ## elimina el retorno de carro al final de string
        if text[-1] == '\n':
            text = text[:-1]

        ## llama a match para buscar re en text
        if match(re, text):
            if print_header:
                #
                print(filename+":", end='')
                #
            print(text)


assert match('011', '001 1001 001') == False
assert match('001', '001 1001 001') == True
assert match('00$', '001 1001 001') == False
assert match('01$', '001 1001 001') == True
assert match('^10', '001 1001 001') == False
assert match('^00', '001 1001 001') == True
assert match('a01*', '00a 100a 00a') == False
assert match('000*', '111 00a1 0a1') == True
assert match('ab*c', 'ac') == True
assert match('ab*c', 'abc') == True
assert match('ab*c', 'abbc') == True
assert match('a.c', 'a0c') == True
assert match('^0.1$', '000') == False
assert match('^0.1$', '001') == True



##
##  programa principal
##
##    realiza la busqueda para cada uno de los archivos
##    pasados en la CML
##
if __name__ == '__main__' and len(sys.argv) >= 3:

    print_header = True if len(sys.argv) > 3 else False
    
    re = sys.argv[1]

    for filename in sys.argv[2:]:
        #
        do_search(re, filename, print_header)
        #
