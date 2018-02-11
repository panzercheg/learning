def grep(pattern):
    print("start grep")
    while True:
        line = yield
        if pattern in line:
            print(line)


g = grep("lang")
next(g) #g.send(None)
g.send("golang is better?")
g.send("python is simple!")