import os 
import sys 
import zlib 
import copy 
from collections import deque

def topo_order_commits():
    # look for .git directory
    cwd = os.getcwd() # current working directory
    while(not (os.path.isdir(cwd + "/.git"))):
        new = os.path.abspath(os.path.join(cwd, os.pardir))
        if (new == cwd):
            print("Not inside a Git repository")
            return
        cwd = new
    print(cwd)


#Get git directory (can be helper function) #Get list of local branch names (can be helper function) #Build the commit graph (can be helper function) #Topologically sort the commit graph (can be helper fnction) #Print the sorted order (can be helper function)

if __name__ == '__main__': 
    topo_order_commits()