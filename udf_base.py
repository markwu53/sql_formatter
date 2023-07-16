
def compose(f, g):
    def fn(d):
        return f(g(d))
    return fn

def disp(t,v):
    if t == "keyword":
        return v.upper()
    elif t == "string":
        return f"'{v}'"
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
