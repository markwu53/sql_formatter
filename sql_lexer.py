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
lex_comment = proc(lex_comment, lambda d: [("block_comment", d)])

line_terminator = parallel(
    sequential(lex_char("\r"), lex_char("\n")),
    sequential(lex_char("\n"), lex_char("\r")),
    lex_char("\n"),
    lex_char("\r"),
    )
def lex_line_comment_char(p):
    q, data = line_terminator(p)
    if q >= 0:
        return -1, []
    return getchar(p)
lex_line_comment = sequential(
    lex_char("-"),
    lex_char("-"),
    star(lex_line_comment_char),
    line_terminator,
    )
lex_line_comment = proc(lex_line_comment, lambda d: [("line_comment", d)])

lex_identifier_first_char = check(getchar, lambda d: d[0].isalpha() or d[0] == "_")
lex_identifier_next_char = check(getchar, lambda d: d[0].isalnum() or d[0] == "_")
lex_identifier = sequential(
    lex_identifier_first_char,
    star(lex_identifier_next_char),
)
lex_identifier = proc(lex_identifier, lambda d: [("identifier", d)])

lex_digit = check(getchar, lambda d: d[0].isdigit())
lex_number = more(lex_digit)
lex_number = proc(lex_number, lambda d: [("number", d)])

lex_symbol = getchar
lex_symbol = proc(lex_symbol, lambda d: [("symbol", d)])

def lex_string_char_normal(p):
    q, data = lex_char("'")(p)
    if q >= 0:
        return -1, []
    return getchar(p)
lex_string_char_quote = sequential(lex_char("'"), lex_char("'"))
lex_string_char = parallel(lex_string_char_quote, lex_string_char_normal)
lex_string_single_quote = sequential(
    lex_char("'"),
    star(lex_string_char),
    lex_char("'"),
)
lex_string = lex_string_single_quote
lex_string = proc(lex_string, lambda d: [("string", d)])

lex_space = more(check(getchar, lambda d: d[0].isspace()))
lex_space = proc(lex_space, lambda d: [("space", d)])

def lex_quoted_body_char(p):
    q, data = lex_char('"')(p)
    if q >= 0:
        return -1, []
    return getchar(p)
lex_quoted = sequential(lex_char('"'), more(lex_quoted_body_char), lex_char('"'))
lex_quoted = proc(lex_quoted, lambda d: [("quoted", d)])

def lex_bracketed_body_char(p):
    q, data = lex_char(']')(p)
    if q >= 0:
        return -1, []
    return getchar(p)
lex_bracketed = sequential(lex_char('['), more(lex_bracketed_body_char), lex_char(']'))
lex_bracketed = proc(lex_bracketed, lambda d: [("bracketed", d)])

lex_token = parallel(
    lex_comment,
    lex_line_comment,
    lex_identifier,
    lex_number,
    lex_string,
    lex_quoted,
    lex_bracketed,
    lex_space,
    lex_symbol,
)
lex_token_list = star(lex_token)

def lexer(text):
    lexer_data["text"] = text
    p, tokens = lex_token_list(0)
    tokens = [(t,"".join(v)) for t,v in tokens]
    #tokens = [(t,v) for t,v in tokens if not t in ["block_comment", "line_comment", "space"]]
    tokens = [(t, v[1:-1] if t == "string" else v) for t,v in tokens]
    return tokens

def run():
    grammar_file_path = "sample2.sql"
    text = open(grammar_file_path).read()
    tokens = lexer(text)

    for i,v in enumerate(tokens): 
        if i > 200:
            break
        print(i, v)
    print(len(tokens))

if __name__ == "__main__":
    run()