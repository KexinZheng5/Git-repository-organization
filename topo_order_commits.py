import os 
import sys 
import zlib 
import copy 
from collections import deque

class CommitNode:
    def __init__(self, commit_hash):
        """
        :type commit_hash: str
        """
        self.commit_hash = commit_hash
        self.parents = set()
        self.children = set()


# get .git directory: 
def get_git_dir():
    # look for .git directory
    cwd = os.getcwd() # current working directory
    while(not (os.path.isdir(cwd + "\\.git"))):
        new = os.path.abspath(os.path.join(cwd, os.pardir))
        # check if it's the root directory
        if (new == cwd):
            sys.stdout.write("Error: Not inside a Git repository\n")
            sys.exit(1)
        cwd = new
    return cwd + "\\.git"

def get_branches(dir):
    # if \\refs\\heads not found
    dir = dir + "\\refs\\heads"
    if(not (os.path.isdir(dir))):
        sys.stdout.write("Error: Can't find refs\\heads in .git directory\n")
        sys.exit(1)

    # initialize a list for branches
    branches = []
    # temp file for all sub directories
    temp = os.listdir(dir)

    # temporary list
    while(temp):
        if os.path.isdir(dir + "\\" + temp[0]):
            extended_dir = ['{1}\\{0}'.format(element,temp[0]) for element in os.listdir(dir + "\\" + temp[0])]
            temp.extend(extended_dir)
            temp.pop(0)
        else: 
            file = open(dir + "\\" + temp[0], 'r')
            branches.append((temp.pop(0), file.readline().strip()))
            file.close()

    return branches        

# create graph    
def build_graph(dir, branches):
    # get commit info and parent
    dir = dir + "\\objects"
    if(not (os.path.isdir(dir))):
        sys.stdout.write("Error: Can't find objects in .git directory\n")
        sys.exit(1)

    # create a dictionary of nodes processed
    nodes = {}
    # visited commits
    visited = set() 
    # commits to process
    stack = []
    # store commit hash into stack
    for e in branches: 
        stack.append(e[1])

    while stack: 
        # pop the first element from stack
        commit_hash = stack.pop(0)

        # if visited -> skip the rest of the steps and continue processing the next element in stack
        if commit_hash in visited: 
            continue 

        # else, add it to visited
        visited.add(commit_hash) 

        # if it is not in nodes -> create node
        if commit_hash not in nodes: #Replace with code - Create a commit node and store it in the graph for later use
            nodes[commit_hash] = CommitNode(commit_hash)
        commit = nodes[commit_hash]

        # get parents
        filename = dir + "\\" + commit_hash[0:2] + "\\" + commit_hash[2:]
        # extract content
        compressed_contents = open(filename, 'rb').read()
        decompressed_contents = zlib.decompress(compressed_contents)
        # get parent commit hash
        lines = str(decompressed_contents).split("\\n")
        for l in lines: 
            if(l.startswith("parent")):
                commit.parents.add(l[7:])

        # process parents
        for p in commit.parents: 
            # if not visited -> add to stack
            if p not in visited: 
                stack.append(p)
            # if not created -> create node and append children
            if p not in nodes: 
                nodes[p] = CommitNode(p)
                nodes[p].children.add(commit_hash)
            elif commit_hash not in nodes[p].children: 
                nodes[p].children.add(commit_hash)
    
    return nodes

# sort in topological order
def topological_sort(nodes): 
    result = []
    no_children = deque()
    copy_graph = copy.deepcopy(nodes) 

    # add commit to no_children if it doesn't have children
    for commit_hash in copy_graph: 
        if len(copy_graph[commit_hash].children) == 0: 
            no_children.append(commit_hash)

    while len(no_children) > 0:
        commit_hash = no_children.popleft() 
        result.append(commit_hash)

        # process parents
        for parent_hash in list(copy_graph[commit_hash].parents): 
            # remove edge
            copy_graph[commit_hash].parents.remove(parent_hash) 
            copy_graph[parent_hash].children.remove(commit_hash)
            # add to list of parent now have no children
            if len(copy_graph[parent_hash].children) == 0:
                no_children.append(parent_hash)

    # check for left over
    if len(result) < len(nodes): 
        raise Exception("cycle detected")
    return result

# print nodes with format
def print_topo_ordered_commits(commit_nodes, topo_ordered_commits, head_to_branches): 
    jumped = False 
    for i in range(len(topo_ordered_commits)): 
        commit_hash = topo_ordered_commits[i] 
        if jumped: 
            jumped = False 
            sticky_hash = ' '.join(commit_nodes[commit_hash].children) 
            print(f'={sticky_hash}')
        branches = sorted(head_to_branches[commit_hash]) if commit_hash in head_to_branches else [] 
        print(commit_hash + (' ' + ' '.join(branches) if branches else ''))
        if i+1 < len(topo_ordered_commits) and topo_ordered_commits[i+1] not in commit_nodes[commit_hash].parents:
            jumped = True 
            sticky_hash = ' '.join(commit_nodes[commit_hash].parents) 
            print(f'{sticky_hash}=\n')

# topo_order_commits
def topo_order_commits():
    # 1. get .git directory
    git_dir = get_git_dir()

    # Get the list of local branch names
    branches = get_branches(git_dir)

    # create graph
    nodes = build_graph(git_dir, branches)
    
    sorted_nodes = topological_sort(nodes)
    #print(sorted_nodes)
    head_to_branches = {}
    for e in branches: 
        head_to_branches[e[1]] = [e[0]]
    #print(head_to_branches)

    print_topo_ordered_commits(nodes, sorted_nodes, head_to_branches)
    
    """
    for value in nodes.values():
        print(value.commit_hash)
        print(value.parents)
        print(value.children, "\n")
    """


#Get git directory (can be helper function) #Get list of local branch names (can be helper function) #Build the commit graph (can be helper function) #Topologically sort the commit graph (can be helper fnction) #Print the sorted order (can be helper function)

if __name__ == '__main__': 
    topo_order_commits()