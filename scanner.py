pointer = 0
current_token_lexeme = ""
current_line = 1
comment_line = 1
symbol_line = 1
node = 0  # node is state number of DFA
is_comment_open = False
is_beginning = True  # if we are in the beginning of the code's line
is_beginning_error = True  # if we are in the beginning of the error text file's line
is_beginning_error_comment = True  # if comment is in the beginning of the code's line
no_error = True
keywords = ["if", "else", "void", "int", "repeat", "break", "until", "return"]
identifiers = []
symbols = [';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '*', '=', '<', '==', '/']
whitespaces = [' ', '\n', '\r', '\t', '\v', '\f']
valid_inputs = symbols + whitespaces + ['=', '*', '/']

f_input = open("input.txt", "r")
f_tokens = open("tokens.txt", "w")
f_errors = open("lexical_errors.txt", "w")
f_symbols = open("symbol_table.txt", "w")

code = f_input.read()
code += " "


def error_handler(error):
    global comment_line, current_line, current_token_lexeme, is_beginning_error, is_beginning_error_comment, no_error
    # errors:
    # 1) Invalid input
    # 2) Unclosed comment
    # 3) Unmatched comment
    # 4) Invalid number
    if error == 1:
        if is_beginning_error:
            f_errors.write(f'{current_line}.    ')
        f_errors.write(f'({current_token_lexeme}, Invalid input) ')
    elif error == 2:
        if is_beginning_error_comment:
            f_errors.write(f'{comment_line}.    ')
        f_errors.write(f'({current_token_lexeme[:7]}..., Unclosed comment)')
    elif error == 3:
        if is_beginning_error:
            f_errors.write(f'{current_line}.    ')
        f_errors.write(f'(*/, Unmatched comment) ')
    elif error == 4:
        if is_beginning_error:
            f_errors.write(f'{current_line}.    ')
        f_errors.write(f'({current_token_lexeme}, Invalid number) ')
    current_token_lexeme = ""
    is_beginning_error = False
    is_beginning_error_comment = False
    no_error = False


def id_keyword():
    global symbol_line, current_line, current_token_lexeme
    if current_token_lexeme in keywords:
        token_generator("KEYWORD")
    else:
        if current_token_lexeme not in identifiers:
            identifiers.append(current_token_lexeme)
            f_symbols.write(f'{symbol_line}.    {current_token_lexeme}\n')
            symbol_line += 1
        token_generator("ID")


def token_generator(token):
    global is_beginning, current_token_lexeme
    if is_beginning:
        f_tokens.write(f"{current_line}.    ")
        is_beginning = False
    f_tokens.write(f'({token}, {current_token_lexeme}) ')


def get_next_token():
    global pointer, current_token_lexeme, current_line, comment_line, node, symbols, whitespaces, code, is_comment_open, is_beginning, is_beginning_error, is_beginning_error_comment
    if not is_comment_open and code[pointer] not in valid_inputs and not code[pointer].isalnum():
        current_token_lexeme += code[pointer]
        error_handler(1)
        pointer += 1
        node = 0
    else:
        if node == 0:
            if code[pointer].isdigit():
                current_token_lexeme += code[pointer]
                node = 1
                pointer += 1
            elif code[pointer].isalpha():
                current_token_lexeme += code[pointer]
                node = 3
                pointer += 1
            elif code[pointer] == '/':
                current_token_lexeme += code[pointer]
                node = 5
                pointer += 1
            elif code[pointer] == '=':
                current_token_lexeme += code[pointer]
                node = 11
                pointer += 1
            elif code[pointer] in symbols:
                current_token_lexeme += code[pointer]
                node = 12
            elif code[pointer] in whitespaces:
                if code[pointer] == '\n':
                    if not is_beginning:
                        f_tokens.write('\n')
                    if not is_beginning_error:
                        f_errors.write('\n')
                    current_line += 1
                    is_beginning = True
                    if is_comment_open:
                        is_beginning_error_comment = False
                    else:
                        is_beginning_error_comment = True
                    is_beginning_error = True
                node = 14
            elif code[pointer] == '*':
                current_token_lexeme += code[pointer]
                node = 15
                pointer += 1
        elif node == 1:
            if code[pointer].isdigit():
                current_token_lexeme += code[pointer]
                pointer += 1
            else:
                if code[pointer].isalpha():
                    current_token_lexeme += code[pointer]
                    error_handler(4)
                    pointer += 1
                    node = 0
                else:
                    node = 2
        elif node == 2:
            token_generator("NUM")
            current_token_lexeme = ""
            node = 0
        elif node == 3:
            if code[pointer].isalnum():
                current_token_lexeme += code[pointer]
                pointer += 1
                node = 3
            else:
                node = 4
        elif node == 4:
            id_keyword()
            current_token_lexeme = ""
            node = 0
        elif node == 5:
            if code[pointer] == '*':
                comment_line = current_line
                is_comment_open = True
                current_token_lexeme += code[pointer]
                pointer += 1
                node = 6
            elif code[pointer] == '/':
                is_comment_open = True
                current_token_lexeme += code[pointer]
                pointer += 1
                node = 9
            else:
                node = 13
        elif node == 6:
            if code[pointer] == '*':
                current_token_lexeme += code[pointer]
                pointer += 1
                node = 7
            else:
                if code[pointer] == '\n':
                    current_line += 1
                current_token_lexeme += code[pointer]
                pointer += 1
                node = 6
        elif node == 7:
            if code[pointer] == '/':
                is_comment_open = False
                current_token_lexeme += code[pointer]
                pointer += 1
                node = 8
            else:
                current_token_lexeme += code[pointer]
                pointer += 1
                node = 6
        elif node == 8:
            current_token_lexeme = ""
            node = 0
        elif node == 9:
            if code[pointer] == '\n' or pointer == len(code):
                is_comment_open = False
                node = 10
            else:
                current_token_lexeme += code[pointer]
                pointer += 1
                node = 9
        elif node == 10:
            current_token_lexeme = ""
            node = 0
        elif node == 11:
            if code[pointer] == '=':
                current_token_lexeme += code[pointer]
                node = 12
            else:
                node = 13
        elif node == 12:
            token_generator("SYMBOL")
            current_token_lexeme = ""
            pointer += 1
            node = 0
        elif node == 13:
            token_generator("SYMBOL")
            current_token_lexeme = ""
            node = 0
        elif node == 14:
            current_token_lexeme = ""
            pointer += 1
            node = 0
        elif node == 15:
            if code[pointer] == '/':
                pointer += 1
                error_handler(3)
                node = 0
            else:
                node = 13


def scan():
    global f_symbols, symbol_line, pointer, code, keywords, is_comment_open
    for key in keywords:
        f_symbols.write(f'{symbol_line}.    {key}\n')
        symbol_line += 1
    while pointer < len(code):
        get_next_token()
    if is_comment_open:
        error_handler(2)
    if no_error:
        f_errors.write("There is no lexical error.")
