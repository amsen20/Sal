def ali(a, b):
    if(a < b):
        a = 2 * a
        b = a * b
        return a
    return b

def main(a, b):
    return ali(a, b)