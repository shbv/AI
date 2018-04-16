from random import randint
from BaseAI_3 import BaseAI
from Displayer_3  import Displayer
import time
from math import log
import os

"""
Heuristic functions for the utility of node
"""

"""
Smoothness heuristic
"""
def get_smoothness(grid):
    
    #global DEBUG

    total = 0
    all_dirs = [[0,1],[1,0],[0,-1],[-1,0]]
    for i in range(4):
        for j in range(4):
            currpos = (i,j)
            cellval = grid.getCellValue(currpos)
            if cellval == 0:
                continue
            currval = log(cellval,2)
            #if DEBUG:
            #    print("currpos(i,j) is {}, cellval is {}, currval is {}".format(currpos,cellval,currval)) 
            for u,v in all_dirs:
                #if DEBUG:
                #    print("Direction(u,v) is {} {}".format(u,v)) 
                p = i+u 
                q = j+v
                found = 0
                while 0 <= p <= 3:
                    while 0 <= q <= 3:
                        npos = (p,q)
                        cellval = grid.getCellValue(npos)
                        if cellval == 0:
                            pass 
                        else:  
                            nval = log(cellval,2)
                            total += -abs(nval - currval)
                            found = 1
                            #if DEBUG:
                            #    print("\tnpos(p,q) is {}, cellval is {}, nval is {}, total is {}".format(npos,cellval,nval,total)) 
                            break
                        if v == 0:
                            break
                        else:
                            q += v
                    if found:
                        break
                    if u == 0:
                        break
                    else:
                        p += u
    #if DEBUG:
    #    print("Smoothness is {}".format(total))
    return total


"""
Monotonicity heuristic
"""
def get_monotonicity(grid):
    
    #global DEBUG

    total_vdir = [0, 0]
    total_udir = [0, 0]
    
    # up, down:
    for u in range(4):
        v = 0
        v_next = 1
        while v_next <= 3:
            #while v_next <=3 and grid.getCellValue((u,v_next)) == 0:
            while v_next <=3 and grid.getCellValue((u,v_next)) < 0.1:
                v_next += 1
            if v_next == 4:
                v_next -= 1
            currval = 0
            nextval = 0
            currcellval = grid.getCellValue((u,v))
            nextcellval = grid.getCellValue((u,v_next))
            #if currcellval == 0 or nextcellval == 0:
            if 0:
                pass
            else:
                if currcellval != 0:
                    currval = log(currcellval,2)
                if nextcellval != 0:
                    nextval = log(nextcellval,2)
                if nextval > currval:
                    total_vdir[0] += -(nextval - currval)
                else:
                    total_vdir[1] += -(currval - nextval)  
                
            v = v_next
            v_next += 1

    # left, right:
    for v in range(4):
        u = 0
        u_next = 1
        while u_next <= 3:
            #while u_next <=3 and grid.getCellValue((u_next,v)) == 0:
            while u_next <=3 and grid.getCellValue((u_next,v)) < 0.1:
                u_next += 1
            if u_next == 4:
                u_next -= 1
            currval = 0
            nextval = 0
            currcellval = grid.getCellValue((u,v))
            nextcellval = grid.getCellValue((u_next,v))
            #if currcellval == 0 or nextcellval == 0:
            if 0:
                pass
            else:
                if currcellval != 0:
                    currval = log(currcellval,2)
                if nextcellval != 0:
                    nextval = log(nextcellval,2)
                if nextval > currval:
                    total_udir[0] += -(nextval - currval)
                else:
                    total_udir[1] += -(currval - nextval)  

            u = u_next
            u_next += 1
    
    # total:
    total = max(total_udir[0], total_udir[1]) + max(total_vdir[0], total_vdir[1])
    #if DEBUG:
    #    print("Monotonicity is {}".format(total))
    return total

"""
Average score of board heuristic
"""
def get_avg(grid):

    #global displayertemp
    #displayertemp.display(grid)
    
    total = 0
    num = 0
    for i in range(4):
        for j in range(4):
            currpos = (i,j)
            currcellval = grid.getCellValue(currpos)
            if currcellval > 0.01:
                #print("i {}, j {}, currcellval {}".format(i,j,currcellval))
                total += log(currcellval,2)
                num += 1
    avg = total/num
    #print("num {}, total {}, total grid avg is {}".format(num,total,avg))
    return avg



"""
Minimax algorithm functions start here:
"""


"""
Utility function using various heuristics
"""
def get_utility(grid, move):
    
    #global weights

    # get various heuristics
    num_avail_cells = len(grid.getAvailableCells())
    if num_avail_cells > 0:
        num_avail_cells = log(num_avail_cells,2)
    max_tile_val = log(grid.getMaxTile(),2)
    smoothness = get_smoothness(grid)
    monotonicity = get_monotonicity(grid)
    avg = get_avg(grid)
    smoothness = smoothness/avg
    monotonicity = monotonicity/avg
    
    # weights for heuristics
    weights = [12.0, 2.0, 0.05, 3.1, 0.0]    
    wc = weights[0]  
    wmt = weights[1]
    ws = weights[2]
    wm = weights[3]
    wa = weights[4]
    #print("weights are {} {} {} {} {}".format(wc,wmt,ws,wm,wa))

    # Get effective utility from all these heuristic contributions
    num_avail_cells += 0.001
    num_avail_cells_contr = wc * (1.0/num_avail_cells)
    max_tile_val_contr = wmt * max_tile_val
    smoothness_contr = ws * smoothness
    monotonicity_contr = wm * monotonicity
    avg_contr = wa * avg
    max_util = num_avail_cells_contr + max_tile_val_contr + smoothness_contr + monotonicity_contr  
    
    #print("num_avail_cells {}, max_tile_val {}, smoothness {}, monotonicity {}, Max_util {}".format(num_avail_cells, max_tile_val, smoothness, monotonicity, max_util))
    #print("move: {}: num_avail_cells_contr {}, max_tile_val_contr {}, smoothness_contr {}, monotonicity_contr {}, avg_contr {}, Max_util {}".format(move,num_avail_cells_contr, max_tile_val_contr, smoothness_contr, monotonicity_contr, avg_contr, max_util))
    #if DEBUG:
    #    print("found terminal state - max util is {}".format(max_util))

    return max_util

"""
Terminal test for current node - based on time constraint and max_depth
"""
def terminal_test(grid, prevtime, depth):
    currtime = time.clock()
    timeLimit = 0.012
    maxdepth = 8
    #if len(grid.getAvailableCells()) > 9:
    #    if grid.getMaxTile() < 32:
    #        maxdepth = 8
    #    if grid.getMaxTile() > 128:
    #        timeLimit = 0.012
    if (len(grid.getAvailableMoves()) == 0) or (time.clock() - prevtime) > timeLimit or depth > maxdepth:
        return True
    else:
        return False

"""
Get min utility among child nodes
"""
def minimize(grid, alpha, beta, prevtime, depth, move):
    
    #global displayertemp
    #global DEBUG
    #print("depth is {}".format(depth))

    # Terminal test
    if terminal_test(grid, prevtime, depth):
        return None,get_utility(grid,move),depth
    
    min_util = float('inf')
    min_move = None
    max_depth_from_this_node = float('-inf')

    # Computer AI moves
    positions = grid.getAvailableCells()
    #if DEBUG:
    #    print("Available positions is {}".format(positions))
    tile_values = [2,4]  
    if isinstance(positions,tuple):
        positions = [positions]
    for pos in positions:
        for value in tile_values:
            gridCopy = grid.clone()
            gridCopy.setCellValue(pos,value)
            #if DEBUG:
            #    print("pos:{},val:{}".format(pos,value))
            #    displayertemp.display(gridCopy)
            
            # Maximize child node (i.e player's play)
            _ , util, maxdepth = maximize(gridCopy, alpha, beta, prevtime, depth+1, move)
            
            # Update min util if util is smaller
            if util < min_util:
                min_util = util
                min_move = None
            # Just for tracking depth that is reaching within time constraints
            if maxdepth > max_depth_from_this_node:
                max_depth_from_this_node = maxdepth
            # Alpha-beta pruning
            if min_util <= alpha:
                return min_move, min_util, max_depth_from_this_node
            # Update beta if min util is smaller
            if min_util < beta:
                beta = min_util

    return min_move, min_util, max_depth_from_this_node
    
"""
Get max utility among child nodes using maximize 
"""
def maximize(grid, alpha, beta, prevtime, depth, move):

    #global displayertemp
    #global DEBUG
    #print("depth is {}".format(depth))

    # Terminal test
    if terminal_test(grid, prevtime,depth):
        return None,get_utility(grid,move),depth
    
    max_util = -float('inf')
    max_move = None
    max_depth_from_this_node = -float('inf')

    # PlayerAI moves
    moves = grid.getAvailableMoves()
    #if DEBUG:
    #    print("Available moves is {}".format(moves))
    for move in moves:
        gridCopy = grid.clone()
        gridCopy.move(move)
        #if DEBUG:
        #    print("Move:{}".format(move))
        #    displayertemp.display(gridCopy)
       
        # Minimize child node (i.e opponent's play)
        _ , util, maxdepth = minimize(gridCopy, alpha, beta, prevtime, depth+1, move)

        # Update max_util if util is larger
        if util > max_util:
            max_util = util
            max_move = move
        # Just for tracking depth that is reaching within time constraints
        if maxdepth > max_depth_from_this_node:
            max_depth_from_this_node = maxdepth
        # Alpha-beta pruning
        if max_util >= beta:
            break
        # Update alpha if max util is larger
        if max_util > alpha:
            alpha = max_util

    return max_move, max_util, max_depth_from_this_node 

"""
Minimax function 
"""
def minimax_decision(state, prevtime, depth):
    
    #global weights    
    #weights = w
    #alpha = -float('inf'), beta = float('inf')
    max_move , _ , maxdepth_from_this_node = maximize(state, -float('inf'), float('inf'), prevtime, depth, 0)
    return max_move

"""
Main PlayerAI getMove method that uses minimax algorithm
"""

class PlayerAI(BaseAI):

    def getMove(self, grid):
        moves = grid.getAvailableMoves()
        #if DEBUG:
        #    print("Start available moves is {}".format(moves))
        prevtime = time.clock()
        move = minimax_decision(grid, prevtime, 0) 
        if move != None:
            return move
        else:
            return moves[randint(0, len(moves) - 1)]


