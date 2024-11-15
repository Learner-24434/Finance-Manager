def draw(n):
    if n == 0:
        return
    draw(n-1)
    print(n)

draw(5)