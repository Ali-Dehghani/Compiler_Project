#import scanner
import json


f_json = open('First-Follow.json')
data = json.load(f_json)
f_json.close()

terminals = data['terminals']
non_terminals = data['non_terminals']
firsts = data['first']
follows = data['follow']


def parse():

    return
