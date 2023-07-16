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
def proc_rule(d): return [(d[0][1], d[4])]
def proc_rule_name(d):
    t,v = d[0]
    return [("rulename", v)]
def proc_rule_def(d):
    if len(d) == 1:
        return d
    return [("parallel", d)]
def proc_next_branch(d):
    return [d[1]]
def proc_branch(d):
    return [("sequential", d)]
def proc_item_quantifier(d):
    return [("item", d)]
def proc_quantifier(d):
    t,v = d[0]
    return [("quantifier", v)]
def proc_item(d):
    t,v = d[0]
    if t == "identifier":
        if v.upper() != v:
            used = parser_data["used"]
            if v not in used:
                used[v] = 0
            used[v] += 1
    return d
            

def yacc(p): return proc(more(rule), proc_yacc)(p)
def rule(p): return proc(sequential(rule_name, symbol(":"), symbol(":"), symbol("="), rule_def, symbol(";")), proc_rule)(p)
def rule_name(p): return proc(token_identifier, proc_rule_name)(p)
def rule_def(p): return proc(sequential(branch, star(next_branch)), proc_rule_def)(p)
def next_branch(p): return proc(sequential(symbol("|"), branch), proc_next_branch)(p)
def branch(p): return proc(more(item_quantifier), proc_branch)(p)
def item_quantifier(p): return proc(sequential(item, optional(quantifier)), proc_item_quantifier)(p)
def quantifier(p): return proc(parallel(symbol("*"), symbol("+"), symbol("?")), proc_quantifier)(p)
def item(p): return proc(parallel(token_identifier, token_string), proc_item)(p)

def substitute(item, repo):
    rules = parser_data["rules"]
    type, content = item
    if type in ["sequential", "parallel"]:
        for x in content:
            substitute(x, repo)
    elif type == "item":
        one = content[0]
        t,v = one
        if t == "identifier":
            if v in repo:
                content[0] = rules[v]
                repo.remove(v)
        elif t in ["sequential", "parallel"]:
            substitute(one, repo)

def expand(name):
    rules = parser_data["rules"]
    body = rules[name]
    repo = set(list(parser_data["repo"]))
    if name in repo:
        repo.remove(name)
    while True:
        compare = str(body)
        substitute(body, repo)
        compare2 = str(body)
        if compare == compare2:
            break
    return body

def dependency(name):
    def depend(item):
        repo = parser_data["repo"]
        #print("type:", item[0])
        type, content = item
        if type in ["sequential", "parallel"]:
            return [y for x in content for y in depend(x)]
        if type == "item":
            one = content[0]
            t,v = one
            if t == "identifier":
                return [v]
            if t in ["sequential", "parallel"]:
                return depend(one)
            return []
        return []
    body = parser_data["expand"][name]
    dep = depend(body)
    result = []
    for x in dep:
        if x not in result:
            if x in parser_data["defined"]:
                result.append(x)
    return result

def traverse(front):
    #width first
    result = []
    while len(front) != 0:
        result += [x for x in front if x not in result]
        new_front = []
        for x in front:
            if x in parser_data["depend"]:
                for y in parser_data["depend"][x]:
                    if y not in result:
                        if y not in new_front:
                            new_front.append(y)
        front = new_front
    return result

def indent(text):
    lines = text.splitlines()
    lines = ["    "+x for x in lines]
    return "\n".join(lines)

def display(item):
    type, content = item
    if type == "parallel":
        #return " | ".join([display(x) for x in content])
        return indent("\n| ".join([display(x) for x in content]))
    if type == "sequential":
        return " ".join([display(x) for x in content])
    if type == "item":
        one = content[0]
        t,v = one
        result = "unknown"
        if t == "identifier":
            result = v
        elif t == "string":
            result = f"'{v}'"
        elif t in ["sequential"]:
            if len(v) == 1:
                result = display(one)
            elif len(content) == 1:
                result = display(one)
            else:
                result = "("+display(one)+")"
        elif t in ["parallel"]:
            if len(v) == 1:
                result = display(one)
            else:
                result = "(\n"+display(one)+"\n)"
        if len(content) == 2:
            suffix = content[1][1]
            result += suffix
        return result

def display(item):
    type, content = item
    if type == "parallel":
        #return " | ".join([display(x) for x in content])
        return " | ".join([display(x) for x in content])
    if type == "sequential":
        return " . ".join([display(x) for x in content])
    if type == "item":
        one = content[0]
        t,v = one
        result = "unknown"
        if t == "identifier":
            result = v
        elif t == "string":
            result = f"'{v}'"
        elif t in ["sequential"]:
            if len(v) == 1:
                result = display(one)
            elif len(content) == 1:
                result = display(one)
            else:
                #result = "("+display(one)+")"
                result = "(\n"+indent(display(one))+")"
        elif t in ["parallel"]:
            if len(v) == 1:
                result = display(one)
            else:
                result = "(\n"+indent(display(one))+")"
        if len(content) == 2:
            suffix = content[1][1]
            #result += suffix
            if suffix == "?":
                result = f"""(
    {result} | NOTHING)"""
            elif suffix == "+":
                result = f"repeat({result})"
            elif suffix == "*":
                result = f"""(
    repeat({result}) | NOTHING)"""
        return result

def run():
    text = open("bnf.txt").read()
    tokens = lexer(text)
    parser_data["tokens"] = tokens
    parser_data["used"] = dict()

    p, d = yacc(0)

    parser_data["rules"] = dict(d)
    rules = parser_data["rules"]
    defined = set(rules.keys())
    parser_data["defined"] = defined
    used = parser_data["used"]
    n1 = [(x, n) for x,n in used.items() if n == 1]
    n2 = [(x, n) for x,n in used.items() if n > 1]
    n2 = set([x for x,n in n2])
    parser_data["repo"] = defined.difference(n2)
    parser_data["expand"] = {name:expand(name) for name in defined}
    parser_data["depend"] = {name:dependency(name) for name in defined}
    #for x in parser_data["depend"].items(): print(x)
    root = ["create_procedure", "create_function", "sql_statements"]
    rule_list = traverse(root)
    for x in rule_list:
        print("{} ::= \n{};\n".format(x, display(parser_data["expand"][x])))

if __name__ == "__main__":
    run()
