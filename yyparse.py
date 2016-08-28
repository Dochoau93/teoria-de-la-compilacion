###< 2016-08-28 18:12:00.905335 >###

#
#  yyparse.py
#    analizador sintactico para el lenguaje bcc
#

import shlex, sys, pickle
import dataTree as dt


## analizador sintactico
def yyparse(filename, quiet = False):

    ## lee la estructura de datos generada por yylex()
    with open(filename + '.dataTree', 'rb') as f:
        DATA = pickle.load(f)

    SOURCECODE  = DATA.find('SOURCECODE')
    TOKENTABLE  = DATA.find('TOKENTABLE')
    SYNTAXTREE  = DATA.find('SYNTAXTREE')
    SYMBOLTABLE = DATA.find('SYMBOLTABLE')

    # funciones auxiliares requeridas por
    # el parser durante el reconocimiento de
    # la gramatica
    def yytext(offset=0):
        #
        return TOKENTABLE[TOKENTABLE.get('index')].get('lexeme')
        #

    def yytoken(offset=0):
        #
        return TOKENTABLE[TOKENTABLE.get('index') + offset].tag
        #

    def yymatch(token, offset=0):
        #
        return token == yytoken(offset)
        #

    def yyadvance(offset=1):
        #
        TOKENTABLE.set('index', TOKENTABLE.get('index') + offset)
        #

    def yylineno():
        #
        return TOKENTABLE[TOKENTABLE.get('index')].get('lineno')
        #

    def yyaccept(token, advance=True):
        #
        if not yymatch(token):
            msg = '{}:Syntax error at line {}: '.format(filename, yylineno())
            msg += 'Unexpected symbol <token := \'{}\', symbol := \'{}\'>'.format(token, yytext())
            print(msg)
            sys.exit()
        #
        if advance:
            yyadvance()

    #
    # crea un nuevo nodo del arbol sintactico
    # sin enlazarlo a los demas
    #
    def yynewnode(kind, datatype=None, value=None, scope=None):
        #
        attrib = {'lineno':yylineno()}
        #
        if not value is None:
            attrib['value'] = value
        #
        if not datatype is None:
            attrib['datatype'] = datatype
        #
        if not scope is None:
            attrib['scope'] = scope
        #
        return dt.TreeNode(tag=kind, attrib=attrib)

    ##
    ##
    ##  G R A M A T I C A
    ##
    ##

    ##
    ##  program
    ##    -> function_decl main_prog
    ##
    def program():
        SYNTAXTREE.append(function_decl())
        SYNTAXTREE.append(main_prog())

    ##
    ## var_decl
    ##   -> ID ':' DATATYPE [',' ID ':' DATATYPE]*
    ##
    def var_decl():
        r = []
        while yymatch('ID'):
            m = yynewnode('ID', value=yytext(), scope=SYNTAXTREE.get('scope'))
            r.append(m)
            yyadvance()
            yyaccept(':')
            yyaccept('DATATYPE', advance=False)
            m.set('datatype', yytext())
            yyadvance()
            if yymatch(','):
                yyadvance()
        return r

    ##
    ##  function_decl
    ##    -> [ FUNTION FID ':' DATATYPE '(' [var_decl] ')'
    ##         [VAR var_decl ';']
    ##         stmt_block ]*
    ##
    def function_decl():

        r = yynewnode('FUNCTIONDECL')

        while yymatch('FUNCTION'):

            SYNTAXTREE.set('scope', SYNTAXTREE.get('scope') + 1)
            yyadvance()

            # nombre de la funcion y tipo retornado
            f = yynewnode('FUNCTION', value=yytext(), scope=SYNTAXTREE.get('scope'))
            r.append(f)
            yyadvance()
            yyaccept(':')
            yyaccept('DATATYPE', advance=False)
            f.set('datatype', yytext())
            SYNTAXTREE.set('datatype', yytext())
            yyadvance()

            # nombres de los argumentos y sus tipos
            yyaccept('(')
            a = yynewnode('ARGS')
            a.extend(var_decl())
            f.append(a)
            yyaccept(')')

            # cuerpo de la funcion
            if yymatch('VAR'):
                v = yynewnode('VAR')
                yyadvance()
                v.extend(var_decl())
                yyaccept(';')
                f.append(v)

            f.append(stmt_block())

            SYNTAXTREE.set('datatype', None)


        return r

    ##
    ##  main_prog
    ##    -> [VAR var_decl ';']  stmt*  END
    ##
    def main_prog():

        r = yynewnode('MAINPROG')

        if yymatch('VAR'):
            v = yynewnode('VAR')
            r.append(v)
            yyadvance()
            v.extend(var_decl())
            yyaccept(';')

        while not yymatch('END'):
            r.append(stmt())

        r.append(yynewnode('END'))

        return r

    ##
    ##  stmt_block
    ##    ->  '{' stmt+ '}'
    ##     |  stmt
    ##
    def stmt_block():
        if yymatch('{'):
            yyadvance()
            r = yynewnode('BLOCK')
            while not yymatch('}'):
                r.append(stmt())
            yyadvance()
            return r
        return stmt()

    ##
    ## stmt
    ##
    def stmt():

        ##
        ##  stmt
        ##    ->  WRITE [STR ':'] lexpr ';'
        ##
        if yymatch('WRITE'):
            r = yynewnode('WRITE')
            yyadvance()
            if yymatch('STR'):
                r.append(yynewnode('STR', datatype='str', value=yytext()))
                yyadvance()
                yyaccept(':')
            r.append(lexpr())
            yyaccept(';')
            return r

        ##
        ##  stmt
        ##     ->  WHEN  '(' lexpr ')' DO stmt_block
        ##
        if yymatch('WHEN'):
            r = yynewnode('WHEN')
            yyadvance()
            yyaccept('(')
            r.append(lexpr())
            yyaccept(')')
            yyaccept('DO')
            r.append(stmt_block())
            return r

        ##
        ##  stmt
        ##     ->  IF    '(' lexpr ')' DO stmt_block  ELSE  stmt_block
        ##
        if yymatch('IF'):
            r = yynewnode('IF')
            yyadvance()
            yyaccept('(')
            r.append(lexpr())
            yyaccept(')')
            yyaccept('DO')
            r.append(stmt_block())
            yyaccept('ELSE')
            r.append(stmt_block())
            return r

        ##
        ##  stmt
        ##     ->  WHILE '(' lexpr ')' DO stmt_block
        ##
        if yymatch('WHILE'):
            r = yynewnode('WHILE')
            yyadvance()
            yyaccept('(')
            r.append(lexpr())
            yyaccept(')')
            yyaccept('DO')
            r.append(stmt_block())
            return r

        ##
        ##  stmt
        ##     ->  RETURN lexpr ';'
        ##
        if yymatch('RETURN'):
            r = yynewnode( 'RETURN',
                           datatype=SYNTAXTREE.get('datatype'),
                           scope=SYNTAXTREE.get('scope'),
                           value='__return__')
            yyadvance()
            r.append(lexpr())
            yyaccept(';')
            return r

        ##
        ##  stmt
        ##     ->  ID ':=' lexpr ';'
        ##

        if yymatch('ID') and yymatch(':=', offset=1):
            r = yynewnode('ASSIGN', value=yytext(), scope=SYNTAXTREE.get('scope'))
            yyadvance(2)
            r.append(lexpr())
            yyaccept(';')
            return r

        ##
        ##  stmt
        ##     ->  UNLESS  '(' lexpr ')' DO stmt_block
        ##


        ##
        ##  stmt
        ##     ->  UNTIL '(' lexpr ')' DO stmt_block
        ##


        ##
        ##  stmt
        ##     ->  LOOP stmt_block
        ##


        ##
        ##  stmt
        ##     ->  DO stmt_block WHILE '(' lexpr ')'
        ##     ->  DO stmt_block UNTIL '(' lexpr ')'
        ##


        ##
        ##  stmt
        ##     ->  REPEAT NUM ':' stmt_block
        ##

        # <inserte su codigo aqui > #


        ##
        ##  stmt
        ##     ->  FOR ID ':=' lexpr, lexpr, lexpr DO stmt_block
        ##


        ##
        ##  stmt
        ##     ->  END ';'
        ##


        ##
        ##  stmt
        ##     ->  NEXT ';'
        ##


        ##
        ##  stmt
        ##     ->  BREAK ';'
        ##


        ##
        ##  stmt
        ##     ->  ID '+=' lexpr ';'
        ##


        ##
        ##  stmt
        ##     ->  ID '-=' lexpr ';'
        ##


        ##
        ##  stmt
        ##     ->  ID '*=' lexpr ';'
        ##


        ##
        ##  stmt
        ##     ->  ID '/=' lexpr ';'
        ##


        ##
        ##  stmt
        ##     ->  ID '%=' lexpr ';'
        ##


        ##
        ##  stmt
        ##     ->  ID ++ ';'
        ##


        ##
        ##  stmt
        ##     ->  ++ ID ';'
        ##


        ##
        ##  stmt
        ##     ->  ID -- ';'
        ##


        ##
        ##  stmt
        ##     ->  -- ID ';'
        ##


        msg = '{}:Syntax error at line {}: '.format(filename, yylineno())
        msg += 'Unknown token <{}>'.format(yytoken())
        print(msg)
        sys.exit()

    # -------------------------------------------------------------------------
    #
    #  lexpr
    #    ->  nexpr [[AND nexpr]* | [OR nexpr]*]
    #
    def lexpr():
        r = nexpr()
        #
        # escriba su codigo aqui
        #
        return r


    # -------------------------------------------------------------------------
    #
    #  nexpr
    #    ->  NOT '(' lexpr ')'
    #     |  rexpr
    #
    def nexpr():


        return rexpr()



    #  rexpr
    #    ->  simple_expr '<'  simple_expr
    #     |  simple_expr '==' simple_expr
    #     |  simple_expr '<=' simple_expr
    #     |  simple_expr '>'  simple_expr
    #     |  simple_expr '>=' simple_expr
    #     |  simple_expr '!=' simple_expr
    #
    def rexpr():

        r = simple_expr()

        if yymatch('<'):
            m = yynewnode(yytext(),  datatype='bool')
            yyadvance()
            m.append(r)
            m.append(simple_expr())
            return m

        if yymatch('<='):
            m = yynewnode(yytext(),  datatype='bool')
            yyadvance()
            m.append(r)
            m.append(simple_expr())
            return m


        return r

    ##
    ##  simple_expr
    ##    ->  term [('+'|'-') term]*
    ##
    def simple_expr():
        r = term()


        while yymatch('+'):
            n = yynewnode(yytext(), datatype='num')
            yyadvance()
            n.append(r)
            n.append(term())
            r = n

        return r


    ##
    ##  term
    ##    ->  factor [ ('*'|'/') factor]*
    ##
    def term():

        r = factor()


        while yymatch('*'):
            n = yynewnode(yytext(), datatype='num')
            yyadvance()
            n.append(r)
            n.append(factor())
            r = n
        return r


    ##
    ##  factor
    ##    ->  ['+'|'-']? NUM
    ##     |  ['+'|'-']? ID
    ##     |  ['+'|'-']?  '(' lexpr ')'
    ##     |  ['+'|'-']? UFID '(' [lexpr [',' lexpr]*] ')'
    ##     |  ['+'|'-']? BFID '(' [lexpr [',' lexpr]*] ')'
    ##     |  ++ID
    ##     |  --ID
    ##     |  ID++
    ##     |  ID--
    ##     |  BOOL
    ##

    def factor():

        if yymatch('NUM'):
            value = yytext()
            if value.isdigit():
                value = int(value)
            else:
                value = float(value)
            r = yynewnode('NUM', datatype='num', value=value)
            yyadvance()
            return r


        if yymatch('ID'):
            r = yynewnode('ID', value=yytext(), scope=SYNTAXTREE.get('scope'))
            yyadvance()
            return r

        if yymatch('('):
            yyadvance()
            r = lexpr()
            yyaccept(')')
            return r


        if yymatch('UFID'):
            r = yynewnode('UFCALL', value=yytext())
            yyadvance()
            yyaccept('(')
            while not yymatch(')'):
                r.append(lexpr())
                if yymatch(','):
                    yyadvance()
            yyaccept(')')
            return r


        if yymatch('BFID'):
            r = yynewnode('BFCALL', value=yytext())
            yyadvance()
            yyaccept('(')
            while not yymatch(')'):
                r.append(lexpr())
                if yymatch(','):
                    yyadvance()
            yyaccept(')')
            return r


        if yymatch('BOOL'):
            value = True if yytext() == 'true' else False
            r = yynewnode('BOOL', datatype='bool', value=value)
            yyadvance()
            return r

        msg = '{}:Syntax error at line {}: '.format(filename, yylineno())
        msg += 'Unexpected symbol <{}>'.format(yytext())
        print(msg)
        sys.exit()

    #
    # rutina principal
    #   inicia el reconocimiento llamando la funcion
    #   correspondiente al simbolo inicial de la gramatica
    #

    #
    # 'index'
    #    es usado para recorrer secuencialmente la tabla de tokens
    #
    # 'scope'
    #   es el indice que indica la region que correspondiente
    #    a una funcion (porcion de codio en que es visible una
    #    variable)
    #
    # 'datatype'
    #    almacena el tipo de dato que retorna la funcion que
    #    esta siendo procesada
    #
    # 'repeat'
    #    es un contador usado para generar variables unicas
    #    que son usadas en los comados  'repeat'
    #
    TOKENTABLE.set('index', 0)
    SYNTAXTREE.set('scope', 0)
    SYNTAXTREE.set('datatype', None)
    SYNTAXTREE.set('repeat', -1)

    # se realiza el proceso de analisis sintactico
    # del codigo fuente
    program()

    del TOKENTABLE.attrib['index']
    del SYNTAXTREE.attrib['scope']
    del SYNTAXTREE.attrib['datatype']
    del SYNTAXTREE.attrib['repeat']


    #   en este punto se ha construido el arbol sintactico
    #   y se procede a almacenar el resultado en un archivo
    #   en disco
    with open(filename + '.dataTree', 'wb') as f:
        pickle.dump(DATA, f)

    if quiet == False:
        dt.printTree(SYNTAXTREE)


if __name__ == '__main__':


    if len(sys.argv) > 1:
        for filename in sys.argv[1:]:
            yyparse(filename)
    else:
        filename = input()
        yyparse(filename)
