#BNF structure
#function signature f(p) -> (p, data)

def sequential(*fs):
    def fn(p):
        data = []
        for f in fs:
            p, d = f(p)
            if p < 0:
                return -1, []
            data += d
        return p, data
    return fn

def parallel(*fs):
    def fn(p):
        for f in fs:
            q, d = f(p)
            if q >= 0:
                return q, d
        return -1, []
    return fn

def nothing(p): return p, []
def optional(f): return parallel(f, nothing)
#def more(f): return sequential(f, star(f))
def more(f):
    def fn(p):
        p, data = f(p)
        if p < 0:
            return -1, []
        result = []
        while p >= 0:
            q, result = p, result+data
            p, data = f(p)
        return q, result
    return fn
def star(f): return optional(lambda p: more(f)(p))

#post processing
#function signature af(p, data) -> (p, data)

def after(f, af):
    def fn(p):
        p, d = f(p)
        if p < 0:
            return -1, []
        return af(p, d)
    return fn

def proc(f, pr):
    def x(p, d): 
        return p, pr(d)
    return after(f, x)

def check(f, good):
    def af(p, d):
        if good(d):
            return p, d
        return -1, []
    return after(f, af)

#lexer

lexer_data = dict()

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

#parser
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

def compose(f, g):
    def fn(d):
        return f(g(d))
    return fn

def disp(t,v):
    if t == "keyword":
        return v.upper()
    elif t == "string":
        return "'"+v+"'"
    return v

def concat_by(sep):
    def fn(d):
        dd = [disp(t,v) for t,v in d]
        dd = [("processed", sep.join(dd))]
        return dd
    return fn

def indent(d):
    lines = [disp(t,v) for t,v in d]
    lines = [x for line in lines for x in line.splitlines()]
    lines = ["    "+x if len(x) != 0 else x for x in lines]
    dd = [("processed", "\n".join(lines))]
    return dd

def indent_next(d):
    lines = [disp(t,v) for t,v in d]
    lines = [lines[0]]+["    "+x for x in lines[1:]]
    dd = [("processed", "\n".join(lines))]
    return dd

def paren_list(n):
    def fn(d):
        if len(d) >= n:
            d1 = d[1:-1]
            d1 = indent(d1)
            d = [d[0], d1[0], d[-1]]
            d = concat_newline(d)
            return d
        return concat(d)
    return fn

def next_list(n):
    def fn(d):
        if len(d) >= n:
            return indent_next(d)
        return concat(d)
    return fn

concat = concat_by(" ")
concat_tight = concat_by("")
concat_newline = concat_by("\n")
concat_double_line = concat_by("\n\n")
default_proc = concat

#default proc functions - generated from bnf
{a}

#user defined proc functions

#undefined:
#token_bracketed
#token_identifier
#token_number
#token_quoted
#token_string

proc_select_list = indent
proc_connected_tables = indent
proc_indent_boolean_items = indent
proc_case_indent = indent
proc_case_indent_2 = indent
proc_sp_parameter_list_1 = indent
proc_sp_parameter_list_group = concat_newline
proc_table_source = concat_newline
proc_query_expression_group = concat_newline
proc_query_specification = concat_newline
proc_table_source_list = concat_newline
proc_search_condition = concat_newline
proc_with_cte = concat_double_line
proc_case_form = concat_newline
proc_case_form_2 = concat_newline
proc_create_procedure_sig = concat_newline
proc_create_function_sig = concat_newline
proc_insert_statement = concat_newline
proc_value_clause = concat_newline
proc_create_procedure = concat_double_line
proc_create_function = concat_double_line
proc_merge_statement = concat_double_line
#proc_merge_when = concat_newline
proc_select_statement = concat_double_line
proc_query_statement = concat_double_line
proc_next_query_expression = concat_double_line
proc_sp_def_body = concat_double_line
proc_sql_statements = concat_double_line
proc_begin_end_block = concat_double_line
proc_begin_try_block = concat_double_line
proc_query_expression = concat_double_line
proc_subquery_expression = indent
proc_sql_variable = concat_tight
proc_number = concat_tight
proc_decimal_part = concat_tight
proc_comparison_op = concat_tight
proc_temp_table = concat_tight
proc_unicode_string = concat_tight
proc_name = concat_tight
proc_set_update_list = indent_next
proc_paren_list_2 = indent_next
proc_column_full_spec = indent_next
proc_if_statement = concat_newline
proc_if_statement_else = concat_newline
proc_while_statement = concat_newline


proc_in_list = paren_list(7)
proc_paren_list_3 = paren_list(7)
proc_column_spec = paren_list(7)
proc_group_by_columns = next_list(5)

def proc_comments(d):
    d = [x.strip() for t,x in d]
    x = "\n"+ "\n".join(d) + "\n"
    return [("processed", x)]

comments = proc(more(token_comment), proc_comments)

def symbol(s):
    return sequential(optional(comments), symbol_bare(s))

#rule_functions - generated from bnf
{b}

def run():
    text = open("sample/sample2.sql").read()
    tokens = lexer(text)
    #tokens = [t for t in tokens if t[0] not in ["space", "block_comment", "line_comment"]]
    tokens = [t for t in tokens if t[0] not in ["space"]]
    #for t in tokens: print(t)
    parser_data["tokens"] = tokens
    p, d = sql_file(0)
    print(d[0][1])
    #for x in enumerate(d): print(x)

if __name__ == "__main__":
    run()

