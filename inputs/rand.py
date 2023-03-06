"""
author: @quiqueluna
random generator of gameOfLife points
"""

import random
file = open("input5.in","a")
for p in range(1000):
    y = random.randint(0,99)
    x = random.randint(0,99)
    file.write(str(y)+" "+str(x)+"\n")
file.close()
