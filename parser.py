import scanner
import json
from anytree import Node, RenderTree

f_json = open('First-Follow.json')
data = json.load(f_json)
f_json.close()

first = data['first']
follow = data['follow']
f_errors = open("syntax_errors.txt", "w")
f_parse_tree = open("parse_tree.txt", "w", encoding='utf-8')
token = ''
token_str = ''
is_there_any_error = False

stack = []


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
    if match_input == '$':
        Node('$', stack[0])
    elif match_input == 'epsilon':
        Node('epsilon', parent=stack[-1])
    elif match_input == token_str:  # token is parsed
        Node("(%s, %s)" % (token[0], token[1]), parent=stack[-1])
        get_next_token()
    else:
        error_handler(3, match_input)


def kill_program():  # unexpected EOF
    for pre, fill, node in RenderTree(stack[0]):
        print("%s%s" % (pre, node.name), file=f_parse_tree)
    f_parse_tree.close()
    quit()


def handle(non_terminal_str, non_terminal_func):
    if token_str not in follow[non_terminal_str]:
        if token_str == '$':
            error_handler(4, '')
            kill_program()
        else:
            error_handler(1, token_str)
            get_next_token()
            non_terminal_func()
    elif token_str in follow[non_terminal_str]:
        error_handler(2, non_terminal_str)


def error_handler(error_type, error_input):
    global is_there_any_error
    is_there_any_error = True
    if error_type == 1:
        f_errors.write(f'#{scanner.get_current_line()} : syntax error, illegal {error_input}\n')
    elif error_type == 2:
        f_errors.write(f'#{scanner.get_current_line()} : syntax error, missing {error_input}\n')
    elif error_type == 3:
        f_errors.write(f'#{scanner.get_current_line()} : syntax error, missing {error_input}\n')
    elif error_type == 4:
        f_errors.write(f'#{scanner.get_current_line()} : syntax error, Unexpected EOF\n')


def parse():
    global first, follow, token, token_str, is_there_any_error, stack
    get_next_token()
    Program()
    for pre, fill, node in RenderTree(stack[0]):
        print("%s%s" % (pre, node.name), file=f_parse_tree)
    f_parse_tree.close()
    if not is_there_any_error:
        f_errors.write(f'There is no syntax error.')
    f_errors.close()


def Program():
    stack.append(Node('Program', parent=None))
    if token_str == '$':
        match('$')
        return  # end of program
    elif token_str in (first['Declaration_list'] + follow['Program']):  # epsilon move (derivative)
        Declaration_list()
    else:  # error
        handle('Program', Program)


def Declaration_list():
    stack.append(Node('Declaration_list', parent=stack[-1]))
    if token_str in first['Declaration']:
        Declaration()
        Declaration_list()
        stack.pop()
    elif token_str in follow['Declaration_list']:  # epsilon move
        if token_str == '$':
            match('$')
            stack.pop()
            return  # end of program
        match('epsilon')
        stack.pop()
        return
    else:  # error
        stack.pop()
        handle('Declaration_list', Declaration_list)


def Declaration():
    stack.append(Node('Declaration', parent=stack[-1]))
    if token_str in first['Declaration_initial']:
        Declaration_initial()
        Declaration_prime()
        stack.pop()
    else:  # error
        stack.pop()
        handle('Declaration', Declaration)


def Declaration_initial():
    stack.append(Node('Declaration_initial', parent=stack[-1]))
    if token_str in first['Type_specifier']:
        Type_specifier()
        match('ID')
        stack.pop()
    else:  # error
        stack.pop()
        handle('Declaration_initial', Declaration_initial)


def Declaration_prime():
    stack.append(Node('Declaration_prime', parent=stack[-1]))
    if token_str in first['Fun_declaration_prime']:
        Fun_declaration_prime()
        stack.pop()
    elif token_str in first['Var_declaration_prime']:
        Var_declaration_prime()
        stack.pop()
    else:  # error
        stack.pop()
        handle('Declaration_prime', Declaration_prime)


def Var_declaration_prime():
    stack.append(Node('Var_declaration_prime', parent=stack[-1]))
    if token_str == '[':
        match('[')
        match('NUM')
        match(']')
        match(';')
        stack.pop()
    elif token_str == ';':
        match(';')
        stack.pop()
    else:  # error
        stack.pop()
        handle('Var_declaration_prime', Var_declaration_prime)


def Fun_declaration_prime():
    stack.append(Node('Fun_declaration_prime', parent=stack[-1]))
    if token_str == '(':
        match('(')
        Params()
        match(')')
        Compound_stmt()
        stack.pop()
    else:  # error
        stack.pop()
        handle('Fun_declaration_prime', Fun_declaration_prime)


def Type_specifier():
    stack.append(Node('Type_specifier', parent=stack[-1]))
    if token_str == 'int':
        match('int')
        stack.pop()
    elif token_str == 'void':
        match('void')
        stack.pop()
    else:  # error
        stack.pop()
        handle('Type_specifier', Type_specifier)


def Params():
    stack.append(Node('Params', parent=stack[-1]))
    if token_str == 'int':
        match('int')
        match('ID')
        Param_prime()
        Param_list()
        stack.pop()
    elif token_str == 'void':
        match('void')
        stack.pop()
    else:  # error
        stack.pop()
        handle('Params', Params)


def Param_list():
    stack.append(Node('Param_list', parent=stack[-1]))
    if token_str == ',':
        match(',')
        Param()
        Param_list()
        stack.pop()
    elif token_str in follow["Param_list"]:  # epsilon move
        match('epsilon')
        stack.pop()
        return
    else:  # error
        stack.pop()
        handle('Param_list', Param_list)


def Param():
    stack.append(Node('Param', parent=stack[-1]))
    if token_str in first['Declaration_initial']:
        Declaration_initial()
        Param_prime()
        stack.pop()
    else:  # error
        stack.pop()
        handle('Param', Param)


def Param_prime():
    stack.append(Node('Param_prime', parent=stack[-1]))
    if token_str == '[':
        match('[')
        match(']')
        stack.pop()
    elif token_str in follow['Param_prime']:  # epsilon move
        match('epsilon')
        stack.pop()
        return
    else:  # error
        stack.pop()
        handle('Param_prime', Param_prime)


def Compound_stmt():
    stack.append(Node('Compound_stmt', parent=stack[-1]))
    if token_str == '{':
        match('{')
        Declaration_list()
        Statement_list()
        match('}')
        stack.pop()
    else:  # error
        stack.pop()
        handle('Compound_stmt', Compound_stmt)


def Statement_list():
    stack.append(Node('Statement_list', parent=stack[-1]))
    if token_str in first['Statement']:
        Statement()
        Statement_list()
        stack.pop()
    elif token_str in follow['Statement_list']:  # epsilon move
        match('epsilon')
        stack.pop()
        return
    else:  # error
        stack.pop()
        handle('Statement_list', Statement_list)


def Statement():
    stack.append(Node('Statement', parent=stack[-1]))
    if token_str in first['Expression_stmt']:
        Expression_stmt()
        stack.pop()
    elif token_str in first['Compound_stmt']:
        Compound_stmt()
        stack.pop()
    elif token_str in first['Selection_stmt']:
        Selection_stmt()
        stack.pop()
    elif token_str in first['Iteration_stmt']:
        Iteration_stmt()
        stack.pop()
    elif token_str in first['Return_stmt']:
        Return_stmt()
        stack.pop()
    else:  # error
        stack.pop()
        handle('Statement', Statement)


def Expression_stmt():
    stack.append(Node('Expression_stmt', parent=stack[-1]))
    if token_str in first['Expression']:
        Expression()
        match(';')
        stack.pop()
    elif token_str == 'break':
        match('break')
        match(';')
        stack.pop()
    elif token_str == ';':
        match(';')
        stack.pop()
    else:  # error
        stack.pop()
        handle('Expression_stmt', Expression_stmt)


def Selection_stmt():
    stack.append(Node('Selection_stmt', parent=stack[-1]))
    if token_str == 'if':
        match('if')
        match('(')
        Expression()
        match(')')
        Statement()
        match('else')
        Statement()
        stack.pop()
    else:  # error
        stack.pop()
        handle('Selection_stmt', Selection_stmt)


def Iteration_stmt():
    stack.append(Node('Iteration_stmt', parent=stack[-1]))
    if token_str == 'repeat':
        match('repeat')
        Statement()
        match('until')
        match('(')
        Expression()
        match(')')
        stack.pop()
    else:  # error
        stack.pop()
        handle('Iteration_stmt', Iteration_stmt)


def Return_stmt():
    stack.append(Node('Return_stmt', parent=stack[-1]))
    if token_str == 'return':
        match('return')
        Return_stmt_prime()
        stack.pop()
    else:  # error
        stack.pop()
        handle('Return_stmt', Return_stmt)


def Return_stmt_prime():
    stack.append(Node('Return_stmt_prime', parent=stack[-1]))
    if token_str == ';':
        match(';')
        stack.pop()
    elif token_str in first['Expression']:
        Expression()
        match(';')
        stack.pop()
    else:  # error
        stack.pop()
        handle('Return_stmt_prime', Return_stmt_prime)


def Expression():
    stack.append(Node('Expression', parent=stack[-1]))
    if token_str in first['Simple_expression_zegond']:
        Simple_expression_zegond()
        stack.pop()
    elif token_str == "ID":
        match('ID')
        B()
        stack.pop()
    else:  # error
        stack.pop()
        handle('Expression', Expression)


def B():
    stack.append(Node('B', parent=stack[-1]))
    if token_str == '=':
        match('=')
        Expression()
        stack.pop()
    elif token_str == '[':
        match('[')
        Expression()
        match(']')
        H()
        stack.pop()
    elif token_str in (first['Simple_expression_prime'] + follow['B']):  # epsilon move (derivative)
        Simple_expression_prime()
        stack.pop()
    else:  # error
        stack.pop()
        handle('B', B)


def H():
    stack.append(Node('H', parent=stack[-1]))
    if token_str == '=':
        match('=')
        Expression()
        stack.pop()
        return
    elif token_str in (first['G'] + first['D'] + first['C'] + follow['H']):  # the epsilon move (derivative)
        G()
        D()
        C()
        stack.pop()
        return
    else:  # error
        stack.pop()
        handle('H', H())


def Simple_expression_zegond():
    stack.append(Node('Simple_expression_zegond', parent=stack[-1]))
    if token_str in first['Additive_expression_zegond']:
        Additive_expression_zegond()
        C()
        stack.pop()
        return
    else:  # error
        stack.pop()
        handle('Simple_expression_zegond', Simple_expression_zegond())


def Simple_expression_prime():
    stack.append(Node('Simple_expression_prime', parent=stack[-1]))
    if token_str in (first['Additive_expression_prime'] + first['C'] + follow['Simple_expression_prime']):
        Additive_expression_prime()
        C()
        stack.pop()
        return
    else:
        stack.pop()
        handle('Simple_expression_prime', Simple_expression_prime)


def C():
    stack.append(Node('C', parent=stack[-1]))
    if token_str in first['Relop']:
        Relop()
        Additive_expression()
        stack.pop()
        return
    elif token_str in follow['C']:  # the epsilon move
        match('epsilon')
        stack.pop()
        return
    else:
        stack.pop()
        handle('C', C)


def Relop():
    stack.append(Node('Relop', parent=stack[-1]))
    if token_str == '<':
        match('<')
        stack.pop()
        return
    elif token_str == '==':
        match('==')
        stack.pop()
        return
    else:
        stack.pop()
        handle('Relop', Relop)


def Additive_expression():
    stack.append(Node('Additive_expression', parent=stack[-1]))
    if token_str in first['Term']:
        Term()
        D()
        stack.pop()
        return
    else:
        stack.pop()
        handle('Additive_expression', Additive_expression)


def Additive_expression_prime():
    stack.append(Node('Additive_expression_prime', parent=stack[-1]))
    if token_str in (first['Term_prime'] + first['D'] + follow['Additive_expression_prime']):  # epsilon move derivative
        Term_prime()
        D()
        stack.pop()
        return
    else:
        stack.pop()
        handle('Additive_expression_prime', Additive_expression_prime)


def Additive_expression_zegond():
    stack.append(Node('Additive_expression_zegond', parent=stack[-1]))
    if token_str in first['Term_zegond']:
        Term_zegond()
        D()
        stack.pop()
        return
    else:
        stack.pop()
        handle('Additive_expression_zegond', Additive_expression_zegond)


def D():
    stack.append(Node('D', parent=stack[-1]))
    if token_str in first['Addop']:
        Addop()
        Term()
        D()
        stack.pop()
        return
    elif token_str in follow['D']:  # the epsilon move
        match('epsilon')
        stack.pop()
        return
    else:
        stack.pop()
        handle('D', D)


def Addop():
    stack.append(Node('Addop', parent=stack[-1]))
    if token_str == '+':
        match('+')
        stack.pop()
        return
    elif token_str == '-':
        match('-')
        stack.pop()
        return
    else:
        stack.pop()
        handle('Addop', Addop)


def Term():
    stack.append(Node('Term', parent=stack[-1]))
    if token_str in first['Factor']:
        Factor()
        G()
        stack.pop()
        return
    else:
        stack.pop()
        handle('Term', Term)


def Term_prime():
    stack.append(Node('Term_prime', parent=stack[-1]))
    if token_str in (first['Factor_prime'] + first['G'] + follow['Term_prime']):  # the epsilon move  (derivative)
        Factor_prime()
        G()
        stack.pop()
        return
    else:
        stack.pop()
        handle('Term_prime', Term_prime)


def Term_zegond():
    stack.append(Node('Term_zegond', parent=stack[-1]))
    if token_str in first['Factor_zegond']:
        Factor_zegond()
        G()
        stack.pop()
        return
    else:
        stack.pop()
        handle('Term_zegond', Term_zegond)


def G():
    stack.append(Node('G', parent=stack[-1]))
    if token_str == '*':
        match('*')
        Factor()
        G()
        stack.pop()
        return
    elif token_str in follow['G']:  # the epsilon move
        match('epsilon')
        stack.pop()
        return
    else:
        stack.pop()
        handle('G', G)


def Factor():
    stack.append(Node('Factor', parent=stack[-1]))
    if token_str == '(':
        match('(')
        Expression()
        match(')')
        stack.pop()
        return
    elif token_str == "ID":
        match('ID')
        Var_call_prime()
        stack.pop()
        return
    elif token_str == 'NUM':
        match('NUM')
        stack.pop()
        return
    else:
        stack.pop()
        handle('Factor', Factor)


def Var_call_prime():
    stack.append(Node('Var_call_prime', parent=stack[-1]))
    if token_str == '(':
        match('(')
        Args()
        match(')')
        stack.pop()
        return
    elif token_str in (first['Var_prime'] + follow['Var_call_prime']):  # the epsilon move  (derivative)
        Var_prime()
        stack.pop()
        return
    else:
        stack.pop()
        handle('Var_call_prime', Var_call_prime)


def Var_prime():
    stack.append(Node('Var_prime', parent=stack[-1]))
    if token_str == '[':
        match('[')
        Expression()
        match(']')
        stack.pop()
        return
    elif token_str in follow['Var_prime']:  # the epsilon move
        match('epsilon')
        stack.pop()
        return
    else:
        stack.pop()
        handle('Var_prime', Var_prime)


def Factor_prime():
    stack.append(Node('Factor_prime', parent=stack[-1]))
    if token_str == '(':
        match('(')
        Args()
        match(')')
        stack.pop()
        return
    elif token_str in follow['Factor_prime']:  # the epsilon move
        match('epsilon')
        stack.pop()
        return
    else:
        stack.pop()
        handle('Factor_prime', Factor_prime)


def Factor_zegond():
    stack.append(Node('Factor_zegond', parent=stack[-1]))
    if token_str == '(':
        match('(')
        Expression()
        match(')')
        stack.pop()
        return
    elif token_str == 'NUM':
        match('NUM')
        stack.pop()
        return
    else:
        stack.pop()
        handle('Factor_zegond', Factor_zegond)


def Args():
    stack.append(Node('Args', parent=stack[-1]))
    if token_str in first['Arg_list']:
        Arg_list()
        stack.pop()
        return
    elif token_str in follow['Args']:  # the epsilon move
        match('epsilon')
        stack.pop()
        return
    else:
        stack.pop()
        handle('Args', Args)


def Arg_list():
    stack.append(Node('Arg_list', parent=stack[-1]))
    if token_str in first['Expression']:
        Expression()
        Arg_list_prime()
        stack.pop()
        return
    else:
        stack.pop()
        handle('Arg_list', Arg_list)


def Arg_list_prime():
    stack.append(Node('Arg_list_prime', parent=stack[-1]))
    if token_str == ',':
        match(',')
        Expression()
        Arg_list_prime()
        stack.pop()
        return
    elif token_str in follow['Arg_list_prime']:  # the epsilon move
        match('epsilon')
        stack.pop()
        return
    else:
        stack.pop()
        handle('Arg_list_prime', Arg_list_prime)
