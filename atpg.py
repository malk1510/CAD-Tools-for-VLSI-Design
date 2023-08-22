###############################################################
###############################################################
#################automatic Test Pattern Gen####################
###############################################################
###############################################################
#
#STUDENTS Name: Malhar Kulkarni, Kunal Chhabra, Kartikeya Chandra
#Roll Nos: 19D070032, 19D070031, 19D070029
#
#This is the code for the Logic Simulator and atpg on Python
#To implement this, we would be using a custom Netlist format, reminiscent of Spice circuit code
#The syntax for the input files starts off with the number of lines in the program
#This is also just the number of nodes in the Directed acyclic graph to form, or just the total number of inputs and componenents.
#
#Syntax for each line in netlist:
#
#<component> <number of inputs> <label of node> <inputs>
#
#Here, the component can be and/or/not/in (we're only going to use and, or, not gates in our logic simulator)
#where 'in' just represents that this is an input node, and will have no previous nodes.
#So, the syntax for in will be:
#
#in 1 <label of input> <boolean input 0/1>
#
#Note that each input will just be a single bit.
#For all other components, the inputs would just be the labels of the required inputs into any given component
#
#Here is an example of a netlist file to find the XOR of two nodes.
#
#7 //this is the number of input nodes
#in 1 0 0
#in 1 1 1
#not 1 2 0
#not 1 3 1
#and 2 4 0 3
#and 2 5 1 2
#or 2 6 4 5
#
#Now, we would need some more input to generate the output.
#This is done using the following syntax:
#
#<number of outputs>
#<list of nodes to output>
#
#In our previous case, we need to output node 6, and so, we simply write the following:
#
#7
#in 1 0 0
#in 1 1 1
#not 1 2 0
#not 1 3 1
#and 2 4 0 3
#and 2 5 1 2
#or 2 6 4 5
#1
#6
#
#This will give an output of 1
#However, for the atpg, we are also using the nor and nand gates, along with a few extra lines to indicate the input and output nodes of the graph
#and also, a last line for the stuck-at testing problem that we need to solve.
#
#Here is the full Netlist file which would appear when testing the program.
#
#7
#in 1 0
#in 1 1
#not 1 2 0
#not 1 3 1
#and 2 4 0 3
#and 2 5 1 2
#or 2 6 4 5
#primary inputs: 0 1
#primary outputs: 6
#test: 0 (s-a-0) 3
#
#This is the Netlist syntax used to implement the below given PODEM algorithm.
#Plus, although the atpg works for multi-input systems, we weren't able to design the various gate functions like nor, nand, etc; for the five-variable logic system. So, this works specifically for only 2-input gates.


#These are just the gate functions, which also use the five variable logic system.
def and_op(x):
    if (x[0] == '0') or (x[1]=='0'):
        return '0'
    if(x[1] == '1'):
        return x[0]
    if (x[0] == '1'):
        return x[1]
    return 'X'
def or_op(x):
    if (x[0] == '1') or (x[1]=='1'):
        return '1'
    if(x[1] == '0'):
        return x[0]
    if (x[0] == '1'):
        return x[1]
    return 'X'
def not_op(x):
    if x=='1':
        return '0'
    if x=='0':
        return '1'
    if x=='D':
        return '!D'
    if x=='!D':
        return 'D'
    return 'X'
def nor_op(x):
    if (x[0] == '1') or (x[1]=='1'):
        return '0'
    if(x[1] == '0'):
        return not_op(x[0])
    if (x[0] == '1'):
        return not_op(x[1])
    return 'X'
def nand_op(x):
    if (x[0] == '0') or (x[1]=='0'):
        return '1'
    if(x[1] == '1'):
        return not_op(x[0])
    if (x[0] == '1'):
        return not_op(x[1])
    return 'X'

#Implementing DFS to traverse over the nodes in order to find the optimal order of implementation of given operations
def dfs(node, v, adj, visited, funcs):
    if((funcs[node]=='in') or (visited[node])):
        return None
    visited[node] = True
    inputs = []
    for i in adj[node]:
        dfs(i, v, adj, visited, funcs)
        inputs.append(v[i])
    temp_var = v[node]
    if(funcs[node] == 'or'):
        v[node] = or_op(inputs)
    elif(funcs[node] == 'and'):
        v[node] = and_op(inputs)
    elif((funcs[node] == 'not')):
        v[node] = not_op(inputs[0])
    elif(funcs[node] == 'fanout'):
        if(not(v[node] == 'D') and not(v[node] == '!D')):
            v[node] = inputs[0]  
    elif(funcs[node] == 'nand'):
        v[node] = nand_op(inputs)
    elif(funcs[node] == 'nor'):
        v[node] = nor_op(inputs)
    else:
        print("Incorrect character entered")
    if ((temp_var == 'D') and ((v[node] == '1') or (v[node] == 'X'))):
        v[node] = 'D'
    elif ((temp_var == '!D') and ((v[node] == '0') or (v[node] == 'X'))):
        v[node] = '!D'
    return None

#Function to implement traversal from the logic simulator, using DFS
def traverse(adj, funcs, v):
    visited = [False for i in adj]
    n = len(v)
    for i in range(n-1,-1,-1):
        dfs(i,v,adj,visited,funcs)
    return None

#Function to backtrace from a given objective location, to find a PI which satisfies the given objective.
def backtrace(adj, funcs, pi, obj, v):
    objGate = obj[0]
    objVal = obj[1]
    node = objGate
    inversions = 0
    if ((funcs[node]=='not') or (funcs[node]=='nand') or (funcs[node]=='nor')):
        inversions+=1
    while node not in pi:
        for i in adj[node]:
            if(v[i]=='X'):
                node = i
                break
        if ((funcs[node]=='not') or (funcs[node]=='nand') or (funcs[node]=='nor')):
            inversions+=1
    pi_gate = node
    if(inversions %2 == 0):
        pi_val = objVal
    else:
        pi_val = not_op(objVal)
    return [pi_gate, pi_val]


#This function just returns whether or not the 'X' input branch of a D-frontier should become '0' or '1' for non-controllability. 
def objective(func):
    if func is in ['and', 'nor']:
        return '1'
    return '0'

#This is the main function to implement the PODEM algorithm
def podem(adj, v, funcs, test, po, pi):
    pi_st = [] #This is the stack which stores 
    times_tried = {}
    pi_test = {} #This is the test vector to be generated for the PIs
    for i in pi: 
        times_tried[i] = 0
        pi_test[i] = 'X' #initialization of all the PIs
    while True:
        v_temp = v.copy()
        d_front = x_path(adj, funcs, v_temp) #D-Frontline obtained using X-path algorithm
        if not d_front: #If there is no D-frontline at the output
            while len(pi_st)>0: #Take new branch in decision tree
                if (times_tried[pi_st[-1][0]]<2):
                    times_tried[pi_st[-1][0]] +=1
                    pi_test[pi_st[-1][0]] = not_op(pi_test[pi_st[-1][0]])
                    v[pi_st[-1][0]] = pi_test[pi_st[-1][0]]
                    break
                else:
                    pi_st.pop()
            if(len(pi_st)==0):
                return None
        else:
            for i in adj[d_front]: #Take the D-frontline and find the objective required
                if(v_temp[i] == 'X'):
                    obj = [i]
                    obj.append(objective(funcs[d_front])) #This function finds the objective for the circuit 
                    break
            pi_st.append(backtrace(adj, funcs, pi, obj, v_temp)) #Line justification through the backtrace algorithm
            v[pi_st[-1][0]] = pi_st[-1][1] #Update the stack with the new PI obtained by backtracing
            pi_test[pi_st[-1][0]] = pi_st[-1][1] #Update the test vector with a new PI having some given value
            times_tried[pi_st[-1][0]] += 1 
        v_temp = v.copy()
        traverse(adj, funcs, v_temp) #Find the implicants by traversing using the newly updated PIs and the logic simulator
        for i in po:
            if (v_temp[i] == 'D') or (v_temp[i] == '!D'): #If the PO becomes D or D', that is, fault propogation and desensitization occurs, then return the test vector generated
                return pi_test
    return None

#This is the X-path algorithm which finds the D frontiers for any given test vector. Initially, we would let the test node be the D frontier, however, if the other port to the
#same input is not 'X', then the D frontier could be pushed further ahead. If the D frontier does not exist, and there is no PI in the stack, it is not possible to find a test vector
#for the PIs.
def x_path(adj, funcs, v):
    traverse(adj, funcs, v)
    for node in range(len(adj)):
        if(v[node] == 'X'):
            dic = {'1':0, '0':0, 'D':0, '!D':0, 'X':0}
            for i in adj[node]:
                dic[v[i]] += 1
            if (((dic['D']>0) or (dic['!D']>0)) and (dic['X']>0)):
                return node
    return None

#This part is used mainly for input and output of the given logic simulator and atpg
with open('netlist.txt','r') as f:
    n = int(f.readline())    
    funcs = ['' for i in range(n)]
    v = ['X' for i in range(n)]
    adj = [[] for i in range(n)]
    inp_taken = [False for i in range(n)]
    for i in range(n):
        x = f.readline().split()
        node = int(x[2])
        if inp_taken[node]:
            print('Incorrect Input given, pls try again')
            break
        if x[0] == 'in':
            inp_taken[node] = True
            funcs[node] = x[0]
            continue
        inp_taken[node] = True
        funcs[node] = x[0]
        adj[node] = [int(i) for i in x[3:]]
    num_in = int(f.readline())
    pi = [int(i) for i in f.readline().split()]
    num_out = int(f.readline())
    po = [int(i) for i in f.readline().split()]
    test = [int(i) for i in f.readline().split()]
    v[test[0]] = 'D' if test[1] is '0' else '!D'
inp_new = podem(adj, v, funcs, test, po, pi)
print(inp_new)