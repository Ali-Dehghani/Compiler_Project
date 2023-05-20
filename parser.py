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
state = '0'
halt_program = False
get_new_token = True

stack = ['']


def match(input):
    return


def error_handler(error_type, missing):
    if error_type == 1:
        f_errors.write(f'(#{scanner.get_current_line()} : syntax error, illegal {token_str}\n)')
    elif error_type == 2:
        f_errors.write(f'(#{scanner.get_current_line()} : syntax error, missing {missing}\n)')
    elif error_type == 3:
        f_errors.write(f'(#{scanner.get_current_line()} : syntax error, missing {missing}\n)')


def parse():
    global terminals, non_terminals, first, follow, token, get_new_token, token_str
    if get_new_token:
        token = scanner.get_next_token()
    if token[0] in ['KEYWORD', 'SYMBOL']:
        token_str = token[1]
    else:
        token_str = token[0]


def Expression():
    return


def B():
    return


def H():
    global token_str
    if token_str == '=':
        match('=')
        Expression()
        return
    elif token_str in (first['G'] + first['D'] + first['C']):
        G()
        D()
        C()
        return
    else:   # the epsilon move (derivative)
        return


def Simple_expression_zegond():
    if token_str in first['Additive_expression_zegond']:
        Additive_expression_zegond()
        C()
        return
    elif token_str in follow['Simple_expression_zegond']:
        # dzf


def Simple_expression_prime():
    if token_str in (first['Additive_expression_prime'] + first['C']):
        Additive_expression_prime()
        C()
        return
    else:   # the epsilon move  (derivative)
        return


def C():
    if token_str in first['Relop']:
        Relop()
        Additive_expression()
        return
    else:   # the epsilon move
        return


def Relop():
    if token_str == '<':
        match('<')
        return
    elif token_str == '==':
        match('==')
        return
    # else panic mode


def Additive_expression():
    if token_str in first['Term']:
        Term()
        D()
        return
    # else panic mode


def Additive_expression_prime():
    if token_str in (first['Term_prime'] + first['D']):
        Term_prime()
        D()
        return
    else:   # the epsilon move  (derivative)
        return


def Additive_expression_zegond():
    if token_str in first['Term_zegond']:
        Term_zegond()
        D()
        return
    # else panic mode


def D():
    if token_str in first['Addop']:
        Addop()
        Term()
        D()
        return
    else:   # the epsilon move
        return


def Addop():
    if token_str == '+':
        match('+')
        return
    elif token_str == '-':
        match('-')
        return
    # else panic mode


def Term():
    if token_str in first['Factor']:
        Factor()
        G()
        return
    # else panic mode


def Term_prime():
    if token_str in (first['Factor_prime'] + first['G']):
        Factor_prime()
        G()
        return
    else:   # the epsilon move  (derivative)
        return


def Term_zegond():
    if token_str in first['Factor_zegond']:
        Factor_zegond()
        G()
        return
    # else panic mode


def G():
    if token_str == '*':
        match('*')
        Factor()
        G()
        return
    else:   # the epsilon move
        return


def Factor():
    if token_str == '(':
        match('(')
        Expression()
        match(')')
        return
    elif token_str == 'ID':
        match('ID')
        Var_call_prime()
        return
    elif token_str == 'NUM':
        match('NUM')
        return
    # panic mode


def Var_call_prime():
    if token_str == '(':
        match('(')
        Args()
        match(')')
        return
    elif token_str in first['Var_prime']:
        Var_prime()
        return
    else:   # the epsilon move  (derivative)
        return


def Var_prime():
    if token_str == '[':
        match('[')
        Expression()
        match(']')
        return
    else:   # the epsilon move
        return


def Factor_prime():
    if token_str == '(':
        match('(')
        Args()
        match(')')
        return
    else:   # the epsilon move
        return


def Factor_zegond():
    if token_str == '(':
        match('(')
        Expression()
        match(')')
        return
    elif token_str == 'NUM':
        match('NUM')
        return
    # panic


def Args():
    if token_str in first['Arg_list']:
        Arg_list()
        return
    else:   # the epsilon move
        return


def Arg_list():
    if token_str in first['Expression']:
        Expression()
        Arg_list_prime()
        return
    # panic


def Arg_list_prime():
    if token_str == ',':
        match(',')
        Expression()
        Arg_list_prime()
        return
    else:   # the epsilon move
        return
