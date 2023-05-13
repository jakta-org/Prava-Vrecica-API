x = ""
c,s = 0,0
while x != "X":
    x = input()
    if "/" not in x:
        continue
    s += int(x.split("/")[0][-1])
    c += 1
print(s/c)