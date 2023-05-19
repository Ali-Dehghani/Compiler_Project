import scanner
import json


f_json = open('First-Follow.json')
data = json.load(f_json)
f_json.close()

terminals = data['terminals']
non_terminals = data['non_terminals']
firsts = data['first']
follows = data['follow']

token = ''
state = '0'
halt_program = False
get_new_token = True


def parse():
    global terminals, non_terminals, firsts, follows, token, get_new_token
    if get_new_token:
        token = scanner.get_next_token()
    if token[0] in ['KEYWORD', 'SYMBOL']:
        token_str = token[1]
    else:
        token_str = token[0]

