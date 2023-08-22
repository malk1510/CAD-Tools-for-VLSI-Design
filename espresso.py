'''
This is the code to implement the ESPRESSO algorithm for 2-level logic minimization using Heuristics.
Here, we implement three main functions Expand, REDUCE, Irredundant.
The input to this file will simply be a truth table, with the number of literals at the start.
The example input is attached along with this program.

The main logic of this code is to implement the Espresso algorithm, using the cost function to be simply the number of cubes in the covering of the input.
The initial covering f will just comprise of the minterms, and we will not require the complementation method here, as we're given the ON-set, OFF-set and DC-set directly in the input.

Other than that, this algorithm uses the following heuristics for its three main functions:
1. For Expand, we minimize WEIGHTS to find the order of cubes to expand, however, we use the naive approach for expansion of literals.
2. For Reduce, we find the cube with the maximum WEIGHT, and minimally reduce that by finding the supercube of its complement.
3. For Irredundant, we have also sorted the cubes according to weight, to be able to check whether or not a cube should be removed if it is irredundant.

Using these three functions iteratively, until the cost function stops minimizing, we may be able to find a highly accurate (though not 100% optimized) minimum 2-level logic, in only polynomial time.

We also use a ESSENTIaLS function, to find the Essential Prime Implicants of the given input covering, so that we may remove them at the start, and focus only on the remaining implicants.

There is an example attached along with this code. If this code is implemented by keeping the example text file in the same directory as the code, we obtain the set of minimized PIs in 0-1 notation.
In this example, the equation 

f = a'b'c' + a'b'c + a'bc' + a'bc + ab'c'

and upon algebraic minimization, we get:

f = a' + b'c'

So, the output obtained will be: 

11 10 10
10 11 11

Names and roll numbers of students invovled:
1. Malhar Kulkarni - 19D070032
2. Kunal Chhabra - 19D070031
3. Kartikeya Chandra - 19D070029
'''

#This function simply finds the cofactor of a given cover with respect to a given cube
#It returns a new covering, which is the cofactor.
def cofactor(cov, cub):
	inter = []
	for i in cov:
		temp = []
		b = True
		for j in range(len(i)):
			temp.append(int(i[j] and cub[j]))
		for j in range(len(temp)//2):
			if((temp[2*j]==0) and (temp[2*j+1]==0)):
				b = False
		if b:
			inter.append(temp)
	cub = [1-i for i in cub]
	cof = []
	for i in inter:
		cof.append([])
		for j in range(len(cub)):
			cof[-1].append(int(i[j] or cub[j]))
	return cof

#This function just checks if any given cover is a tautology or not.
#Here, we use a recursive algorithm to take cofactors of functions with respect to each literal, one-by-one, and pass them through the same function.
#This function just returns TRUE or False
def tautology(cov):
	if(len(cov) == 0):
		return False

	#If there is only one literal, we stop the recursion.
	if(len(cov[0]) == 2):
		s1 = 0
		s2 = 0
		for i in cov:
			s1 += i[0]
			s2 += i[1]
		if((s1==0) or (s2==0)):
			return False
		else:
			return True
	x1 = []
	x2 = []

	#This part of the function simply iterates through the cover to check for all cubes which would be in either the cofactor of one literal, or that of the not of that literal.
	for i in cov:
		if i[0]==0:
			x1.append(i[2:])
		elif i[1]==0:
			x2.append(i[2:])
		else:
			x1.append(i[2:])
			x2.append(i[2:])
	if((tautology(x1)) and (tautology(x2))):
		return True
	return False

#This is a recursive function which finds the complement of a given function, using the approach similar to the one used to check for tautology.
def complement(f):
	if(len(f) == 0):
		return []
	if(len(f[0] == 2)):
		if(tautology(f)):
			return []
		elif f[0][0]==0:
			return [1,0]
		else:
			return [0,1]
	x0 = []
	x1 = []
	for i in f:
		if i[0]==0:
			x0.append(i)
		else:
			x1.append(i)
	t0 = complement(x0) #The formula for complement is f' = af'_a + a'f'_a', so we find the two complements of the cofactors.
	t1 = complement(x1)
	for i in range(len(t0)):
		t0[i] = [1,0] + t0[i]
	for i in range(len(t1)):
		t1[i] = [0,1] + t1[i]
	return t0+t1

#This function simply finds the weights of each cube of a cover.
def find_weights(f):
	sums = []
	weights = []
	for i in range(len(f[0])):
		sm = 0
		for j in range(len(f)):
			sm += f[j][i]
		sums.append(sm)
	for i in range(len(f)):
		sm = 0
		for j in f[i]:
			sm += j*sums[i]
		weights.append(sm)
	return weights

#This functions finds and returns the EPIs in a given cover. Note that this does not require all the primes. It only requires the list of prime implicants.
#The algorithm is to simply remove each PI from the cover, and see if the remaining ON-set, along with the DC-set, intersects the removed PI entirely.
#If the PI is intersected entirely, that is the cofactor is a tautology, then the PI is not essential.
def essential(f,d):
	e = []
	for i in range(len(f)):
		x = []
		for j in f:
			if not(j==f[i]):
				x.append(j)
		x += d
		cof = cofactor(x,f[i])
		if not(tautology(cof)):
			e.append(f[i])
	return e

#This is a naive method of expansion, where we expand the literals of a given cube one-by-one, and see if the new cube intersects with the OFF-set or not.
def naive_exp(cub,r,depth):
	for i in range(len(cub)//2):
		t1 = cub[2*i]
		t2 = cub[2*i+1]
		cub[2*i] = 1
		cub[2*i+1] = 1
		if(cofactor(r,cub) == []):
			continue
		else:
			cub[2*i] = t1
			cub[2*i+1] = t2
	return cub

#This is the expand function, one of the three main functions to be used.
#This function expands all the prime implicants in the cover, and removes any redundant prime implicants.
def expand(f, r):
	w = find_weights(f)
	f = [i for _,i in sorted(zip(w,f))] #arranging the cubes in ascending order of weights
	it = 0
	remove = []
	while(it < len(f)): #Iterating through all the cubes in the cover.
		if(f[it] in remove): #If any prime implicant is redundant, simply remove it.
			del f[it]
			continue
		depth = 0
		f[it] = naive_exp(f[it], r, depth) #Expanding the chosen cube
		for i in range(len(f)):
			if(i!=it):
				if not(tautology(cofactor([f[it]], f[i]))): #Checking all other cubes to see if they lie entirely within the expanded implicant or not.
					remove.append(f[i])
		it+=1
	return f

#This function reduces the covers, using the formula given in the slides.
#However, the reduction also uses the weight heuristic to decide the order of cubes to reduce.
def reduce(f,d):
	w = find_weights(f)
	f = [i for _,i in sorted(zip(w,f), reverse = True)]
	for i in range(len(f)):
		q = f + d
		q.remove(f[i])
		q = complement(cofactor(q,f[i]))
		arr = []
		for j in range(len(q[0])):
			x_tmp = 0
			for k in range(len(q)):
				x_tmp = int(x_tmp or q[k][j])
			arr.append(x_tmp)
		for j in range(len(f[i])):
			f[i][j] = int(f[i][j] and arr[j])
	return f

#This function simply removes irredundant cubes by checking if upon removing one of the cubes, the union of the other cubes would intersect completely (cofactor is tautology) or not
def irredundant(f,d):
	w = find_weights(f)
	f = [i for _,i in sorted(zip(w,f), reverse = True)]
	it = 0
	while(it<len(f)):
		x = [t for t in f]
		x.remove(f[it])
		x += d
		if(tautology(cofactor(x,f[it]))):
			f.remove(f[it])
		else:
			it += 1
	return f

#This function is for the input and output and for the direct implementation of the ESPRESSO algorithm.
def main():
	f = [] #ON set
	r = [] #OFF set
	d = [] #DC set

	#INPUT
	with open('read_file.txt') as file:
		n = int(file.readline())
		for _ in range(2**n):
			st = file.readline().split()
			x = list(st[0])
			x_temp = []
			for i in x:
				if i=='0':
					x_temp.append(1)
					x_temp.append(0)
				else:
					x_temp.append(0)
					x_temp.append(1)
			if(st[1] == '1'):
				f.append(x_temp)
			elif(st[1] == '0'):
				r.append(x_temp)
			elif(st[1] == 'x'):
				d.append(x_temp)

		#Length of the ON-set, that is, number of cubes in the cover will be our cost function for heuristic minimization.
		l1 = len(f) 
		f = expand(f,r)
		f = irredundant(f,d)
		e = essential(f,d)
		for i in e:
			f.remove(i) #Remove EPIs from the ON-set
		d += e
		while((len(f) < l1) and (len(f) > 0)):
			f = reduce(f,d)
			f = expand(f,r)
			f = irredundant(f,d)

		f += e #Include the EPIs back into the ON-set.

		#OUTPUT
		for i in f:
			for j in range(len(i)//2):
				print(str(i[2*j]) + str(i[2*j+1]), end = ' ')
			print()
	return

main()
