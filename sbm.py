###< 2016-08-28 18:12:00.913367 >###

#! /usr/bin/python3
import shlex, sys, math


def sbm(filename):
    #
    # registros del procesador
    #
    OS  = []             # Operand Stack
    DR  = [0]    * 256   # Data Registers
    JT  = [None] * 256   # Jump Table
    SF  = []             # Stack Frame
    LP  = []             # Literal Pool
    IP  = 0              # Instruction Pointer
    HLT = False          # HaLT register
    CS  = ''             # Code Segment



    #
    # Carga del programa desde el archivo y lo separa en cadenas de texto
    #
    x = open(filename, 'r').readlines()
    for n, line in enumerate(x):
        if line[-1] == '\n':
            line = line[:-1]
        if line == '%%':
            break
        LP.append(line)

    x = x[n+1:]

    x = ''.join(x)
    x = list(shlex.shlex(x))

    #
    # shlex separa la cadena '123.456' como '123', '.', '456'
    # y debe unirse como un numero. La cadena de texto debe
    # convertirse en numero
    #
    m = []
    n = 0
    while n < len(x):

        if x[n] == 'RCL' and x[n+1] in ('+', '-', '*', '/', '%'):
            m.append('RCL' + x[n+1])
            n += 2

        elif x[n] == 'STO' and x[n+1] == '+' and x[n+2] == '+':
            m.append('STO++')
            n += 3

        elif x[n] == 'STO' and x[n+1] == '-' and x[n+2] == '-':
            m.append('STO--')
            n += 3

        elif x[n] == 'STO' and x[n+1] in ('+', '-', '*', '/', '%'):
            m.append('STO' + x[n+1])
            n += 2

        elif x[n] == 'ADD' and x[n+1] == '+':
            m.append('ADD+')
            n += 2

        elif x[n] == '<' and x[n+1] == '=':
            m.append('<=')
            n += 2

        elif x[n] == '>' and x[n+1] == '=':
            m.append('>=')
            n += 2

        elif x[n] == '=' and x[n+1] == '=':
            m.append('==')
            n += 2

        elif x[n] == '!' and x[n+1] == '=':
            m.append('!=')
            n += 2

        elif x[n].isdigit() and x[n+1] == '.' and not x[n+2].isdigit():
            txt = x[n] + '.'
            m.append(float(txt))
            n += 2

        elif x[n].isdigit() and x[n+1] == '.' and x[n+2].isdigit():
            txt = x[n] + '.' + x[n+2]
            m.append(float(txt))
            n += 3

        elif x[n].isdigit():
            m.append(int(x[n]))
            n += 1

        else:
            m.append(x[n])
            n += 1

    CS = m

    #
    # Se actualiza la tabla de saltos (JT) con las
    # posiciones de las etiquetas 'lbl' dentro del codigo.
    # CS[i+1] es el numero de la etiqueta
    # i es el numero de la instruccion dentro del programa
    #
    for i, code in enumerate(CS):

        if CS[i] == 'LBL':
            JT[CS[i+1]] = i

    #
    # Ejecucion del programa
    #
    while HLT != True and IP < len(CS):

        #
        # lee los argumentos de la instruccion
        #
        r = CS[IP+1] if IP+1 < len(CS) else []

        # ---------------------------------------------------------------------
        #
        # parada del programa
        #
        if CS[IP] == 'HLT':

            HLT = True

        # ---------------------------------------------------------------------
        #
        # entrada / salida
        #
        elif type(CS[IP]) == type(0) or type(CS[IP]) == type(0.0):

            OS.append(CS[IP])

        elif CS[IP] == '?':

            x = input()
            a = int(x)
            b = float(x)
            if a == b:
                OS.append(a)
            else:
                OS.append(b)

        elif CS[IP] == 'PRN':
            result = OS.pop()
            print(result)
            IP += 0

        elif CS[IP] == 'PRB':

            result = OS.pop()
            if result == 0 or result == 0.0:
                print('false')
            else:
                print('true')
            IP += 0

        elif CS[IP] == 'STR':

            print(LP[r][1:-1], end = '')
            IP += 0

        elif CS[IP] == 'XCHG':

            temp = OS[-2]
            OS[-2] = OS[-1]
            OS[-1] = temp

        # ---------------------------------------------------------------------
        #
        # saltos / subrutinas
        #
        elif CS[IP] == 'LBL':

            IP += 1

        elif CS[IP] == 'GTO':

            IP = JT[r] - 1

        elif CS[IP] == 'IFZ':

            IP = JT[r] - 1 if OS.pop() == 0 else IP + 1

        elif CS[IP] == 'IFNZ':

            IP = JT[r] - 1 if OS.pop() != 0 else IP + 1

        elif CS[IP] == 'GSB':

            SF.append(IP + 1)
            IP = JT[r] - 1

        elif CS[IP] == 'RET':

            IP = SF.pop()

        # ---------------------------------------------------------------------
        #
        # gestion de la memoria
        #
        elif CS[IP] == 'RCL':

                OS.append( DR[r] )
                IP += 1

        elif CS[IP] == 'RCL+':

                OS[-1] += DR[s]
                IP += 2

        elif CS[IP] == 'RCL*':

                OS[-1] *= DR[s]
                IP += 2

        elif CS[IP] == 'RCL-':

                OS[-1] -= DR[s]
                IP += 2

        elif CS[IP] == 'RCL/':

                OS[-1] /= DR[s]
                IP += 2

        elif CS[IP] == 'STO':

                DR[r] = OS.pop()
                IP += 1

        elif CS[IP] == 'STO+':

                DR[r] += OS.pop()
                IP += 1

        elif CS[IP] == 'STO*':

                DR[r] *= OS.pop()
                IP += 1

        elif CS[IP] == 'STO-':

                DR[r] -= OS.pop()
                IP += 1

        elif CS[IP] == 'STO/':

                DR[r] /= OS.pop()
                IP += 1

        elif CS[IP] == 'STO%':

                DR[r] %= OS.pop()
                IP += 1

        elif CS[IP] == 'STO++':

                DR[r] += 1
                IP += 1

        elif CS[IP] == 'STO--':

                DR[r] -= 1
                IP += 1

        # ---------------------------------------------------------------------
        #
        # funciones matematicas (math library)
        #
        elif CS[IP] == 'FABS':

            OS[-1] = math.fabs(OS[-1])

        elif CS[IP] == 'SQRT':

             OS[-1] = math.sqrt(OS[-1])

        elif CS[IP] == 'LOG':

            OS[-1] = math.log(OS[-1])

        elif CS[IP] == 'EXP':

            OS[-1] = math.exp(OS[-1])

        elif CS[IP] == 'LOG10':

            OS[-1] = math.log10(OS[-1])

        elif CS[IP] == 'SIN':

            OS[-1] = math.sin(OS[-1])

        elif CS[IP] == 'COS':

            OS[-1] = math.cos(OS[-1])

        elif CS[IP] == 'TAN':

            OS[-1] = math.tan(OS[-1])

        elif CS[IP] == 'ASN':

            OS[-1] = math.asin(OS[-1])

        elif CS[IP] == 'ACS':

            OS[-1] = math.acos(OS[-1])

        elif CS[IP] == 'ATN':

            OS[-1] = math.atan(OS[-1])
        #
        # funciones compelentarias
        #
        elif CS[IP] == 'CHS':

            OS[-1]  = - OS[-1]

        elif CS[IP] == 'SQ':

            OS[-1]  = OS[-1] ^  2

        elif CS[IP] == 'INV':

            OS[-1]  = 1 / OS[-1]

        elif CS[IP] == 'INTG':

            OS[-1]  = int(OS[-1])

        elif CS[IP] == 'FRAC':

            OS[-1]  = OS[-1] - int(OS[-1])

        elif CS[IP] == 'INCR':

            OS[-1]  += 1

        elif CS[IP] == 'DECR':

            OS[-1]  -= 1

        # ---------------------------------------------------------------------
        elif CS[IP] == '+':

            OS.append(OS.pop() + OS.pop())

        elif CS[IP] == '*':

            OS.append(OS.pop() * OS.pop())

        elif CS[IP] == '-':

            OS.append(- OS.pop() + OS.pop())

        elif CS[IP] == '/':

            OS.append(1 / OS.pop() * OS.pop())

        elif CS[IP] == '%':

            b = OS.pop()
            a = OS.pop()
            OS.append(b % a)

        # ---------------------------------------------------------------------
        elif CS[IP] == '==':

            OS.append(1 if OS.pop() == OS.pop() else 0)

        elif CS[IP] == '<':

            OS.append(1 if OS.pop() > OS.pop() else 0)

        elif CS[IP] == '<=':

            OS.append(1 if OS.pop() >= OS.pop() else 0)

        elif CS[IP] == '>':

            OS.append(1 if OS.pop() < OS.pop() else 0)

        elif CS[IP] == '>=':

            OS.append(1 if OS.pop() <= OS.pop() else 0)

        elif CS[IP] == '==':

            OS.append(1 if OS.pop() == OS.pop() else 0)

        elif CS[IP] == '!=':

            OS.append(1 if OS.pop() != OS.pop() else 0)

        elif CS[IP] == 'AND':

            OS.append(1 if OS.pop() and OS.pop() else 0)

        elif CS[IP] == 'OR':

            OS.append(1 if OS.pop() or OS.pop() else 0)

        elif CS[IP] == 'NOT':

            OS[-1] = 1 if OS[-1] == 0 else 0

        else:

            txt = '\n\nsbm Syntax error: unknown bytecode <{}>\n\n'.format(CS[IP])
            print(txt)
            sys.exit()

        # ---------------------------------------------------------------------

        IP += 1



#
# Esa es la rutina principal para llamada de la funcion
# La variable DBG controla si se ejecutan las corridas
# de diagnostico o la operacion normal del programa
#

if __name__ == '__main__':


    if len(sys.argv) > 1:
        for filename in sys.argv[1:]:
            sbm(filename)
    else:
        filename = input()
        sbm(filename)
