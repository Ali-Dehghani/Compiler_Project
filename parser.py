import scanner
import json

f_json = open('data.json')
data = json.load(f_json)
f_json.close()

terminals = data['terminals']
non_terminals = data['non-terminal']
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
    print(token)
    if token[0] in ['KEYWORD', 'SYMBOL']:
        token_str = token[1]
    else:
        token_str = token[0]
    return


def match(input):
    global token_str
    if input == token_str:
        get_next_token()
    else:
        error_handler(3, input)


def error_handler(error_type, input):
    global is_there_any_error
    is_there_any_error = True
    if error_type == 1:
        f_errors.write(f'(#{scanner.get_current_line()} : syntax error, illegal {input})\n')
        get_next_token()
    elif error_type == 2:
        f_errors.write(f'(#{scanner.get_current_line()} : syntax error, missing {input})\n')
    elif error_type == 3:
        f_errors.write(f'(#{scanner.get_current_line()} : syntax error, missing {input})\n')


def parse():
    global terminals, non_terminals, first, follow, token, token_str, is_there_any_error
    get_next_token()
    Program()
    if not is_there_any_error:
        f_errors.write(f'There is no syntax error.')
    f_errors.close()


def handle(non_terminal_str, non_terminal_func):
    if token_str not in follow[non_terminal_str]:
        error_handler(1, token_str)
        non_terminal_func()
    else:
        error_handler(2, non_terminal_str)


def Program():
    if token_str in first["Declaration-list"]:
        Declaration_list()
    else:
        # error
        handle("Program", Program)


def Declaration_list():
    if token_str in first["Declaration"]:
        Declaration()
        Declaration_list()
    elif token_str in follow["Declaration-list"]:  # for epsilon
        pass
    else:
        # error
        handle("Declaration-list", Declaration_list)


def Declaration():
    if token_str in first["Declaration-initial"]:
        Declaration_initial()
        Declaration_prime()
    else:
        # error
        handle("Declaration", Declaration)


def Declaration_initial():
    if token_str in first["Type-specifier"]:
        Type_specifier()
        match("ID")
    else:
        # error
        handle("Declaration-initial", Declaration_initial)


def Declaration_prime():
    if token_str in first["Fun-declaration-prime"]:
        Fun_declaration_prime()
    elif token_str in first["Var-declaration-prime"]:
        Var_declaration_prime()
    else:
        # error
        handle("Declaration-prime", Declaration_prime)


def Var_declaration_prime():
    if token_str == "[":
        match("[")
        match("NUM")
        match("]")
        match(";")
    elif token_str == ";":
        match(";")
    else:
        # error
        handle("Var-declaration-prime", Var_declaration_prime)


def Fun_declaration_prime():
    if token_str == "(":
        match("(")
        Params()
        match(")")
        Compound_stmt()
    else:
        # error
        handle("Fun-declaration-prime", Fun_declaration_prime)


def Type_specifier():
    if token_str == "int":
        match("int")
    elif token_str == "void":
        match("void")
    else:
        # error
        handle("Type-specifier", Type_specifier)


def Params():
    if token_str == "int":
        match("int")
        match("ID")
        Param_prime()
        Param_list()
    elif token_str == "void":
        match("void")
    else:
        # error
        handle("Params", Params)


def Param_list():
    if token_str == ",":
        match(",")
        Param()
        Param_list()
    elif token_str in follow["Param-list"]:
        pass
    else:
        # error
        handle("Param-list", Param_list)


def Param():
    if token_str in first["Declaration-initial"]:
        Declaration_initial()
        Param_prime()
    else:
        # error
        handle("Param", Param)


def Param_prime():
    if token_str == "[":
        match("[")
        match("]")
    elif token_str in follow["Param-prime"]:  # for epsilon
        pass
    else:
        # error
        handle("Params-prime", Param_prime)


def Compound_stmt():
    if token_str == "{":
        match("{")
        Declaration_list()
        Statement_list()
        match("}")
    else:
        # error
        handle("Compound-stmt", Compound_stmt)


def Statement_list():
    if token_str in first["Statement"]:
        Statement()
        Statement_list()
    elif token_str in follow["Statement-list"]:  # for epsilon
        pass
    else:
        # error
        handle("Statement-list", Statement_list)


def Statement():
    if token_str in first["Expression-stmt"]:
        Expression_stmt()
    elif token_str in first["Compound-stmt"]:
        Compound_stmt()
    elif token_str in first["Selection-stmt"]:
        Selection_stmt()
    elif token_str in first["Iteration-stmt"]:
        Iteration_stmt()
    elif token_str in first["Return-stmt"]:
        Return_stmt()
    else:
        # error
        handle("Statement", Statement)


def Expression_stmt():
    if token_str in first["Expression"]:
        Expression()
        match(";")
    elif token_str == "break":
        match("break")
        match(";")
    elif token_str == ";":
        match(";")
    else:
        # error
        handle("Expression-stmt", Expression_stmt)


def Selection_stmt():
    if token_str == "if":
        match("if")
        match("(")
        Expression()
        match(")")
        Statement()
        match("else")
        Statement()
    else:
        # error
        handle("Selection-stmt", Selection_stmt)


def Iteration_stmt():
    if token_str == "repeat":
        match("repeat")
        Statement()
        match("until")
        match("(")
        Expression()
        match(")")
    else:
        # error
        handle("Iteration-stmt", Iteration_stmt)


def Return_stmt():
    if token_str == "return":
        match("return")
        Return_stmt_prime()
    else:
        # error
        handle("Return-stmt", Return_stmt)


def Return_stmt_prime():
    if token_str == ";":
        match(";")
    elif token_str in first["Expression"]:
        Expression()
        match(";")
    else:
        # error
        handle("Return-stmt-prime", Return_stmt_prime)


def Expression():
    if token_str in first["Simple-expression-zegond"]:
        Simple_expression_zegond()
    elif token_str == "ID":
        match("ID")
        B()
    else:
        # error
        handle("Expression", Expression)


def B():
    if token_str == '=':
        match("=")
        Expression()
    elif token_str == '[':
        match("[")
        Expression()
        match("]")
        H()
    elif token_str in first["Simple-expression-prime"]:
        Simple_expression_prime()
    else:
        # error
        handle("B", B)


def H():
    global token_str
    if token_str == '=':
        match('=')
        Expression()
        return
    elif token_str in first['G']:
        G()
        D()
        C()
        return
    else:  # the epsilon move (derivative)
        handle("H", H)


def Simple_expression_zegond():
    if token_str in first['Additive-expression-zegond']:
        Additive_expression_zegond()
        C()
        return
    # elif token_str in follow['Simple_expression_zegond']:
    #     pass
    else:
        handle("Simple-expression-zegond", Simple_expression_zegond)


# dzf


def Simple_expression_prime():
    if token_str in (first['Additive-expression-prime']):
        Additive_expression_prime()
        C()
        return
    else:  # the epsilon move  (derivative)
        handle("Simple-expression-prime", Simple_expression_prime)


def C():
    if token_str in first['Relop']:
        Relop()
        Additive_expression()
        return
    elif token_str in follow["C"]:  # the epsilon move
        pass

    else:
        handle("C", C)


def Relop():
    if token_str == '<':
        match('<')
        return
    elif token_str == '==':
        match('==')
        return
    # else panic mode
    else:
        handle("Relop", Relop)


def Additive_expression():
    if token_str in first['Term']:
        Term()
        D()
        return
    # else panic mode
    else:
        handle("Additive-expression", Additive_expression)


def Additive_expression_prime():
    if token_str in (first['Term-prime']):
        Term_prime()
        D()
        return
    else:
        # error
        handle("Additive-expression-prime", Additive_expression_prime)


def Additive_expression_zegond():
    if token_str in first['Term-zegond']:
        Term_zegond()
        D()
        return
    # else panic mode
    else:
        handle("Additive-expression-zegond", Additive_expression_zegond)


def D():
    if token_str in first['Addop']:
        Addop()
        Term()
        D()
        return
    elif token_str in follow["D"]:  # the epsilon move
        pass
    else:
        handle("D", D)


def Addop():
    if token_str == '+':
        match('+')
        return
    elif token_str == '-':
        match('-')
        return
    # else panic mode
    else:
        handle("Addop", Addop)


def Term():
    if token_str in first['Factor']:
        Factor()
        G()
        return
    # else panic mode
    else:
        handle("Term", Term)


def Term_prime():
    if token_str in (first['Factor-prime']):
        Factor_prime()
        G()
        return
    else:  # the epsilon move  (derivative)
        handle("Term-prime", Term_prime)


def Term_zegond():
    if token_str in first['Factor-zegond']:
        Factor_zegond()
        G()
        return
    # else panic mode
    else:
        handle("Term-zegond", Term_zegond)


def G():
    if token_str == '*':
        match('*')
        Factor()
        G()
        return
    elif token_str in follow["G"]:  # the epsilon move
        pass
    else:
        handle("G", G)


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
    else:
        handle("Factor", Factor)


def Var_call_prime():
    if token_str == '(':
        match('(')
        Args()
        match(')')
        return
    elif token_str in first['Var-prime']:
        Var_prime()
        return
    else:  # the epsilon move  (derivative)
        handle("Var-call-prime", Var_call_prime)


def Var_prime():
    if token_str == '[':
        match('[')
        Expression()
        match(']')
        return
    elif token_str in follow["Var-prime"]:  # the epsilon move
        pass
    else:
        handle("Var-prime", Var_prime)


def Factor_prime():
    if token_str == '(':
        match('(')
        Args()
        match(')')
        return
    elif token_str in follow["Factor-prime"]:  # the epsilon move
        pass
    else:
        handle("Factor-prime", Factor_prime)


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
    else:
        handle("Factor-zegond", Factor_zegond)


def Args():
    if token_str in first['Arg-list']:
        Arg_list()
        return
    elif token_str in follow["Args"]:  # the epsilon move
        pass
    else:
        handle("Args", Args)


def Arg_list():
    if token_str in first['Expression']:
        Expression()
        Arg_list_prime()
        return
    # panic
    else:
        handle("Arg-list", Arg_list)


def Arg_list_prime():
    if token_str == ',':
        match(',')
        Expression()
        Arg_list_prime()
        return
    elif token_str in follow["Arg-list-prime"]:  # the epsilon move
        pass
    else:
        handle("Arg-list-prime", Arg_list_prime)
