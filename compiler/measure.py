import time
from test import main

n = int(input())

start_time = time.time()
ret = main(n)
print("--- {} ms ---".format(int((time.time() - start_time)*1e6)))
print(ret)