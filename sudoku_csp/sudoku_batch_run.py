import sys
import os

"""
Launch sudokus_start.txt in batch mode 
"""

if __name__ == '__main__':
    
    fp = open("output.txt","w") 
    fp.close()

    filename = 'sudokus_start.txt'
    lines = open(filename).read().split('\n')
    for line in lines:
        if line != '':
            cmd = "python sudoku_batch.py " + line
            os.system(cmd)
            #os._exit(1)
