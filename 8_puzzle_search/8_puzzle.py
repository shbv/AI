"""
Modules
"""
import sys
import collections
import resource
import time
import queue

"""
Manh_score - heuristic cost to reach goal state from current state
"""
def manh_score(state):

    # Goal state
    goal_state = {0 : [0,0], 1 : [0,1], 2 : [0,2], 3 : [1,0], 4 : [1,1], 5 : [1,2], 6 : [2,0], 7 : [2,1], 8 : [2,2] }

    # manh dist of state from goal state
    manh_score = 0    
    for i in range(1,9):
        index = state.index(i)    
        row = int(index/3)
        col = index % 3
        manh_score += abs(goal_state[i][0]-row) + abs(goal_state[i][1]-col) 
    return manh_score

"""
Score of a node
"""
def cost_fn(node):
    # depth of the current node from parent + heuristic cost to reach the goal state from this node
    return node.dep + manh_score(node.state)

"""
Node class:
"""
class node:
    """ Class for Node datastructure in the graph """
    
    def __init__(self, state, par=None, move=None, dep=0):
        self.state = state #state
        self.par = par #parent
        self.move = move #move of parent to reach here
        if par is not None:
            self.dep = self.par.dep + 1 #depth of node from root
        else:
            self.dep = dep #depth of node from root

    def get_neighbors(self, board):
        neighbors = []
        for move in board.legal_moves:
            nnode_state = board.get_new_state(self.state, move)
            if nnode_state is not None:    
                neighbors.append(node(nnode_state, self, move))
        return neighbors

    def get_neighbors_reverse(self, board):
        neighbors = []
        for move in list(reversed(board.legal_moves)):
            nnode_state = board.get_new_state(self.state, move)
            if nnode_state is not None:    
                neighbors.append(node(nnode_state, self, move))
        return neighbors

    def path_from_root(self):
        reverse_path_from_root = []
        currnode = self
        while currnode:
            reverse_path_from_root.append(currnode.move)
            currnode = currnode.par
        path_from_root = list(reversed(reverse_path_from_root))
        return path_from_root[1:] 

    def __eq__(self, other):
        return self.state == other.state

    def __ne__(self, other):
        return self.state != other.state

"""
Board - 8 puzzle game class:
"""
class Board:
    """ Class for 8 puzzle board and its state """
    
    def __init__(self, init_state = None, goal_state = None):
        self.legal_moves = ["Up", "Down", "Left", "Right"]
        #self.legal_moves_reverse = ["Right", "Left", "Down", "Up"]
        self.init_state = init_state
        self.goal_state = goal_state

    def get_new_state(self, from_state, move):
        
        # new state initialize
        to_state = list(from_state)
        # index location of zero
        z_index = to_state.index(0)
        
        #print(from_state)
        #print(z_index)
        #print(move)
        
        if move == "Up":
            # Swap z_index-3, z_index except for 1st row
            if z_index >= 3:
                swap_val = to_state[z_index-3]
                to_state[z_index] = swap_val
                to_state[z_index-3] = 0
                #print(to_state)
                return to_state
        elif move == "Down":
            # Swap z_index+3, z_index except for last row
            if z_index <= 5:
                swap_val = to_state[z_index+3]
                to_state[z_index] = swap_val
                to_state[z_index+3] = 0
                #print(to_state)
                return to_state
        elif move == "Left":
            # Swap z_index-1, z_index except for 1st column
            if (z_index % 3) != 0:
                swap_val = to_state[z_index-1]
                to_state[z_index] = swap_val
                to_state[z_index-1] = 0
                #print(to_state)
                return to_state
        elif move == "Right":
            # Swap z_index+1, z_index except for last column
            if ((z_index + 1) % 3) != 0:
                swap_val = to_state[z_index+1]
                to_state[z_index] = swap_val
                to_state[z_index+1] = 0
                #print(to_state)
                return to_state
        return None       


"""
Goal test function
"""
def goaltest(state, goal_state): 
    if state == goal_state:
        print("Found goal_state: {}".format(state))
        return True
    else:
        return False


"""
BFS function:
"""
def bfs(board):

    global max_search_depth

    # Initial and goal settings
    init_state = board.init_state
    goal_state = board.goal_state

    # Create empty frontier and explored set
    frontier = collections.deque()
    explored = set()
    frontier_set = set()

    # Add init state to queue
    currnode = node(init_state)
    frontier.append(currnode)

    # Search the graph    
    while len(frontier) > 0:
        
        # Remove state from queue
        currnode = frontier.popleft()
        explored.add(tuple(currnode.state))
        if currnode.dep > max_search_depth:
                max_search_depth = currnode.dep 

        # Check against goal state
        if goaltest(currnode.state, goal_state):
            num_explored_nodes = len(explored)
            num_frontier_nodes = len(frontier)
            return currnode, num_explored_nodes, num_frontier_nodes
        
        # Get neighbors (avoid repetitions)
        #print("Parent node: {}".format(currnode.state))
        neighbors = currnode.get_neighbors(board)
        for nnode in neighbors:
            #print("nnode state is {}, move used to get here is {}".format(nnode.state,nnode.move))
            if ((tuple(nnode.state) not in explored) and (tuple(nnode.state) not in frontier_set)):
                frontier.append(nnode)
                frontier_set.add(tuple(nnode.state))
                if nnode.dep > max_search_depth:
                    max_search_depth = nnode.dep 

        # Find the len of explored / frontier nodes
        num_explored_nodes = len(explored)
        num_frontier_nodes = len(frontier)
        if num_explored_nodes % 10000 == 0:
            print("num_explored_nodes = {}, num_frontier_nodes = {}".format(num_explored_nodes, num_frontier_nodes))

    num_explored_nodes = len(explored)
    num_frontier_nodes = len(frontier)
    return None, num_explored_nodes, num_frontier_nodes

"""
DFS function:
"""
def dfs(board):

    global max_search_depth

    # Initial and goal settings
    init_state = board.init_state
    goal_state = board.goal_state

    # Create empty frontier and explored set
    frontier = collections.deque()
    explored = set()
    frontier_set = set()

    # Add init state to queue
    currnode = node(init_state)
    frontier.append(currnode)

    # Search the graph    
    while len(frontier) > 0:
        
        # Remove state from queue
        currnode = frontier.pop()
        explored.add(tuple(currnode.state))
        if currnode.dep > max_search_depth:
                max_search_depth = currnode.dep 

        # Check against goal state
        if goaltest(currnode.state, goal_state):
            num_explored_nodes = len(explored)
            num_frontier_nodes = len(frontier)
            return currnode, num_explored_nodes, num_frontier_nodes
        
        # Get neighbors (avoid repetitions)
        #print("Parent node: {}".format(currnode.state))
        neighbors = currnode.get_neighbors_reverse(board)
        for nnode in neighbors:
            #print("nnode state is {}, move used to get here is {}".format(nnode.state,nnode.move))
            if ((tuple(nnode.state) not in explored) and (tuple(nnode.state) not in frontier_set)):
                frontier.append(nnode)
                frontier_set.add(tuple(nnode.state))
                if nnode.dep > max_search_depth:
                    max_search_depth = nnode.dep 

        # Find the len of explored / frontier nodes
        num_explored_nodes = len(explored)
        num_frontier_nodes = len(frontier)
        if num_explored_nodes % 10000 == 0:
            print("num_explored_nodes = {}, num_frontier_nodes = {}".format(num_explored_nodes, num_frontier_nodes))

    num_explored_nodes = len(explored)
    num_frontier_nodes = len(frontier)
    return None, num_explored_nodes, num_frontier_nodes

"""
Priority obj for priority queue with node
"""
class priority_obj():
    def __init__(self, priority, obj):
        self.priority = priority
        self.object = obj
        return
    def __cmp__(self, other):
        return cmp(self.priority, other.priority)
    def __lt__(self, other):
        return self.priority < other.priority

"""
A* function:
"""
def ast(board):

    global max_search_depth

    # Initial and goal settings
    init_state = board.init_state
    goal_state = board.goal_state

    # Create empty frontier and explored set
    frontier = queue.PriorityQueue()
    explored = set()
    frontier_set = set()

    # Add init state to queue
    currnode = node(init_state)
    f = cost_fn(currnode)
    print("Initial cost fn is {}".format(f))
    frontier.put(priority_obj(f,currnode))

    # Search the graph    
    while not frontier.empty():
        
        # Remove state from queue
        currnode = frontier.get().object
        if (tuple(currnode.state) in explored):
            continue
        explored.add(tuple(currnode.state))
        if currnode.dep > max_search_depth:
                max_search_depth = currnode.dep 

        # Check against goal state
        if goaltest(currnode.state, goal_state):
            num_explored_nodes = len(explored)
            num_frontier_nodes = frontier.qsize()
            return currnode, num_explored_nodes, num_frontier_nodes
        
        # Get neighbors (avoid repetitions)
        #print("Parent node: {}".format(currnode.state))
        neighbors = currnode.get_neighbors(board)
        for nnode in neighbors:
            nnode_cost = cost_fn(nnode)
            if ((tuple(nnode.state) not in explored) and (tuple(nnode.state) not in frontier_set)):
                #print("nnode state is {}, move used to get here is {}, cost is {}".format(nnode.state,nnode.move,nnode_cost))
                frontier.put(priority_obj(nnode_cost,nnode))
                frontier_set.add(tuple(nnode.state))
                if nnode.dep > max_search_depth:
                    max_search_depth = nnode.dep 
            elif tuple(nnode.state) in frontier_set:
                # Update the cost. 
                # Possible duplicates in priority queue but check at beginning for skipping explored nodes should suffice
                #print("Existing nnode state is {}, cost is {}".format(nnode.state,nnode_cost))
                frontier.put(priority_obj(nnode_cost,nnode))
                #frontier.put((nnode_cost,nnode))
                

        # Find the len of explored / frontier nodes
        num_explored_nodes = len(explored)
        num_frontier_nodes = frontier.qsize()
        if num_explored_nodes % 10000 == 0:
            print("num_expored_nodes = {}, num_frontier_nodes = {}".format(num_explored_nodes, num_frontier_nodes))

    num_explored_nodes = len(explored)
    num_frontier_nodes = len(frontier)
    return None, num_explored_nodes, num_frontier_nodes

"""
Main 
"""
if __name__ == '__main__':
    
    tick = time.process_time() 
    max_search_depth = 0

    # Get the inputs:
    if len(sys.argv) != 3:
        print("Wrong number of arguments given: {}".format(len(sys.argv)))
    method = sys.argv[1]
    init_state = [int(x) for x in sys.argv[2].split(",")]
    print("method: {}, board init_state: {}".format(method,init_state))
    goal_state = [0,1,2,3,4,5,6,7,8]
    print("goal: {}".format(goal_state))
    
    # Create a board:
    board = Board(init_state, goal_state)

    # Call the search method
    if method == "bfs":
        terminal_node, num_explored_nodes, num_frontier_nodes = bfs(board)
        path_to_goal = terminal_node.path_from_root()
    elif method == "dfs":
        terminal_node, num_explored_nodes, num_frontier_nodes = dfs(board)
        path_to_goal = terminal_node.path_from_root()
    elif method == "ast":
        terminal_node, num_explored_nodes, num_frontier_nodes = ast(board)
        path_to_goal = terminal_node.path_from_root()
    else:
        print("Only bfs,dfs,afs are supported currently")

    tock = time.process_time()

    file = open("output.txt","w") 
    file.write("path_to_goal: {}\n".format(path_to_goal)) 
    file.write("cost_of_path: {}\n".format(terminal_node.dep)) 
    file.write("nodes_expanded: {}\n".format(num_explored_nodes-1)) 
    file.write("search_depth: {}\n".format(terminal_node.dep)) 
    file.write("max_search_depth: {}\n".format(max_search_depth)) 
    file.write("running_time: {:.8f}\n".format(tock - tick)) 
    file.write("max_ram_usage: {:.8f}\n".format(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1.0/1000000)) 
    file.close() 

    #print("Path to goal is {}".format(path_to_goal))
    #print("Search depth is {}".format(terminal_node.dep))
    print("Number of explored nodes: {}, frontier nodes: {}".format(num_explored_nodes, num_frontier_nodes))
    print("Number of expanded nodes: {}".format(num_explored_nodes-1))
    #print("Computation time is {:.8f}".format(tock - tick))
    #print("Ram usage is {:.8f}".format(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1.0/1000000)) 


