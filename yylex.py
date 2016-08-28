###< 2016-08-28 18:12:00.904393 >###

#
#  yylex.py
#    analizador lexico para el lenguaje bcc
#

import sys, shlex, pickle
import dataTree as dt

#
# analizador lexico
#
def yylex(filename, quiet=False):

    # estructura de datos.
    #   crea un arbol para almacenar la informacion
    #   generada por las distintas componentes
    #   del interprete
    DATA = dt.TreeNode('DATA', {'filename': filename})
    SOURCECODE  = dt.SubNode(DATA, 'SOURCECODE')
    TOKENTABLE  = dt.SubNode(DATA, 'TOKENTABLE')
    SYNTAXTREE  = dt.SubNode(DATA, 'SYNTAXTREE')
    SYMBOLTABLE = dt.SubNode(DATA, 'SYMBOLTABLE')

    # preparacion del codigo fuente.
    #   sourceCode es un vector donde cada elemento
    #   es una linea del codigo fuente incluyendo
    #   comentarios. Despues almacena el codigo
    #   en la estructura de datos
    sourceCode = open(filename, 'r').readlines()
    for i, line in enumerate(sourceCode):
        lineno = i
        x = dt.SubNode(SOURCECODE, lineno)
        if line[-1] == '\n':
            line = line[:-1]
        x.text = line

    #
    # yyputtoken.
    #   esta es uan funcion auxiliar que agrega cada token y su
    #   correspondiente lexema a la tabla de tokens de forma
    #   secuencial.
    #   yyputtoken crea un nuevo nodo a la tabla se simbolos
    #
    def yyputtoken(token, lexeme, lineno):
        #
        dt.SubNode(TOKENTABLE, token, dict(lexeme=lexeme, lineno=lineno))
        #


    # analizador lexico.
    #   esta es la rutina de analisis lexico como tal.
    #   se procesa una linea a la vez, para todas las
    #   lineas del codigo fuente
    lineno = -1
    for line in sourceCode:

        # shlex.
        #   es una utilidad de python que permite descomponer
        #   una cadena de texto en sus lexemas componentes. shlex
        #   descarta automaticamente las lineas de comentarios.
        #
        # lexemes.
        #   es una lista de strings, donde cada string es un lexema
        lexemes = list(shlex.shlex(line))

        n = 0
        lineno += 1
        while n < len(lexemes):
            # lex1:  es el lexema actual
            # lex2:  es el lexema actual concatenado con el
            #        siguiente. se requiere para poder reconocer
            #        algunas secuencias como '>=' que shlex
            #        separa en '>' y '='
            lex1 = lexemes[n]
            lex2 = lexemes[n] + lexemes[n+1] if n+1 < len(lexemes) else None

            #  en este punto se inicia el reconocimiento de cada
            #  uno de los lexemas que conforman el codigo fuente
            if lex1[0] == "'" or lex1[0] == '"':
                #
                yyputtoken('STR', lex1, lineno)
                #
            elif lex1 in 'function var end write when do if else while return'.split():
                #
                yyputtoken(lex1.upper(), lex1, lineno)
                #


            elif lex2 in ':= =='.split():
                yyputtoken(lex2, lex2, lineno)
                n += 1


            elif lex1 in ': , ; ( ) { } < + *'.split():
                yyputtoken(lex1, lex1, lineno)


            elif lex1 in 'true false'.split():
                yyputtoken('BOOL', lex1, lineno)

            elif lex1 in 'bool num'.split():
                yyputtoken('DATATYPE', lex1, lineno)

            elif lex1 == '@':
                yyputtoken('UFID', lex2, lineno)
                n += 1

            elif lex1 == '$':
                yyputtoken('BFID', lex2, lineno)
                n += 1

            elif (lex1 == '.' and
                  n+1 < len(lexemes) and
                  lexemes[n+1].isdigit()):
                lex1 = '.' + lexemes[n+1]
                yyputtoken('NUM', lex1, lineno)
                n += 1

            elif lex1.isdigit():
                if n+1 < len(lexemes) and lexemes[n+1] == '.':
                    lex1 += '.'
                    n += 1
                    if n+1 < len(lexemes) and lexemes[n+1].isdigit():
                        lex1 += lexemes[n+1]
                        n += 1
                yyputtoken('NUM', lex1, lineno)

            elif lex1.isalnum():
                yyputtoken('ID', lex1, lineno)

            else:
                msg = '{}:Lexical error at line <{}>: '.format(filename, lineno)
                msg += 'Unexpected symbol <{}>'.format(lex1)
                # msg += '--> ' + sourceCode[lineno]
                print(msg)
                sys.exit()

            n += 1

    yyputtoken('END', 'end', len(lexemes))

    # en este punto se han reconocido todos los
    # lexemas y se procede a almacenar el resultado
    # en un archivo en disco
    with open(filename + '.dataTree', 'wb') as f:
        pickle.dump(DATA, f)

    if quiet == False:
        #
        dt.printTree(TOKENTABLE)
        #


if __name__ == '__main__':


    if len(sys.argv) > 1:
        for filename in sys.argv[1:]:
            yylex(filename)
    else:
        filename = input()
        yylex(filename)
