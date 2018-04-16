"""
Modules
"""
import sys
import os
import collections


"""
Class for sudoku grid
"""
class Sudoku_grid:
    
    def __init__(self,input_grid,assignment):
        
        ## Set var values for each cell, its domain and its neighbors
        
        ## Cells:
        rid = 'ABCDEFGHI'
        cid = '123456789'
        self.rid = rid
        self.cid = cid
        cells = [x+y for x in rid for y in cid]
        self.cells = cells        
        #print("Cells in sudoku are:\n{}".format(self.cells))

        ## Initial assignment:
        self.assignment = dict(zip(cells,input_grid))
        #print("Initial assignment is:\n{}".format(self.assignment))

        ## Neighbor cells for each cell:
        rows_cols_boxs = ([[x+y for x in rid for y in ctemp] for ctemp in cid] +
                            [[x+y for x in rtemp for y in cid] for rtemp in rid] +
                            [[x+y for x in rtemp for y in ctemp] for rtemp in ('ABC','DEF','GHI') for ctemp in ('123', '456', '789')])
        neighbors_temp = dict((c, [rcb for rcb in rows_cols_boxs if c in rcb]) for c in cells)
        neighbors = dict((c, sorted(set(sum(neighbors_temp[c],[]))-set([c]))) for c in cells)
        self.neighbors = neighbors
        #print("neighbors are:\n{}".format(neighbors))

        ## Domain for each cell: (for already assigned cells, just keep its value so that display debug is easier)
        domain = {}
        values = ['1','2','3','4','5','6','7','8','9']
        for c in cells:
            if self.assignment[c] == '0':
                domain[c] = values.copy() 
            else:
                domain[c] = list(self.assignment[c])
        self.domain = domain
        #print("Domain for each cell is:\n{}".format(self.domain))

    # Initialize domain remaining for each cell in sudoku grid
    def initialize_domain_remaining(self):
        self.domain_remaining = {c: self.domain[c].copy() for c in self.cells}
        #print("Domain remaining for each cell is:\n{}".format(self.domain_remaining))

    # Display sudoku grid
    def display(self,assignment):
        #print("assignment is {}".format(assignment))
        assignment_temp = {c: assignment[c] for c in assignment}
        for c in self.cells:
            assignment_temp[c] = ''.join(assignment_temp[c])  
        w = 1+max(len(assignment_temp[c]) for c in self.cells)
        l = '+'.join(['-'*(w*3)]*3)
        for row in self.rid:
            print(''.join(assignment_temp[row+col].center(w)+('|' if col in '36' else '') for col in self.cid))
            if row in 'CF': 
                print(l)
    
    # Basic constraint for any two suduko cell values that are neighbors
    def constraint_met(self,ci_value,cj_value):
        #print("constraint met function: {}(type:{}),{}(type:{})".format(ci_value,type(ci_value),cj_value,type(cj_value)))
        if ci_value != cj_value:
            return True
        else:
            return False
            
    # Check if all cells have domain_remaining as single value instead of list
    def check_if_solved(self):
        if all(len(self.domain_remaining[c])==1 for c in self.cells):
            return True
        else:
            return False          

    # Check if all cells have values assigned
    def check_if_solved_bts(self):
        if all(self.assignment[c]!='0' for c in self.cells):
            return True
        else:
            return False  
    
    # Check if sudoku is solved with no conflicts - sanity check
    def check_if_solved_noconflicts(self):
        for ci in self.cells:
            x = self.assignment[ci]
            for cj in self.neighbors[ci]:
                y = self.assignment[cj]
                if not sudoku.constraint_met(x,y):
                    return False
        return True
    
    # Update assignment from domain remaining values in each cell
    def update_assignment(self):
        for c in self.cells:
            self.assignment[c] = self.domain_remaining[c]

    # Grid to string for print   
    def grid_to_string(self):
        result = []
        for r in self.rid:
            for c in self.cid:
                result.append(''.join(self.assignment[r+c]))
        result = ''.join(result)
        #print("result is {}".format(result))
        return result

"""
AC3 algorithm function
"""
def AC3_algo(sudoku):

    # initialize queue with all possible arcs
    ac3_queue = collections.deque((c,n) for c in sudoku.cells for n in sudoku.neighbors[c])
    print("Length of AC3 queue is: {}".format(len(ac3_queue)))
    
    # for debug
    #debug_revised = 0

    # AC3 algo
    while len(ac3_queue) > 0:
        #print("\n==Length of AC3 queue is: {}==".format(len(ac3_queue)))
        ci, cj = ac3_queue.popleft()
        #print("\n==Processing arc: {},{} with domains {},{}\n".format(ci,cj,sudoku.domain_remaining[ci],sudoku.domain_remaining[cj]))
        if AC3_revise(sudoku, ci, cj):
            #print("{}'s domain has been revised to {}".format(ci,sudoku.domain_remaining[ci]))
            #debug_revised += 1
            if len(sudoku.domain_remaining[ci]) == 0:
                return False
            for ck in sudoku.neighbors[ci]:
                if ck != cj:
                    #print("Adding arc: {},{}".format(ci,ck))
                    ac3_queue.append((ci,ck))
        # debug:
        #print("assignments is:")
        #sudoku.display(sudoku.assignment)
        #print("orig domain is:")
        #sudoku.display(sudoku.domain)
        #print("domain remaining is:")
        #sudoku.display(sudoku.domain_remaining)
        #if debug_revised == 20:
        #    os._exit(1)

    return True

## Revise function in AC3
def AC3_revise(sudoku,ci,cj):
    
    revised = False
    for x in sudoku.domain_remaining[ci]:
        if all(not sudoku.constraint_met(x,y) for y in sudoku.domain_remaining[cj]):
            #print("Cell {} value {} has conflict with any value in Cell {} values {}".format(ci,x,cj,sudoku.domain_remaining[cj]))
            sudoku.domain_remaining[ci].remove(x)
            revised = True
    #print("Is {} revised? {}".format(ci,revised))
    return revised

"""
Inference and Forward checking for conflicts that could be seen in neighbor cells
"""
def Inference_FC(sudoku, ci, x, domain_pruned):
    
    for cj in sudoku.neighbors[ci]:
        if len(sudoku.domain_remaining[cj]) > 1:
            for y in sudoku.domain_remaining[cj]:
                if x==y:
                    #print("Pruning domain for {} value {} based on this assignment {} {}.".format(cj,y,ci,x))
                    domain_pruned.append((cj,y))
                    sudoku.domain_remaining[cj].remove(y)
            if len(sudoku.domain_remaining[cj]) == 0:
                #print("This assignment {} {} leads to conflict for {} {}. FC failed".format(ci,x,cj,sudoku.domain_remaining[cj]))
                return False
    #print("Pruned domain is {}".format(domain_pruned))
    # FC passed if here
    return True
                
"""
Backtrack search algorithm (recursive)
"""
def Backtrack_search(sudoku):

    # Check if solved
    if sudoku.check_if_solved_bts(): 
        print("Sudoku is solved")
        return True
    
    # Select unassigned variable using MRV heuristic
    cell = Select_unassigned_variables(sudoku)
    #print("Choosing cell {} using MRV heuristic".format(cell))

    # Depth first search for assignments
    for x in sudoku.domain_remaining[cell]:
        
        #print("Choosing value {} for {}".format(x,cell))

        # Check if consistent with all neighbors
        consistent = True
        for cj in sudoku.neighbors[cell]:
            if all(not sudoku.constraint_met(x,y) for y in sudoku.domain_remaining[cj]):
                #print("The assignment {} {} is not consistent for {} {}".format(cell,x,cj,sudoku.domain_remaining[cj]))
                consistent = False
                break 

        # If no consistency issues:
        # prune the domain of current cell and its neighbors and backtrack search on new sudoku board state.
        if consistent:
        
            #print("This assignment is consistent with its neighbors currently. Trying further..")

            ## Trying this assignment. Bookkeeping to restore domain remaining later.
            domain_pruned = [(cell,val) for val in sudoku.domain_remaining[cell] if val != x]
            sudoku.domain_remaining[cell] = [x]
            sudoku.assignment[cell] = x
            #print("Pruned domain is {}".format(domain_pruned))
            #print("current assignment - after assignment before IFC")
            #sudoku.display(sudoku.assignment)
            #print("current domain remaining - after assignment before IFC")
            #sudoku.display(sudoku.domain_remaining)
            
            ## Do inference on neighbors to check if this is ok
            if Inference_FC(sudoku,cell,x,domain_pruned):
                
                # Inference passed
                #print("Pruned domain is {}".format(domain_pruned))
                #print("current domain remaining - after IFC:")
                #sudoku.display(sudoku.domain_remaining)      

                ## Didnt terminate, OK. Do next level of assignment
                result = Backtrack_search(sudoku)
                #print("result is {}".format(result))
                if result:
                    # Still didnt terminate. This assignment works. Return.
                    #print("BTS passed for {} {}".format(cell,x))
                    return True
                
            ## Not OK. This assignment didnt work. Remove assignment and restore domain_remaining
            #print("BTS failed for {} {}. Restoring domain_remaining and assignment".format(cell,x))
            sudoku.assignment[cell] = '0' 
            #print("Pruned domain is {}".format(domain_pruned))
            for c,val in domain_pruned:
                #print("Pruned domain c,val {} {}".format(c,val))
                sudoku.domain_remaining[c].append(val)
            
            #print("current assignment - after restore:")
            #sudoku.display(sudoku.assignment)
            #print("current domain remaining - after restore:")
            #sudoku.display(sudoku.domain_remaining)            
            #os._exit(1)

    #print("No assignment found in this subtree. BTS returning false")
    return False


# Select unassigned variables for BTS using MRV heuristic
def Select_unassigned_variables(sudoku):

    #print("Domain remaining:")
    #sudoku.display(sudoku.domain_remaining)            
    #for c in sudoku.cells:
    #    print("{}: {}".format(c,sudoku.domain_remaining[c]))
    mincell = min([c for c in sudoku.cells if sudoku.assignment[c] == '0'], key=lambda c: len(sudoku.domain_remaining[c]))  
    #print("Min remaining value cell: {}, value: {} ".format(mincell,len(sudoku.domain_remaining[mincell])))
    return mincell

"""
Main 
"""
if __name__ == '__main__':
    
    # Get the input grid
    if len(sys.argv) != 2:
        print("Wrong number of arguments given: " + len(sys.argv))
        os._exit(1)
    input_grid = sys.argv[1]
    print("Input grid is " + input_grid)

    # Output file
    fp = open("output.txt","w") 
    #fp = open("output.txt","a") 

    # Initial assignment and create sudoku object
    assignment = {}
    sudoku = Sudoku_grid(input_grid, assignment)
    print("Initial assignment:")
    sudoku.display(sudoku.assignment)
    # Initialize domain remaining to keep track of current available values
    print("Initialize domain remaining:")
    sudoku.initialize_domain_remaining()
    sudoku.display(sudoku.domain_remaining)

    # Try AC3
    status = AC3_algo(sudoku)
    print("AC3 domain remaining is")
    sudoku.display(sudoku.domain_remaining)
    if status and sudoku.check_if_solved():
        print("AC3 solved it. Assignments are:")
        sudoku.update_assignment()
        sudoku.display(sudoku.assignment)
        result = sudoku.grid_to_string()
        fp.write("{} AC3\n".format(result))
    else:
        # Try BTS
        print("AC3 couldn't solve it. Trying BTS")
        print("Initializing domain remaining again:")
        sudoku.initialize_domain_remaining()
        sudoku.display(sudoku.domain_remaining)
        status = Backtrack_search(sudoku)
        status1 = sudoku.check_if_solved_noconflicts()
        if status:
            print("BTS solved it. (There are no conflicts?: {}). Assignments are:".format(status1))
            sudoku.display(sudoku.assignment)
            result = sudoku.grid_to_string()
            fp.write("{} BTS\n".format(result))
        else:
            print("BTS couldnt solve it too")
    fp.close()
