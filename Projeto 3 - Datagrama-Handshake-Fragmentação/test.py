
import time

a = 10
time_init = time.time()

while a < 10000:
    time.sleep(0.1)
    a+=0.5
    print(a)
    if (time.time()-time_init) > 5:
        break

input("hello, fuck")

