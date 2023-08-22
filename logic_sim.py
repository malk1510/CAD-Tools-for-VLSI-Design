####################################################
####################################################
#################Logic Simulator####################
####################################################
####################################################
#
#STUDENT Name: Malhar Kulkarni
#Roll No: 19D070032
#
#This is the code for the Logic Simulator on Python
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
#We would be using this Netlist format to implement the logic simulator, example files for which are included in the zip file submitted.

def and_op(x):
    ans = 1
    for i in x:
        ans = (ans and i)
    return ans

def or_op(x):
    ans = 0
    for i in x:
        ans = (ans or i)
    return ans

def not_op(x):
    ans = int(not x)
    return ans

#Implementing DFS to traverse over the nodes in order to find the optimal order of implementation of given operations
def dfs(node, v, adj, visited, funcs):
    if((funcs[node]=='in') or (visited[node])):
        return
    visited[node] = True
    inputs = []
    for i in adj[node]:
        dfs(i, v, adj, visited, funcs)
        inputs.append(v[i])
    if(funcs[node] == 'or'):
        v[node] = or_op(inputs)
    elif(funcs[node] == 'and'):
        v[node] = and_op(inputs)
    elif(funcs[node] == 'not'):
        v[node] = not_op(inputs[0])
    else:
        print("Incorrect character entered")
    return

#This part is used mainly for input and output of the given logic simulator
with open('netlist.txt','r') as f:
    n = int(f.readline())    
    funcs = ['' for i in range(n)]
    v = [0 for i in range(n)]
    adj = [[] for i in range(n)]
    inp_taken = [False for i in range(n)]
    for i in range(n):
        x = f.readline().split()
        node = int(x[2])
        if inp_taken[node]:
            print('Incorrect Input given, pls try again')
            break
        if x[0] == 'in':
            v[node] = int(x[3])
            inp_taken[node] = True
            funcs[node] = x[0]
            continue
        inp_taken[node] = True
        funcs[node] = x[0]
        adj[node] = [int(i) for i in x[3:]]
    visited = [False for i in range(n)]
    for i in range(n-1,-1,-1):
        dfs(i,v,adj,visited,funcs)
    num_out = int(f.readline())
    out_nodes = [int(i) for i in f.readline().split()]
for i in out_nodes:
    with open('output.txt','w') as f:
        f.writeline(str(v[i]))
