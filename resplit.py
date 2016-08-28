###< 2016-08-28 18:12:00.915325 >###

##
##  resplit
##    esta funcion permite dividir una cadena de texto
##    en lexemas usando expresiones regulares (re)
##
##    ejemplo: resplit('abb*', 'ababbabbb') devuelve 'ab/abb/abbb'
##  

##
## Estructuras de datos.
##
##  dfa:  Es una lista de diccionarios.
##        El elemento i de la lista dfa es un diccionario
##        que representa el nodo i.
##        Cada clave del diccionario corresponde a un caracter
##        del alfabeto el autómata
##        Cada valor del diccionario es el siguiente estado
##        al que se realiza la transicion despues de leer
##        el caracter correspondiente a la clave
##
##        por ejemplo:
##
##        dfa = [{a:1, b:2}, {a:0, b:1}]
##
##        indica que en el estaddo 0 si se lee la `a` se
##        va al estado 1 y si se lee la `b` se va al estado 2.
##        de la misma forma si se está en el estado 1 y se lee
##        la `a` se va al estado 0 y si se lee la `b` se va al
##        estado 1.
##
##  accept_states:  es un vector de enteros que contiene los
##        estados de aceptación del dfa.
##


import sys

dfa = []
accept_states = []

# agrega c
def addch(state, c):
    next_state = len(dfa)
    dfa.append(dict())
    dfa[state][c] = next_state
    return next_state


# agrega c*
def addch_star(state, c):
    dfa[state][c] = state
    return state




# construye la tabla de transiciones
# a partir de la expresion regular
def do_dfa(re, text):
    pos = 0
    state = 0
    while pos < len(re):
        if pos+1 < len(re) and re[pos+1] == '*':
            state = addch_star(state, re[pos])
            pos += 1
        else:
            state = addch(state, re[pos])
        pos += 1
    accept_states.append(state)
    return


# recorre el dfa a partir de los caracteres
def sim_dfa(text):
    state = 0
    pos = 0
    text_len = 0
    while pos < len(text) and state != -1:
        d = dfa[state]
        ch = text[pos]
        if ch in d.keys():
            state = d[ch]
            if state in accept_states:
                text_len = pos+1
            pos += 1
        elif '.' in d.keys():
            state = d['.']
            if state in accept_states:
                text_len = pos+1
            pos += 1
        else:
            state = -1
    return text_len



def resplit(re, text, sep = '/'):
    del dfa[:]
    del accept_states[:]
    dfa.append(dict())
    do_dfa(re, text)
    m = 0
    n = 0
    result = ''
    while m < len(text):
        n = sim_dfa(text[m:])
        if n == 0:
            return 'FAIL'
        if m != 0:
            result += sep
        result += text[m:m+n]
        m += n
    return result


assert resplit('ab0', 'abcabcabc') == 'FAIL'
assert resplit('abc', 'abcabcabc') == 'abc/abc/abc'
assert resplit('a.c', 'a0ca1ca2c') == 'a0c/a1c/a2c'
assert resplit('ab*c', 'acabcabbcabbbc') == 'ac/abc/abbc/abbbc'


