from base import *
from sql_lexer import lexer

parser_data = dict()

id = lambda d: d

def get_token(p):
    tokens = parser_data["tokens"]
    if p == len(tokens):
        return -1, []
    return p+1, [tokens[p]]

def symbol_bare(s):
    def good(d):
        (t,v), = d
        return t == "symbol" and v == s
    return check(get_token, good)

keywords_not_identifier = [
    "select",
    "from",
    "where",
    "group",
    "by",
    "order",
    "in",
    "between",
    "and",
    "on",
    "or",
    "when",
    "then",
    "else",
    "case",
    "cast",
    "partition",
    "over",
    "having",
    "not",
    "join",
    "asc",
    "desc",
    "union",
    "all",
    "except",
    "intersect",
    "into",
    "set",
    "exec",
    "execute",
    "if",
    "end",
    "create",
    "return",
    "update",
    "declare",
    "option",
    "pivot",
    "grouping",
    "try",
    "catch",
    "merge",
    "while",
    "begin",
    ]
token_identifier_all = check(get_token, lambda d: d[0][0] == "identifier")
token_identifier = check(get_token, lambda d: d[0][0] == "identifier" and d[0][1].lower() not in keywords_not_identifier)
token_string = check(get_token, lambda d: d[0][0] == "string")
token_number = check(get_token, lambda d: d[0][0] == "number")
token_quoted = check(get_token, lambda d: d[0][0] == "quoted")
token_bracketed = check(get_token, lambda d: d[0][0] == "bracketed")
token_comment = check(get_token, lambda d: d[0][0] in ["block_comment", "line_comment"])

def keyword(k):
    def good(d):
        t,v = d[0]
        return k.upper() == v.upper()
    def proc_keyword(d):
        t,v = d[0]
        return [("keyword", v)]
    return proc(check(token_identifier_all, good), proc_keyword)

#default_proc_functions
from default_udf import *

#user defined proc functions
from udf import *

comments = proc(more(token_comment), proc_comments)

def symbol(s):
    return sequential(optional(comments), symbol_bare(s))

#rule_functions
{b}

def run():
    text = open("sample/sample9.sql").read()
    tokens = lexer(text)
    #tokens = [t for t in tokens if t[0] not in ["space", "block_comment", "line_comment"]]
    tokens = [t for t in tokens if t[0] not in ["space"]]
    parser_data["tokens"] = tokens
    p, d = sql_statements(0)
    print(d[0][1])
    #for x in enumerate(d): print(x)

if __name__ == "__main__":
    run()
