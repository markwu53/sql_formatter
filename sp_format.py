from gen_parser import *

def run():
    text = open("sample/sample8.sql").read()
    tokens = lexer(text)
    parser_data["tokens"] = tokens
    p, d = sql_statements(0)
    print(d[0][1])
    #for x in enumerate(d): print(x)

def run():
    import os, time
    files = os.listdir("pk_function")
    before = time.time()
    for x in files:
        #if x != "Wordparser.sql": continue
        #if x.find("Smart") < 0: continue
        text = open(f"pk_function/{x}").read()
        tokens = lexer(text)
        parser_data["tokens"] = tokens
        p, d = create_function(0)
        #print(d[0][1])
        #print(len(tokens) == p)
        if (len(tokens) != p):
            print("bad:", x, p, len(tokens))
        else:
            #print("good:", x, p)
            fd = open(f"pk_function_formatted/{x}", "w")
            fd.write(d[0][1])
            #command = f"del pk_sp_bad\{x}"
            #os.system(command)
    after = time.time()
    difference = after - before
    difference = round(difference)
    print(difference)

def run():
    import os, time
    files = os.listdir("AON_PL/sql")
    before = time.time()
    for x in files:
        text = open(f"AON_PL/sql/{x}").read()
        tokens = lexer(text)
        parser_data["tokens"] = tokens
        p, d = sql_statements(0)
        if (len(tokens) != p):
            print("bad:", x, p, len(tokens))
        else:
            print("good:", x, p)
            fd = open(f"AON_PL/formatted/{x}", "w")
            fd.write(d[0][1])
            #command = f"del pk_sp_bad\{x}"
            #os.system(command)
    after = time.time()
    difference = after - before
    difference = round(difference)
    print(difference)

if __name__ == "__main__":
    run()
