###< 2016-08-28 18:12:00.908258 >###

#
#  yytypecheck.py
#    verificador de tipos
#

import shlex, sys, pickle
import dataTree as dt



def yytypecheck(filename, quiet=False):

    # lee la estructura de datos
    with open(filename + '.dataTree', 'rb') as f:
        DATA = pickle.load(f)

    SOURCECODE  = DATA.find('SOURCECODE')
    TOKENTABLE  = DATA.find('TOKENTABLE')
    SYNTAXTREE  = DATA.find('SYNTAXTREE')
    SYMBOLTABLE = DATA.find('SYMBOLTABLE')


    def yyerror(node):
        msg = '{}:Type error at line {}: '.format(filename, node.get('lineno'))
        msg += 'Invalid type <{}> found'.format(node.get('datatype'))
        print(msg)
        sys.exit()

    def find_symbol(symbol, scope=None):
        if scope is None:
            # se esta buscando una funcion
            return SYMBOLTABLE.find(symbol)
        return SYMBOLTABLE.search(symbol, 'scope', scope)


    def typecheck(node):

        # verifica los nodos hijos primero
        for n in node:
            typecheck(n)

        if node.tag is ('WHEN',
                        'IF',
                        'WHILE'):

            if node[0].get('datatype') != 'bool':
                yyerror(n[0])



        if node.tag == 'ASSIGN':
            n = find_symbol(node.get('value'), node.get('scope'))
            if n.get('datatype') != node[0].get('datatype'):
                yyerror(node)


        if node.tag == 'ID':
            n = find_symbol(node.get('value'), node.get('scope'))
            node.set('datatype', n.get('datatype'))


        if node.tag in ('<',
                        '<='):

            if node[0].get('datatype') != 'num':
                yyerror(node[0])
            if node[1].get('datatype') != 'num':
                yyerror(node[1])


        if node.tag == 'RETURN':
            if node[0].get('datatype') != node.get('datatype'):
                yyerror(node[0])


        if node.tag == 'BFID':
            # obtiene la funcion de la tabla de simbolos
            symbol = find_symbol(node.get('value'))

            # verifica la cantidad de argumentos de la funcion
            nargs = symbol.get('nargs')
            nparams = len(node[0])

            if nargs != nparams:
                msg = '{}:Type error at line {}:\n'.format(filename, node.get('lineno'))
                msg += 'Invalid number of arguments in function call'
                # msg += '--> ' + SOURCECODE[node.get('lineno')].text
                print(msg)
                sys.exit()


            for a, b in zip(m, node):
                if a.get('datatype') != b.get('datatype'):
                    msg = '{}:Type error at line {}:\n'.format(filename, node.get('lineno'))
                    msg += 'Invalid type of arguments in function call'
                    # msg += '--> ' + SOURCECODE[node.get('lineno')].text
                    print(msg)
                    sys.exit()


        if node.tag in ('BFCALL', 'UFCALL'):
            # obtiene la funcion de la tabla de simbolos
            symbol = find_symbol(node.get('value'))

            # verifica la cantidad de argumentos de la funcion
            nargs = symbol.get('nargs')
            if nargs != len(node):
                msg = '{}:Type error at line {}: '.format(filename, node.get('lineno'))
                msg += 'Invalid number of arguments in function call'
                # msg += '--> ' + SOURCECODE[node.get('lineno')].text
                print(msg)
                sys.exit()

            for a, b in zip(symbol.get('argstype'), node):
                if a != b.get('datatype'):
                    msg = '{}:Type error at line {}: '.format(filename, node.get('lineno'))
                    msg += 'Invalid type of arguments in function call'
                    # msg += '--> ' + SOURCECODE[node.get('lineno')].text
                    print(msg)
                    sys.exit()


    typecheck(SYNTAXTREE)

    #   el proceso se ejecuto correctamente y se
    #   procede a almacenar el resultado en un archivo
    #   en disco
    with open(filename + '.dataTree', 'wb') as f:
        pickle.dump(DATA, f)

    if quiet == False:
        dt.printTree(SYNTAXTREE)




if __name__ == '__main__':


    if len(sys.argv) > 1:
        for filename in sys.argv[1:]:
            yytypecheck(filename)
    else:
        filename = input()
        yytypecheck(filename)
