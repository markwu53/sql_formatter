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
