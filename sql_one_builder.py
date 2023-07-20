from base import *
from yacc_lexer import lexer

parser_data = {}

id = lambda d: d

def get_token(p):
    tokens = parser_data["tokens"]
    if p == len(tokens):
        return -1, []
    return p+1, [tokens[p]]

def symbol(s):
    def good(d):
        (t,v), = d
        return t == "symbol" and v == s
    return check(get_token, good)

token_identifier = check(get_token, lambda d: d[0][0] == "identifier")
token_string = check(get_token, lambda d: d[0][0] == "string")

proc_yacc = id
proc_rule = id
proc_rule_name = id
proc_rule_def = id
proc_next_branch = id
proc_branch = id
proc_item_quantifier = id
proc_quantifier = id
proc_item = id

#user defined proc functions
def proc_item(d):
    t,v = d[0]
    if t == "identifier":
        if v.upper() == v:
            return [f'keyword("{v}")']
        else:
            parser_data["used"].add(v)
            return [v]
    elif t == "string":
        if len(v) == 1:
            return [f'symbol("{v}")']
        else:
            return [f'keyword("{v}")']

def proc_quantifier(d):
    return [d[0][1]]

def proc_item_quantifier(d):
    if len(d) == 1:
        return d
    v, q = d
    if q == "*":
        return [f"star({v})"]
    elif q == "+":
        return [f"more({v})"]
    elif q == "?":
        return [f"optional({v})"]

def proc_branch(d):
    #if len(d) == 1: return d
    return ["sequential(optional(comments), {}, optional(comments))".format(", ".join(d))]

def proc_next_branch(d):
    return [d[1]]

def proc_rule_def(d):
    if len(d) == 1:
        return d
    return ["parallel({})".format(", ".join(d))]

def proc_rule_name(d):
    name = d[0][1]
    parser_data["defined"].add(name)
    return [name]

def proc_rule(d):
    rule_name = d[0]
    rule_def = d[4]
    default_proc = f"proc_{rule_name} = default_proc"
    rule_function = "def {0}(p): return proc({1}, proc_{0})(p)".format(rule_name, rule_def)
    return [(default_proc, rule_function)]

def yacc(p): return proc(more(rule), proc_yacc)(p)
def rule(p): return proc(sequential(rule_name, symbol(":"), symbol(":"), symbol("="), rule_def, symbol(";")), proc_rule)(p)
def rule_name(p): return proc(token_identifier, proc_rule_name)(p)
def rule_def(p): return proc(sequential(branch, star(next_branch)), proc_rule_def)(p)
def next_branch(p): return proc(sequential(symbol("|"), branch), proc_next_branch)(p)
def branch(p): return proc(more(item_quantifier), proc_branch)(p)
def item_quantifier(p): return proc(sequential(item, optional(quantifier)), proc_item_quantifier)(p)
def quantifier(p): return proc(parallel(symbol("*"), symbol("+"), symbol("?")), proc_quantifier)(p)
def item(p): return proc(parallel(token_identifier, token_string), proc_item)(p)

def write_udf():
    fd = open("udf.py", "w")
    undefined = parser_data["used"].difference(parser_data["defined"])
    undefined = sorted(list(undefined))
    fd.write("#undefined:\n")
    for x in undefined:
        fd.write(f"#{x}\n")
    fd.write("\n")
    fd.write("#proc functions:\n")
    defined = sorted(list(parser_data["defined"]))
    for x in defined:
        fd.write(f"#proc_{x}\n")

def run():
    text = open("bnf.txt").read()
    tokens = lexer(text)
    parser_data["tokens"] = tokens
    parser_data["used"] = set()
    parser_data["defined"] = set()
    p, d = yacc(0)
    a,b = ["\n".join(x) for x in zip(*d)]
    pymodel = open("sql_one_model.py").read()

    fd = open("sql_one_generated.py", "w")
    fd.write(pymodel.format(a=a, b=b))

if __name__ == "__main__":
    run()
