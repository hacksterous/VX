
smallPrimes = [ 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 
41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 
107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 
179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 
251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 
331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 
409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 
487, 491, 499]

lSP = len(smallPrimes)

def isprime(x, t = 128):
	"""
	Miller-Rabin primality test.
 
	A return value of False means n is certainly not prime. A return value of
	True means n is very likely a prime.
	"""
	n=int(x)

	if n in smallPrimes:
		return True

	#Miller-Rabin test for prime
	if n==0 or n==1 or n==4 or n==6 or n==8 or n==9:
		return False
 
	if n==2 or n==3 or n==5 or n==7:
		return True

	s = 0
	d = n-1
	while d % 2 == 0:
		d >>= 1
		s += 1
	assert(2**s * d == n-1)
 
	def trial_composite(a):
		if pow(a, d, n) == 1:
			return False
		for i in range(s):
			if pow(a, 2**i * d, n) == n-1:
				return False
		return True  
 
	for i in range(t):#number of trials 
		a = smallPrimes[i % lSP]
		if trial_composite(a):
			return False
	return True  

def isqrtnaive(x):
	#Naive implementation O(n*n)
	#https://cs.stackexchange.com/questions/37596/arbitrary-precision-integer-square-root-algorithm
	n = int(x)
	r = 0
	i = n.bit_length()
	while i >= 0:
		inc = (r << (i+1)) + (1 << (i*2))
		if inc <= n:
			n -= inc
			r += 1 << i
		i -= 1
	return r

def nextprime (n):
	sqrt = int(isqrtnaive(n))
	n = int(n)
	if n <= 1:
		return 2

	if n % 2 == 0:
		n += 1
	for i in range(n, n+sqrt+1, 2):
		#Assume Oppermann's unproven conjecture
		if isprime(i):
			return i
	return 0
