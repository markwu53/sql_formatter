from gen_parser import *

def run():
    text = open("sample/sample8.sql").read()
    tokens = lexer(text)
    #tokens = [t for t in tokens if t[0] not in ["space", "block_comment", "line_comment"]]
    tokens = [t for t in tokens if t[0] not in ["space"]]
    #for t in tokens: print(t)
    parser_data["tokens"] = tokens
    p, d = sql_statements(0)
    print(d[0][1])
    #for x in enumerate(d): print(x)

def run2():
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

if __name__ == "__main__":
    run()
