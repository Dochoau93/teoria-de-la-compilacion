###< 2016-08-28 18:12:00.910709 >###

import sys, pickle
import dataTree as dt




def yysbm(filename):

    # lee la estructura de datos
    f = open(filename + '.dataTree', 'rb')
    DATA = pickle.load(f)
    f.close()
    SOURCECODE  = DATA.find('SOURCECODE')
    TOKENTABLE  = DATA.find('TOKENTABLE')
    SYNTAXTREE  = DATA.find('SYNTAXTREE')
    SYMBOLTABLE = DATA.find('SYMBOLTABLE')

    LP = []  # Literal Pool
    CS = []  # Code Segment

    def instr(code, r=None):
        if code == 'LBL':
            txt = 'LBL {}'.format(r)
        else:
            if type(code) is int:
                code = str(code)
            txt =  '          {0:5}'.format(code)
            if not r is None:
                txt += ' {:3}'.format(r)
        CS.append(txt)


    def find_symbol(symbol, scope=None):
        if scope is None:
            # se esta buscando una funcion
            return SYMBOLTABLE.find(symbol)
        return SYMBOLTABLE.search(symbol, 'scope', scope)


    # registro para manejo de labels
    # generados automaticamente
    num_labels = [256]
    stack_next = []
    stack_break = []

    def new_label():
        num_labels[0] = num_labels[0] - 1
        return num_labels[0]

    def new_next_label():
        x = new_label()
        stack_next.append(x)
        return x

    def new_break_label():
        x = new_label()
        stack_break.append(x)
        return x


    # esta rutina recorre los nodos del arbol de forma recursiva
    # para generar el codigo maquina de tres direcciones
    def code_generation(node):

        if node.tag in '< <= + *'.split():
            code_generation(node[0])
            code_generation(node[1])
            instr(node.tag)
            return


        if node.tag in ('BLOCK',
                        'FUNCTIONDECL',
                        'MAINPROG',
                        'SYNTAXTREE'):
            for n in node:
                code_generation(n)
            return

        if node.tag == 'CHS':
            code_generation(node[0])
            instr('CHS')
            return


        if node.tag == 'ASSIGN':
            symbol = find_symbol(node.get('value'), node.get('scope'))
            code_generation(node[0])
            instr('STO', symbol.get('location'))
            return



        if node.tag == 'BFCALL':

            # genera los argumentos
            code_generation(node[0])

            # obtiene la cantidad de argumentos de la funcion
            symbol = find_symbol(node.get('value'))
            nargs = symbol.get('nargs')

            if nargs == 1:
                if symbol.tag == '$chs':  m = 'CHS'
                if symbol.tag == '$abs':  m = 'FABS'
                if symbol.tag == '$sgn':  m = 'SGN'
                instr(m)
            else:
                pass

            return

        if node.tag == 'UFCALL':

            # pasa los argumentos por valor
            function_symbol = find_symbol(node.get('value'))
            nargs = function_symbol.get('nargs')
            return_symbol = find_symbol('__return__', function_symbol.get('scope'))
            location = return_symbol.get('location')

            # genera los argumentos y los pasa
            for arg in node:
                code_generation(arg)

            if nargs > 0:
                for k in range(nargs, 0, -1):
                    instr('STO', location + k)

            instr('GSB', function_symbol.get('entrylabel'))
            instr('RCL', location)
            return

        if node.tag == 'BOOL':
            value = 1 if node.get('value') else 0
            instr(value)
            return


        if node.tag == 'END':
            instr('HLT')
            return


        if node.tag == 'FUNCTION':
            #
            # genera un salto al final de la funcion
            L1 = new_label()
            instr('GTO', L1)
            #
            # genera el punto de entrada
            symbol = find_symbol(node.get('value'), node.get('scope'))
            instr('LBL', symbol.get('entrylabel'))
            #
            # genera el codigo del cuerpo de la funcion
            if node[1].tag == 'VAR':
                code_generation(node[2])
            else:
                code_generation(node[1])
            #
            # retorno obligatorio al final
            instr('RET')
            #
            # final de la funcion
            instr('LBL', L1)
            return

        if node.tag == 'ID':
            symbol = find_symbol(node.get('value'), node.get('scope'))
            instr('RCL', symbol.get('location'))
            return


        if node.tag == 'IF':
            L1 = new_label()
            L2 = new_label()
            code_generation(node[0])    # condicional
            instr('IFZ', L1)   # 
            code_generation(node[1])    # then-part
            instr('GTO', L2)            #
            instr('LBL', L1)            #
            code_generation(node[2])    # else-part
            instr('LBL', L2)
            return


        if node.tag == 'RETURN':
            code_generation(node[0])
            symbol = find_symbol(node.get('value'), node.get('scope'))
            instr('STO', symbol.get('location'))
            instr('RET')
            return


        if node.tag == 'NUM':
            num = node.get('value')
            instr(abs(node.get('value')))
            if num < 0:
                instr('CHS')
            return

        if node.tag == 'VAR':
            return

        if node.tag == 'WRITE':
            n = 0
            if node[0].tag == 'STR':
                LP.append(node[n].get('value'))
                instr('STR', len(LP)-1)
                n += 1
            code_generation(node[n])
            if node[n].get('datatype') == 'bool':
                instr('PRB')
            if node[n].get('datatype') == 'num':
                instr('PRN')
            return

        if node.tag == 'WHEN':
            L1 = new_label()
            code_generation(node[0])    # condicional
            instr('IFZ', L1)
            code_generation(node[1])    # cuerpo
            instr('LBL', L1)            # fin
            return

        if node.tag == 'WHILE':
            L1 = new_next_label()
            L2 = new_break_label()
            instr('LBL', L1)
            code_generation(node[0])
            instr('IFZ', L2)
            code_generation(node[1])
            instr('GTO', L1)
            instr('LBL', L2)
            stack_next.pop()
            stack_break.pop()
            return

        msg = '{}: Internal error at line {}:\n'.format(filename, node.get('lineno'))
        msg += 'Unexpected syntax tree nodel <{}>'.format(node.tag)
        # msg += '--> ' + SOURCECODE[node.get('lineno')].text + '\n'
        raise Exception(msg)

    # rutina principal
    code_generation(SYNTAXTREE)

    with open(filename + '.sbm', 'w') as file:
        for s in LP:
            file.write(s + '\n')
        file.write('%%\n')
        for c in CS:
            file.write(c + '\n')


if __name__ == '__main__':


    if len(sys.argv) > 1:
        for filename in sys.argv[1:]:
            yysbm(filename)
    else:
        filename = input()
        yysbm(filename)
