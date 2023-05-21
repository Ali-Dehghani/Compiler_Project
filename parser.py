import scanner
import json

f_json = open('First-Follow.json')
data = json.load(f_json)
f_json.close()

terminals = data['terminals']
non_terminals = data['non_terminals']
first = data['first']
follow = data['follow']
f_errors = open("syntax_errors.txt", "w")
token = ''
token_str = ''
# state = '0'
# halt_program = False
# get_new_token = True
is_there_any_error = False

stack = ['']


def get_next_token():
    global token_str, token
    token = scanner.get_next_token()
    if token[0] in ['KEYWORD', 'SYMBOL']:
        token_str = token[1]
    else:
        token_str = token[0]
    return


def match(match_input):
    global token_str, token
    if match_input == token_str:  # token is parsed
        get_next_token()
    else:
        error_handler(3, match_input)


def handle(non_terminal_str, non_terminal_func):
    if token_str not in follow[non_terminal_str]:
        error_handler(1, token_str)
        get_next_token()
        non_terminal_func()
    elif token_str in follow[non_terminal_str]:
        error_handler(2, non_terminal_str)


def error_handler(error_type, input):
    global is_there_any_error
    is_there_any_error = True
    if error_type == 1:
        f_errors.write(f'#{scanner.get_current_line()} : syntax error, illegal {input}\n')
    elif error_type == 2:
        f_errors.write(f'#{scanner.get_current_line()} : syntax error, missing {input}\n')
    elif error_type == 3:
        f_errors.write(f'#{scanner.get_current_line()} : syntax error, missing {input}\n')


def parse():
    global terminals, non_terminals, first, follow, token, token_str, is_there_any_error
    get_next_token()
    Program()
    if not is_there_any_error:
        f_errors.write(f'There is no syntax error.')
    f_errors.close()
    return


def Program():
    if token_str == '$':
        return  # end of program
    elif token_str in (first['Declaration_list'] + follow['Program']):    # epsilon move (derivative)
        Declaration_list()
    else:   # error
        handle('Program', Program)


def Declaration_list():
    if token_str == '$':
        return  # end of program
    elif token_str in first['Declaration']:
        Declaration()
        Declaration_list()
    elif token_str in follow['Declaration_list']:  # epsilon move
        return
    else:   # error
        handle('Declaration_list', Declaration_list)


def Declaration():
    if token_str in first['Declaration_initial']:
        Declaration_initial()
        Declaration_prime()
    else:   # error
        handle('Declaration', Declaration)


def Declaration_initial():
    if token_str in first['Type_specifier']:
        Type_specifier()
        match('ID')
    else:   # error
        handle('Declaration_initial', Declaration_initial)


def Declaration_prime():
    if token_str in first['Fun_declaration_prime']:
        Fun_declaration_prime()
    elif token_str in first['Var_declaration_prime']:
        Var_declaration_prime()
    else:   # error
        handle('Declaration_prime', Declaration_prime)


def Var_declaration_prime():
    if token_str == '[':
        match('[')
        match('NUM')
        match(']')
        match(';')
    elif token_str == ';':
        match(';')
    else:   # error
        handle('Var_declaration_prime', Var_declaration_prime)


def Fun_declaration_prime():
    if token_str == '(':
        match('(')
        Params()
        match(')')
        Compound_stmt()
    else:   # error
        handle('Fun_declaration_prime', Fun_declaration_prime)


def Type_specifier():
    if token_str == 'int':
        match('int')
    elif token_str == 'void':
        match('void')
    else:   # error
        handle('Type_specifier', Type_specifier)


def Params():
    if token_str == 'int':
        match('int')
        match('ID')
        Param_prime()
        Param_list()
    elif token_str == 'void':
        match('void')
    else:   # error
        handle('Params', Params)


def Param_list():
    if token_str == ',':
        match(',')
        Param()
        Param_list()
    elif token_str in follow["Param_list"]:     # epsilon move
        return
    else:   # error
        handle('Param_list', Param_list)


def Param():
    if token_str in first['Declaration_initial']:
        Declaration_initial()
        Param_prime()
    else:   # error
        handle('Param', Param)


def Param_prime():
    if token_str == '[':
        match('[')
        match(']')
    elif token_str in follow['Param_prime']:  # epsilon move
        return
    else:   # error
        handle('Params_prime', Param_prime)


def Compound_stmt():
    if token_str == '{':
        match('{')
        Declaration_list()
        Statement_list()
        match('}')
    else:   # error
        handle('Compound_stmt', Compound_stmt)


def Statement_list():
    if token_str in first['Statement']:
        Statement()
        Statement_list()
    elif token_str in follow['Statement_list']:  # epsilon move
        return
    else:   # error
        handle('Statement_list', Statement_list)


def Statement():
    if token_str in first['Expression_stmt']:
        Expression_stmt()
    elif token_str in first['Compound_stmt']:
        Compound_stmt()
    elif token_str in first['Selection_stmt']:
        Selection_stmt()
    elif token_str in first['Iteration_stmt']:
        Iteration_stmt()
    elif token_str in first['Return_stmt']:
        Return_stmt()
    else:   # error
        handle('Statement', Statement)


def Expression_stmt():
    if token_str in first['Expression']:
        Expression()
        match(';')
    elif token_str == 'break':
        match('break')
        match(';')
    elif token_str == ';':
        match(';')
    else:   # error
        handle('Expression_stmt', Expression_stmt)


def Selection_stmt():
    if token_str == 'if':
        match('if')
        match('(')
        Expression()
        match(')')
        Statement()
        match('else')
        Statement()
    else:   # error
        handle('Selection_stmt', Selection_stmt)


def Iteration_stmt():
    if token_str == 'repeat':
        match('repeat')
        Statement()
        match('until')
        match('(')
        Expression()
        match(')')
    else:   # error
        handle('Iteration_stmt', Iteration_stmt)


def Return_stmt():
    if token_str == 'return':
        match('return')
        Return_stmt_prime()
    else:   # error
        handle('Return_stmt', Return_stmt)


def Return_stmt_prime():
    if token_str == ';':
        match(';')
    elif token_str in first['Expression']:
        Expression()
        match(';')
    else:   # error
        handle('Return_stmt_prime', Return_stmt_prime)


def Expression():
    if token_str in first['Simple_expression_zegond']:
        Simple_expression_zegond()
    elif token_str == "ID":
        match('ID')
        B()
    else:   # error
        handle('Expression', Expression)


def B():
    if token_str == '=':
        match('=')
        Expression()
    elif token_str == '[':
        match('[')
        Expression()
        match(']')
        H()
    elif token_str in (first['Simple_expression_prime'] + follow['B']):     # epsilon move (derivative)
        Simple_expression_prime()
    else:   # error
        handle('B', B)


def H():
    global token_str
    if token_str == '=':
        match('=')
        Expression()
        return
    elif token_str in (first['G'] + first['D'] + first['C'] + follow['H']):  # the epsilon move (derivative)
        G()
        D()
        C()
        return
    else:   # error
        handle('H', H())


def Simple_expression_zegond():
    if token_str in first['Additive_expression_zegond']:
        Additive_expression_zegond()
        C()
        return
    else:   # error
        handle('Simple_expression_zegond', Simple_expression_zegond())


def Simple_expression_prime():
    if token_str in (first['Additive_expression_prime'] + first['C'] + follow['Simple_expression_prime']):  # the epsilon move  (derivative)
        Additive_expression_prime()
        C()
        return
    else:
        handle('Simple_expression_prime', Simple_expression_prime)


def C():
    if token_str in first['Relop']:
        Relop()
        Additive_expression()
        return
    elif token_str in follow['C']:  # the epsilon move
        return
    else:
        handle('C', C)


def Relop():
    if token_str == '<':
        match('<')
        return
    elif token_str == '==':
        match('==')
        return
    else:
        handle('Relop', Relop)


def Additive_expression():
    if token_str in first['Term']:
        Term()
        D()
        return
    else:
        handle('Additive_expression', Additive_expression)


def Additive_expression_prime():
    if token_str in (first['Term_prime'] + first['D'] + follow['Additive_expression_prime']):  # the epsilon move  (derivative)
        Term_prime()
        D()
        return
    else:
        handle('Additive_expression_prime', Additive_expression_prime)


def Additive_expression_zegond():
    if token_str in first['Term_zegond']:
        Term_zegond()
        D()
        return
    else:
        handle('Additive_expression_zegond', Additive_expression_zegond)


def D():
    if token_str in first['Addop']:
        Addop()
        Term()
        D()
        return
    elif token_str in follow['D']:  # the epsilon move
        return
    else:
        handle('D', D)


def Addop():
    if token_str == '+':
        match('+')
        return
    elif token_str == '-':
        match('-')
        return
    else:
        handle('Addop', Addop)


def Term():
    if token_str in first['Factor']:
        Factor()
        G()
        return
    else:
        handle('Term', Term)


def Term_prime():
    if token_str in (first['Factor_prime'] + first['G'] + follow['Term_prime']):  # the epsilon move  (derivative)
        Factor_prime()
        G()
        return
    else:
        handle('Term_prime', Term_prime)


def Term_zegond():
    if token_str in first['Factor_zegond']:
        Factor_zegond()
        G()
        return
    else:
        handle('Term_zegond', Term_zegond)


def G():
    if token_str == '*':
        match('*')
        Factor()
        G()
        return
    elif token_str in follow['G']:  # the epsilon move
        return
    else:
        handle('G', G)


def Factor():
    if token_str == '(':
        match('(')
        Expression()
        match(')')
        return
    elif token_str == "ID":
        match('ID')
        Var_call_prime()
        return
    elif token_str == 'NUM':
        match('NUM')
        return
    else:
        handle('Factor', Factor)


def Var_call_prime():
    if token_str == '(':
        match('(')
        Args()
        match(')')
        return
    elif token_str in (first['Var_prime'] + follow['Var_call_prime']):  # the epsilon move  (derivative)
        Var_prime()
        return
    else:
        handle('Var_call_prime', Var_call_prime)


def Var_prime():
    if token_str == '[':
        match('[')
        Expression()
        match(']')
        return
    elif token_str in follow['Var_prime']:  # the epsilon move
        return
    else:
        handle('Var_prime', Var_prime)


def Factor_prime():
    if token_str == '(':
        match('(')
        Args()
        match(')')
        return
    elif token_str in follow['Factor_prime']:  # the epsilon move
        return
    else:
        handle('Factor_prime', Factor_prime)


def Factor_zegond():
    if token_str == '(':
        match('(')
        Expression()
        match(')')
        return
    elif token_str == 'NUM':
        match('NUM')
        return
    else:
        handle('Factor_zegond', Factor_zegond)


def Args():
    if token_str in first['Arg_list']:
        Arg_list()
        return
    elif token_str in follow['Args']:  # the epsilon move
        return
    else:
        handle('Args', Args)


def Arg_list():
    if token_str in first['Expression']:
        Expression()
        Arg_list_prime()
        return
    else:
        handle('Arg_list', Arg_list)


def Arg_list_prime():
    if token_str == ',':
        match(',')
        Expression()
        Arg_list_prime()
        return
    elif token_str in follow['Arg_list_prime']:  # the epsilon move
        return
    else:
        handle('Arg_list_prime', Arg_list_prime)
