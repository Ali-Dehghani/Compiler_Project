pointer = 0
current_token_lexeme = ""
current_line = 1
comment_line = 1
symbol_line = 1  # symbol table file' line
state = 0

is_comment_open = False
in_beginning = True  # if we are in the beginning of the token text file's line
in_beginning_error = True  # if we are in the beginning of the error text file's line
in_beginning_error_comment = True  # if unmatched comment is in the beginning of the code's line
no_error = True

keywords = ["break", "else", "if", "int", "repeat", "return", "until", "void"]
identifiers = []
symbols = [';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '*', '=', '<', '==']
whitespaces = [' ', '\n', '\r', '\t', '\v', '\f']
valid_symbols = symbols + whitespaces + ['/']

f_input = open("input.txt", "r")
f_tokens = open("tokens.txt", "w")
f_errors = open("lexical_errors.txt", "w")
f_symbols = open("symbol_table.txt", "w")

code = f_input.read()
code += " "

# new variables added for parser
is_token_generated = False
generating_token = ['', '']


def error_handler(error):
    global comment_line, current_line, current_token_lexeme, in_beginning_error, in_beginning_error_comment, no_error
    # errors:
    if error == 1:  # 1) Invalid input
        if in_beginning_error:
            f_errors.write(f'{current_line}.\t')
        f_errors.write(f'({current_token_lexeme}, Invalid input) ')
    elif error == 2:  # 2) Unclosed comment
        if in_beginning_error_comment:
            f_errors.write(f'{comment_line}.\t')
        f_errors.write(f'({current_token_lexeme[:7]}..., Unclosed comment)')
    elif error == 3:  # 3) Unmatched comment
        if in_beginning_error:
            f_errors.write(f'{current_line}.\t')
        f_errors.write(f'(*/, Unmatched comment) ')
    elif error == 4:  # 4) Invalid number
        if in_beginning_error:
            f_errors.write(f'{current_line}.\t')
        f_errors.write(f'({current_token_lexeme}, Invalid number) ')

    current_token_lexeme = ""
    in_beginning_error = False
    in_beginning_error_comment = False
    no_error = False


def id_keyword():
    global symbol_line, current_line, current_token_lexeme
    if current_token_lexeme in keywords:
        token_generator("KEYWORD")
    else:
        if current_token_lexeme not in identifiers:
            identifiers.append(current_token_lexeme)
            f_symbols.write(f'{symbol_line}.\t{current_token_lexeme}\n')
            symbol_line += 1
        token_generator("ID")


def token_generator(token):
    global in_beginning, current_token_lexeme
    if in_beginning:
        f_tokens.write(f"{current_line}.\t")
        in_beginning = False
    f_tokens.write(f'({token}, {current_token_lexeme}) ')

    # new
    is_token_generated = True
    generating_token = [token, current_token_lexeme]


def get_next_token():
    global pointer, current_token_lexeme, current_line, comment_line, state, symbols, whitespaces, code, is_comment_open, in_beginning, in_beginning_error, in_beginning_error_comment, is_token_generated, is_token_generated, is_token_generated

    if pointer == len(code):
        if is_comment_open:
            error_handler(2)
        if no_error:
            f_errors.write("There is no lexical error.")
        return ['$', '$']

    if (not is_comment_open) and (code[pointer] not in valid_symbols) and (not code[pointer].isalnum()):
        current_token_lexeme += code[pointer]
        error_handler(1)
        pointer += 1
        state = 0
    else:
        if state == 0:  # finding the path ahead
            if code[pointer].isdigit():
                current_token_lexeme += code[pointer]
                state = 1
                pointer += 1
            elif code[pointer].isalpha():
                current_token_lexeme += code[pointer]
                state = 3
                pointer += 1
            elif code[pointer] == '/':
                current_token_lexeme += code[pointer]
                state = 5
                pointer += 1
            elif code[pointer] == '=':
                current_token_lexeme += code[pointer]
                state = 9
                pointer += 1
            elif code[pointer] == '*':
                current_token_lexeme += code[pointer]
                state = 13
                pointer += 1
            elif code[pointer] in symbols:
                current_token_lexeme += code[pointer]
                state = 10
            elif code[pointer] in whitespaces:
                if code[pointer] == '\n':
                    if not in_beginning:
                        f_tokens.write('\n')
                    if not in_beginning_error:
                        f_errors.write('\n')
                    current_line += 1
                    in_beginning = True
                    if is_comment_open:
                        in_beginning_error_comment = False
                    else:
                        in_beginning_error_comment = True
                    in_beginning_error = True
                state = 12

        elif state == 1:  # finding numbers
            if code[pointer].isdigit():  # is still a number
                current_token_lexeme += code[pointer]
                pointer += 1
            else:
                if code[pointer].isalpha():  # is no longer a number
                    current_token_lexeme += code[pointer]
                    error_handler(4)
                    pointer += 1
                    state = 0
                else:
                    state = 2
        elif state == 2:  # finalized Numbers
            token_generator("NUM")
            current_token_lexeme = ""
            state = 0
        elif state == 3:  # finding ID/Keywords
            if code[pointer].isalnum():
                current_token_lexeme += code[pointer]
                pointer += 1
                state = 3
            else:
                state = 4
        elif state == 4:  # finalized ID/Keywords
            id_keyword()
            current_token_lexeme = ""
            state = 0
        elif state == 5:  # finding Comments
            if code[pointer] == '*':
                comment_line = current_line
                is_comment_open = True
                current_token_lexeme += code[pointer]
                pointer += 1
                state = 6
            else:
                error_handler(1)
                current_token_lexeme = ""
                state = 0
        elif state == 6:  # checking if the comment is ending (first part)
            if code[pointer] == '*':  # comment could be ending
                current_token_lexeme += code[pointer]
                pointer += 1
                state = 7
            else:
                if code[pointer] == '\n':  # comment did not end
                    current_line += 1
                current_token_lexeme += code[pointer]
                pointer += 1
                state = 6
        elif state == 7:  # checking if the comment is ending (second part)
            if code[pointer] == '/':  # comment did end
                is_comment_open = False
                current_token_lexeme += code[pointer]
                pointer += 1
                state = 8
            else:  # comment did not end
                current_token_lexeme += code[pointer]
                pointer += 1
                state = 6
        elif state == 8:  # clean up after comment ending
            current_token_lexeme = ""
            state = 0
        elif state == 9:  # '=' and '==' differentiation
            if code[pointer] == '=':
                current_token_lexeme += code[pointer]
                state = 10
            else:
                state = 11
        elif state == 10:  # finding '==' and other symbols (except '=' and '*')
            token_generator("SYMBOL")
            current_token_lexeme = ""
            pointer += 1
            state = 0
        elif state == 11:  # finding '=' and '*'
            token_generator("SYMBOL")
            current_token_lexeme = ""
            state = 0
        elif state == 12:  # removing whitespace
            current_token_lexeme = ""
            pointer += 1
            state = 0
        elif state == 13:  # unmatched comment or '*' differentiation
            if code[pointer] == '/':
                pointer += 1
                error_handler(3)
                state = 0
            else:
                state = 11

    # new
    if is_token_generated:
        is_token_generated = False
        return generating_token
    else:
        return get_next_token()


def scan():
    global f_symbols, symbol_line, pointer, code, keywords, is_comment_open
    for key in keywords:  # adding all the keywords to the symbol table
        f_symbols.write(f'{symbol_line}.\t{key}\n')
        symbol_line += 1
    while pointer < len(code):  # main job
        get_next_token()
    if is_comment_open:  # unclosed comment
        error_handler(2)
    if no_error:  # no errors
        f_errors.write("There is no lexical error.")


def get_current_line():
    return current_line