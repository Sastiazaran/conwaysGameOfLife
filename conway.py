"""
conway.py 
A simple Python/matplotlib implementation of Conway's Game of Life.
author: @asti
"""

import sys, argparse
import numpy as np
import matplotlib.pyplot as plt 
import matplotlib.animation as animation
from patterns import *

ON = 1
OFF = 0
vals = [ON, OFF]

# files
file = "reports/report5.txt"
inputFile = "inputs/input5.in"

# global variables
currentGen = 0
generations = 200

def randomGrid(N):
    """returns a grid of NxN random values"""
    return np.random.choice(vals, N*N, p=[0.2, 0.8]).reshape(N, N)

# def addGlider(i, j, grid):
#     """adds a glider with top left cell at (i, j)"""
#     glider = np.array([[0,    0, 255], 
#                        [255,  0, 255], 
#                        [0,  255, 255]])
#     grid[i:i+3, j:j+3] = glider

def counter():
    for element in allPatterns:
        counters[element.name] = 0

def compareMatrix(matA,matB,width,height):
    for i in range(width):
        for j in range(height):
            if(matA[i][j] != matB[i][j]):
                return False
    return True

def update(frameNum, img, grid, neighbor, N):
    # copy grid since we require 8 neighbors for calculation
    # and we go line by line 
    newGrid = grid.copy()
    
    # TODO: Implement the rules of Conway's Game of Life
    global currentGen
    global generations

    if currentGen > generations:
        exit()

    counter()

    for i in range(N):
        for j in range(N):
            # implementation of comparation of matrix 
            if not neighbor[i,j]:   
                neighbor[i,j] = 1
                for element in allPatterns:
                    for pat in element.pattern:
                        width, height = len(pat), len(pat[0])
                        if i + width + 1 > N or j + height + 1 > N:
                            continue

                        array = np.array(pat)
                        newArray = np.zeros((width + 2, height + 2))
                        newArray[1:width + 1, 1:height + 1] = array
                        # print("array", array)
                        # print("newarray", newArray)

                        if compareMatrix(newArray, grid[i:i+width+2, j:j+height+2], width+1, height+1):
                            # print("comparando matriz")
                            counters[element.name] += 1

                            for a in range(i, i + width + 1):
                                for b in range(j, j + height + 1):
                                    neighbor[a,b] = 1
                
            # Counting the number of alive neighbors
            neighbors = grid[(i-1)%N,(j-1)%N] + grid[(i-1)%N,j] + grid[(i-1)%N,(j+1)%N] \
                      + grid[i,(j-1)%N] + grid[i,(j+1)%N] \
                      + grid[(i+1)%N,(j-1)%N] + grid[(i+1)%N,j] + grid[(i+1)%N,(j+1)%N]
            # Basic rules of Conway's Game Of Life
            if grid[i,j] == ON and (neighbors < 2 or neighbors > 3):
                newGrid[i,j] = OFF
            elif grid[i,j] == OFF and neighbors == 3:
                newGrid[i,j] = ON

    currentGen += 1

    # report generator
    #print(counters)

    f = open(file, "a")
    total = 0
    for key in counters:
        total += counters[key]
    
    f.write("iteration: {}\n".format(currentGen))

    for key, val in counters.items():
        chain = key.ljust(10)
        chain_val = str(val).ljust(6)
        percentage = 0.0
        if total > 0:
            percentage = float(val) / total * 100
        chain_percentage = "{:.5f}".format(percentage).ljust(6)
        f.write("|{}\t|\t{}\t\t|\t{}\t\t|\n".format(chain, chain_val, chain_percentage))

    chain_total = str(total).ljust(6)

    f.write("|total      |\t{}\t\t|               |\n".format(chain_total))
    f.write("\n")
    f.close()

    for i in range(N):
        for j in range(N):
            neighbor[i, j] = 0

    # update data
    img.set_data(newGrid)
    grid[:] = newGrid[:]
    return img,

# main() function
def main():
    # Command line args are in sys.argv[1], sys.argv[2] ..
    # sys.argv[0] is the script name itself and can be ignored
    # parse arguments
    parser = argparse.ArgumentParser(description="Runs Conway's Game of Life system.py.")
    # TODO: add arguments
    
    # :(

    # set grid size
    N = 100
    M = 100
        
    # set animation update interval
    updateInterval = 50

    # declare grid
    grid = np.array([])
    neighbor = np.array([])

    # reading input 
    f = open(inputFile, "r")
    lines = f.readlines()

    width, height = lines[0].split()
    width, height = int(width), int(height)
    N = width
    M = height
    

    generations = int(lines[1])
    grid = np.zeros((N,M))
    neighbor = np.zeros((N,M))

    for line in lines[2:]:
        i, j = line.split()
        i, j = int(i), int(j)
        grid[i,j] = ON


    # glider
    # grid[50, 50:53] = 1
    # grid[51, 52] = 1
    # grid[52, 51] = 1
    # grid[52, 50] = 1
    # grid[52, 49] = 1



    # populate grid with random on/off - more off than on
    #grid = randomGrid(N)
    # Uncomment lines to see the "glider" demo
    #grid = np.zeros(N*N).reshape(N, N)
    #addGlider(1, 1, grid)

    # set up animation
    fig, ax = plt.subplots()
    img = ax.imshow(grid, interpolation='nearest')
    ani = animation.FuncAnimation(fig, update, fargs=(img, grid, neighbor, N, ),
                                  frames = 10,
                                  interval=updateInterval,
                                  save_count=50)

    plt.show()

# call main
if __name__ == '__main__':
    main()