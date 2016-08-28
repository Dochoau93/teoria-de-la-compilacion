###< 2016-08-28 18:12:00.911927 >###

#
#  rbm.py
#    maquina virtual de registros
#

import shlex, sys, math


def rbm(filename):
    #
    # registros del procesador
    #
    DR  = [0]    * 256   # Data Registers
    TR  = [0]    * 256   # Temporary Registers
    JT  = [None] * 256   # Jump Table
    SF  = []             # Stack Frame
    SS  = []             # Stack
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

        elif len(m) >= 3 and m[-3] == 'ADD+':

            if x[n] == '.':
                txt = '.' + x[n+1]
                m[-1] = float(txt)
                n += 2

            elif x[n] == '-' and x[n+1].isdigit() and x[n+2] != '.':
                m.append(-int(x[n+1]))
                n += 2

            elif x[n] == '-' and x[n+1].isdigit() and x[n+2] == '.' and not x[n+3]:
                txt = '-' + x[n+1] + '.'
                m.append(-float(txt))
                n += 3

            elif x[n] == '-' and x[n+1].isdigit() and x[n+2] == '.' and x[n+3].isdigit():
                txt = '-' + x[n+1] + '.' + x[n+3]
                m.append(-float(txt))
                n += 4

            elif x[n].isdigit() and x[n+1] == '.' and not x[n+2].isdigit():
                txt = x[n] + '.'
                m.append(float(txt))
                n += 2

            elif x[n].isdigit() and x[n+1] == '.' and x[n+2].isdigit():
                txt = x[n] + '.' + x[n+2]
                m.append(float(txt))
                n += 3

            else:
                m.append(int(x[n]))
                n += 1

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
        s = CS[IP+2] if IP+2 < len(CS) else []
        t = CS[IP+3] if IP+3 < len(CS) else []

        # print(CS[IP], r, s, t)
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
        elif CS[IP] == '?':

            x = input()
            a = int(x)
            b = float(x)
            if a == b:
                TR[r] = a
            else:
                TR[r] = b
            IP += 1

        elif CS[IP] == 'PRN':

            result = TR[r]
            print(result)
            IP += 1

        elif CS[IP] == 'PRB':

            result = TR[r]
            if result == 0:
                print('false')
            else:
                print('true')
            IP += 1

        elif CS[IP] == 'STR':

            print(LP[r][1:-1], end = '')
            IP += 1

        elif CS[IP] == 'XCHG':

            temp = TR[r]
            TR[r] = TR[s]
            TR[s] = temp

        # ---------------------------------------------------------------------
        #
        # saltos / subrutinas
        #

        elif CS[IP] == 'LBL':

            IP += 1

        elif CS[IP] == 'GTO':

            IP = JT[r] - 1

        elif CS[IP] == 'IFZ':

            IP = JT[s] - 1 if TR[r] == 0 else IP + 2

        elif CS[IP] == 'IFNZ':

            IP = JT[s] - 1 if TR[r] != 0 else IP + 2

        elif CS[IP] == 'GSB':

            SF.append(IP + 1)
            IP = JT[r] - 1

            for n in TR:
                SS.append(n)

        elif CS[IP] == 'RET':

            IP = SF.pop()

            for n in range(len(TR)-1,-1,-1):
                TR[n] = SS.pop()

        # ---------------------------------------------------------------------
        #
        # gestion de la memoria
        #
        elif CS[IP] == 'RCL':

            TR[r] = DR[s]
            IP += 2

        elif CS[IP] == 'RCL+':

            TR[r] += DR[s]
            IP += 2

        elif CS[IP] == 'RCL*':
            IP += 2

            TR[r] *= DR[s]

        elif CS[IP] == 'RCL-':

            TR[r] -= DR[s]
            IP += 2

        elif CS[IP] == 'RCL/':

            TR[r] /= DR[s]
            IP += 2

        elif CS[IP] == 'RCL%':

            TR[r] %= DR[s]
            IP += 2

        elif CS[IP] == 'STO':

            DR[s] = TR[r]
            IP += 2

        elif CS[IP] == 'STO+':

            DR[s] += TR[r]
            IP += 2

        elif CS[IP] == 'STO*':

            DR[s] *= TR[r]
            IP += 2

        elif CS[IP] == 'STO-':

            DR[s] -= TR[r]
            IP += 2

        elif CS[IP] == 'STO/':

            DR[s] /= TR[r]
            IP += 2

        elif CS[IP] == 'STO%':

            DR[s] %= TR[r]
            IP += 2

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
        elif CS[IP] == 'SGN':

            if TR[s] > 0:
                TR[r] = 1
            elif TR[s] < 0:
                TR[r] = -1
            else:
                TR[r] = 0
            IP += 2

        elif CS[IP] == 'FABS':

            TR[r] = math.fabs(TR[s])
            IP += 2

        elif CS[IP] == 'SQRT':

            TR[r] = math.sqrt(TR[s])
            IP += 2

        elif CS[IP] == 'LOG':

            TR[r] = math.log(TR[s])
            IP += 2

        elif CS[IP] == 'EXP':

            TR[r] = math.exp(TR[s])
            IP += 2

        elif CS[IP] == 'LOG10':

            TR[r] = math.log10(TR[s])
            IP += 2

        elif CS[IP] == 'SIN':

            TR[r] = math.sin(TR[s])
            IP += 2

        elif CS[IP] == 'COS':

            TR[r] = math.cos(OS[s])
            IP += 2

        elif CS[IP] == 'TAN':

            TR[r] = math.tan(TR[s])
            IP += 2

        elif CS[IP] == 'ASN':

            TR[r] = math.asin(TR[s])
            IP += 2

        elif CS[IP] == 'ACS':

            TR[r] = math.acos(TR[s])
            IP += 2

        elif CS[IP] == 'ATN':

            TR[r] = math.atan(TR[s])
            IP += 2
        #
        # funciones compelentarias
        #
        elif CS[IP] == 'CHS':

            TR[r] = - TR[s]
            IP += 2

        elif CS[IP] == 'SQR':

            TR[r] = TR[s] ^ 2
            IP += 2

        elif CS[IP] == 'INV':

            TR[r] = 1 / TR[s]
            IP += 2

        elif CS[IP] == 'INTG':

            TR[r] = int(TR[s])
            IP += 2

        elif CS[IP] == 'FRAC':

            TR[r] = TR[s] - int(TR[s])
            IP += 2

        elif CS[IP] == 'ADD+':

            TR[r] = TR[s] + t
            IP += 3

        elif CS[IP] == '+':

            TR[r] = TR[s] + TR[t]
            IP += 3

        elif CS[IP] == '-':

            TR[r] = TR[s] - TR[t]
            IP += 3

        elif CS[IP] == '*':

            TR[r] = TR[s] * TR[t]
            IP += 3

        elif CS[IP] == '/':

            TR[r] = TR[s] / TR[t]
            IP += 3

        elif CS[IP] == '%':

            TR[r] = TR[s] % TR[t]
            IP += 3

        elif CS[IP] == '<':

            TR[r] = 1 if TR[s] < TR[t] else 0
            IP += 3

        elif CS[IP] == '<=':

            TR[r] = 1 if TR[s] <= TR[t] else 0
            IP += 3

        elif CS[IP] == '>':

            TR[r] = 1 if TR[s] > TR[t] else 0
            IP += 3

        elif CS[IP] == '>=':

            TR[r] = 1 if TR[s] >= TR[t] else 0
            IP += 3

        elif CS[IP] == '==':

            TR[r] = 1 if TR[s] == TR[t] else 0
            IP += 3

        elif CS[IP] == '!=':

            TR[r] = 1 if TR[s] != TR[t] else 0
            IP += 3

        elif CS[IP] == 'AND':

            TR[r] = 1 if TR[s] and TR[t] else 0
            IP += 3

        elif CS[IP] == 'OR':

            TR[r] = 1 if TR[s] or TR[t] else 0
            IP += 3

        elif CS[IP] == 'NOT':

            TR[r] = 0 if TR[s] else 1
            IP += 2

        else:

            txt = '\n\nrbm: Syntax error: unknown bytecode <{}>\n\n'.format(CS[IP])
            print(txt)
            sys.exit()

        # ---------------------------------------------------------------------
        TR[0] = 0   # TR[0] es siempre 0
        IP += 1



if __name__ == '__main__':


    if len(sys.argv) > 1:
        for filename in sys.argv[1:]:
            rbm(filename)
    else:
        filename = input()
        rbm(filename)
