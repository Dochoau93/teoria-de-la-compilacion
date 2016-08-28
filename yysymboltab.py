###< 2016-08-28 18:12:00.907115 >###

#
#  yysimboltab.py
#    generador de la tabla de simbolos
#

import shlex, sys, pickle
import dataTree as dt


# generacion de la tabla de simbolos
def yysymboltab(filename, quiet = False):

    # lee la estructura de datos
    with open(filename + '.dataTree', 'rb') as f:
        DATA = pickle.load(f)

    SOURCECODE  = DATA.find('SOURCECODE')
    TOKENTABLE  = DATA.find('TOKENTABLE')
    SYNTAXTREE  = DATA.find('SYNTAXTREE')
    SYMBOLTABLE = DATA.find('SYMBOLTABLE')

    def yyerror(node, msg):
        # el simbolo ya existe en la tabla de simbolos
        lineno = node.attrib['lineno']
        symbol = node.attrib['value']
        txt = '{}:Semantic error at line {}: '.format(filename, lineno)
        txt += 'Symbol <{}> {}'.format(symbol, msg)
        # msg += '--> ' + SOURCECODE[yylineno].text
        print(txt)
        sys.exit()

    def find_symbol(symbol, scope=None):
        if scope is None:
            # se esta buscando una funcion
            return SYMBOLTABLE.find(symbol)
        return SYMBOLTABLE.search(symbol, 'scope', scope)



    # install_symbol.
    #    instala un nuevo simbolo en la tabla.
    def install_symbol(symbol, kind, nargs=None, datatype=None, scope=None,
                       argstype=None):
        attrib = {'kind': kind}
        if not nargs is None:
            attrib['nargs'] = nargs
        if not datatype is None:
            attrib['datatype'] = datatype
        if not scope is None:
            attrib['scope'] = scope
        if not argstype is None:
            attrib['argstype'] = argstype
        SYMBOLTABLE.append(dt.TreeNode(tag=symbol, attrib=attrib))

    def symbol_table(node):

        if node.tag == 'FUNCTION':

            # varifica que la funcion
            # no exista en la tabla de simbolos
            if not find_symbol(node.get('value')) is None:
                yyerror(node, 'already defined')

            # cuenta el numero de argumentos
            nargs = len(node._children[0])

            # inserta la función en la tabla de simbolos
            install_symbol( symbol   = node.get('value'),
                            kind     = 'ufun',
                            scope    = node.get('scope'),
                            nargs    = nargs,
                            datatype = node.get('datatype'))

            argstype = []
            for arg in node[0]:
                argstype.append(arg.get('datatype'))
            symbol = find_symbol(node.attrib['value'])
            symbol.set('argstype', argstype)

            # inserta la variable de retorno
            install_symbol( symbol   = '__return__',
                            kind     = 'uvar',
                            scope    = node.get('scope'),
                            datatype = node.get('datatype'))


        # tipos de nodos que instalan variables
        if node.tag == 'ARGS':
            for arg in node:
                r = find_symbol(arg.get('value'), arg.get('scope'))
                if not r is None:
                    yyerror(arg, 'already defined')
                install_symbol( symbol   = arg.get('value'),
                                kind     = 'uvar',
                                scope    = arg.get('scope'),
                                datatype = arg.get('datatype'))

        if node.tag == 'VAR':
            for arg in node:
                r = find_symbol(arg.get('value'), arg.get('scope'))
                if not r is None:
                    yyerror(arg, 'already defined')
                install_symbol( symbol   = arg.get('value'),
                                kind     = 'uvar',
                                scope    = arg.get('scope'),
                                datatype = arg.get('datatype'))




        if node.tag in ('BFCALL',
                        'UFCALL'):

            f = find_symbol(node.get('value'))
            if f is None:
                yyerror(node, 'not defined')

            node.set('datatype', f.get('datatype'))

            nargs = len(node)
            if nargs != f.get('nargs'):
                msg = '{}:Semantic error at line {}: '.format(filename, node.get('lineno'))
                msg += 'Invalid number of arguments for function <{}>'.format(node.get('value'))
                # msg += '--> ' + SOURCECODE[node.get('lineno')].text
                print(msg)
                sys.exit()


        for b in node:
            symbol_table(b)

    # rutina principal.
    #   instalacion de funciones internas
    #   soportadas por la maquina virtual

    install_symbol( symbol   = '$chs',
                    kind     = 'bfun',
                    nargs    = 1,
                    datatype = 'num',
                    argstype = ['num'])

    install_symbol( symbol   = '$abs',
                    kind     = 'bfun',
                    nargs    = 1,
                    datatype = 'num',
                    argstype = ['num'])

    install_symbol( symbol   = '$sgn',
                    kind     = 'bfun',
                    nargs    = 1,
                    datatype = 'num',
                    argstype = ['num'])


    symbol_table(SYNTAXTREE)



    #
    # el campo entrylabel es usando para asignar el punto (label)
    #   de entrada para las funciones de usuario
    #
    # el campo location es usado para enumerar las posiciones
    #   de memoria en el registro DS que ocupan las variables
    #   de usuario
    #

    m = 0  # contador de funciones de usuario
    n = 0  # contador de variables de usuario

    for symbol in SYMBOLTABLE:

        if symbol.get('kind') == 'ufun':
            symbol.set('entrylabel', m)
            m += 1

        if symbol.get('kind') == 'uvar':
            symbol.set('location', n)
            n += 1


    #   en este punto se ha construido la tabla de simbolos
    #   y se procede a almacenar el resultado en un archivo
    #   en disco
    with open(filename + '.dataTree', 'wb') as f:
        pickle.dump(DATA, f)

    if quiet == False:
        dt.printTree(SYMBOLTABLE)


if __name__ == '__main__':


    if len(sys.argv) > 1:
        for filename in sys.argv[1:]:
            yysymboltab(filename)
    else:
        filename = input()
        yysymboltab(filename)
