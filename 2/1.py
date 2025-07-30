def check(st:str)-> bool:
    if len(st)>1 and st[0] == '0':
        return False
    if int(st) >= 256:
        return False
    return True
def count(st)->int:
    n = len(st)
    ans = 0
    for i in range(1, min(4, n - 2)):
        first = st[:i]
        if not check(first):
            continue
        for j in range(i + 1, min(i + 4, n - 1)):
            second = st[i:j]
            if not check(second):
                continue
            for k in range(j + 1, min(j + 4, n)):
                third = st[j:k]
                fourth = st[k:]
                if not check(third):
                    continue
                if not check(fourth):
                    continue
                ans+=1
                # print(f"{first}.{second}.{third}.{fourth}")
    return ans
s = input().strip()
print(count(s[1:-1]))
