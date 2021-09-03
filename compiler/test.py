def fib(n):
    ret = 1
    if n > 1:
        ret = fib(n-1) + fib(n-2)
    return ret

def main(n):
    return fib(n)