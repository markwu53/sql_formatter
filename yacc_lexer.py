from base import *

lexer_data = {}

def getchar(p):
    text = lexer_data["text"]
    if p == len(text):
        return -1, []
    return p+1, [text[p]]

def lex_char(ch):
    good = lambda d: d[0] == ch
    return check(getchar, good)

lex_comment_begin = sequential(
    lex_char("/"),
    lex_char("*"),
)
lex_comment_end = sequential(
    lex_char("*"),
    lex_char("/"),
)
def lex_comment_body(p):
    q, data = lex_comment_end(p)
    if q >= 0:
        return -1, []
    return getchar(p)
lex_comment = sequential(
    lex_comment_begin,
    star(lex_comment_body),
    lex_comment_end,
)
lex_comment = proc(lex_comment, lambda d: [("comment", d)])

lex_identifier_first_char = check(getchar, lambda d: d[0].isalpha() or d[0] == "_")
lex_identifier_next_char = check(getchar, lambda d: d[0].isalnum() or d[0] == "_")
lex_identifier = sequential(
    lex_identifier_first_char,
    star(lex_identifier_next_char),
)
lex_identifier = proc(lex_identifier, lambda d: [("identifier", d)])

lex_symbol = getchar
lex_symbol = proc(lex_symbol, lambda d: [("symbol", d)])

def lex_string_char_single_quote(p):
    q, data = lex_char("'")(p)
    if q >= 0:
        return -1, []
    return getchar(p)
lex_string_single_quote = sequential(
    lex_char("'"),
    star(lex_string_char_single_quote),
    lex_char("'"),
)
def lex_string_char_double_quote(p):
    q, data = lex_char('"')(p)
    if q >= 0:
        return -1, []
    return getchar(p)
lex_string_double_quote = sequential(
    lex_char('"'),
    star(lex_string_char_double_quote),
    lex_char('"'),
)
lex_string = parallel(
    lex_string_single_quote,
    lex_string_double_quote,
)
lex_string = proc(lex_string, lambda d: [("string", d)])

lex_space = more(check(getchar, lambda d: d[0].isspace()))
lex_space = proc(lex_space, lambda d: [("space", d)])

def lex_tag_identifier_char(p):
    q, data = lex_char(">")(p)
    if q >= 0:
        return -1, []
    return getchar(p)
lex_tag_identifier = sequential(
    lex_char("<"),
    more(lex_tag_identifier_char),
    lex_char(">"),
)
lex_tag_identifier = proc(lex_tag_identifier, lambda d: [("identifier", "".join(d[1:-1]).strip().replace(" ", "_"))])

lex_token = parallel(
    lex_comment,
    lex_identifier,
    lex_string,
    lex_tag_identifier,
    lex_space,
    lex_symbol,
)
lex_token_list = star(lex_token)

def lexer(text):
    lexer_data["text"] = text
    p, tokens = lex_token_list(0)
    tokens = [(t,"".join(v)) for t,v in tokens if not t in ["comment", "space"]]
    tokens = [(t, v[1:-1] if t == "string" else v) for t,v in tokens]
    return tokens

def run():
    import os
    print(os.getcwd())

    grammar_file_path = "my_sql_yacc.bnf"
    text = open(grammar_file_path).read()
    tokens = lexer(text)

    for item in tokens: print(item)
    print(len(tokens))

if __name__ == "__main__":
    run()