#(c) 2019 Anirban Banerjee

####from mpcap import *
from apbf import *
from u5angaPC import *
import sys
import os
import time
from datetime import date
from primes import *

#future proofing!
try:
	sys.set_int_max_str_digits(0)
except:
	pass

def zfill (s, w):
	#print ("ZFILL 1. string is ", s, "width is ", w)
	if w < 0:
		return s
	return ('0'*w + s)[-w:]

def dPY(*args, lvl=0):
	s = ''
	for arg in args:
		s = s + ' ' + str(arg)
	if lvl > 10:
		print(s)

class VexError (Exception):
	pass

class UnhandledVexError (Exception):
	pass

class VexMicroPC ():

	def bfopdigits (self):
		return APBF_LAST_OP_DIGITS_LEN

	def cmpop (self, operator='<', lvalue=0):
		#Compare Operation
		if operator == '<':
			if self.look == '=':
				self.match('=')
				value, width, base = self.expr()
				#less than or equals operator
				try: 
					value = (lvalue <= value)
				except (NameError, TypeError, ValueError, AttributeError, OverflowError, SyntaxError):
					self.sher ("Error: LTEQ operation returned error.")
					value = mpap(0)
			else:
				#less than operator
				#we have to prove that in all possible values of lvalue and value,
				#lvalue is smaller than value
				self.sw()
				#handle this error specially
				if self.look == '=':
					self.sher ("Error: expected LTEQ operator '<='.")
					return mpap(0)
				value, width, base = self.expr()
				#dPY ("for LT op, value is ", value)
				try: 
					value = (lvalue < value)
				except (NameError, TypeError, ValueError, AttributeError, OverflowError, SyntaxError):
					self.sher ("Error: LT operation returned error.")
					return mpap(0)
			#endif =
		elif operator == '>':
			if self.look == '=':
				self.match('=')
				value, width, base = self.expr()
				#greater than or equals operator
				try: 
					value = (lvalue >= value)
				except (NameError, TypeError, ValueError, AttributeError, OverflowError, SyntaxError):
					self.sher ("Error: GTEQ operation returned error.")
					return mpap(0)
			else:
				#greater than operator
				self.sw()
				#handle this error specially
				if self.look == '=':
					self.sher ("Error: expected GTEQ operator '>='.")
					return mpap(0)
				value, width, base = self.expr()
				try: 
					value = (lvalue > value)
				except (NameError, TypeError, ValueError, AttributeError, OverflowError, SyntaxError):
					self.sher ("Error: GT operation returned error.")
					return mpap(0)
			#endif =

		elif operator == '=':
			# '==' has already been matched
			value, width, base = self.expr()
			try:
				#dPY("Equality operator: lvalue ----->", lvalue, "type is ", type(lvalue))
				#dPY("Equality operator: value ----->", value, "type is ", type(value))
				value = (lvalue == value)

			except (NameError, TypeError, ValueError, AttributeError, OverflowError, SyntaxError):
				self.sher ("Error: equality operation returned error.")
				return mpap(0)
			
		elif operator == '!':
			# '!=' has already been matched
			value = self.expr()[0]
			try: 
				value = (lvalue != value)
			except (NameError, TypeError, ValueError, AttributeError, OverflowError, SyntaxError):
				self.sher ("Error: inequality operation returned error.")
				return mpap(0)

		return value

	def _factorial (self, n):
		#print('n is ', n)
		if n <= 1:
			return 1
		else:
			fac = 1
			while n > 1:
				fac *= n
				n -= 1
			#print ("fact is ", fac)
			return fac
	
	def dec2xxx(self, n, dec2what='h'):
		#returns string repr of number converted
		#to base 'dec2what'
		if dec2what == 'h':
			return (hex(n)[2:])
		elif dec2what == 'b':
			return (bin(n)[2:])
		elif dec2what == 'o':
			return (oct(n)[2:])

	def ldst (self):
		#hashes/dicts for symbol table
		self.abv = [
		#all BuiltIn Variables
								'True',
								'False'
								]
		#symbol table value
		self.stv = {
								'True': mpap(1),
								'False': mpap(0),
								'ans': mpap(0)
								}
		
		#symbol table width
		self.stw = {			
								'True': 0,
								'False': 0,
								'ans': 0
								}
		
		#base
		self.stb = {
								'True':'b',
								'False':'b',
								'ans': 'd'
								}
		#value is rounded
		self.vir = {
								'ans': False
								}

	def __init__ (self):
		self.mpapFunctionsList = [
				'ln',
				'log10'
				'log',
				'sqrt',
				'exp',
				'digits',
				'tan',
				'sin',
				'cos',
				'tanh',
				'sinh',
				'cosh',
				'atan',
				'asin',
				'acos',
				'atanh',
				'asinh',
				'acosh'
			]
				
		#comma as digit separator is OK, but
		#when parsing parameters passed to a function,
		#comma is the parameter separator
		self.dcn = False #disable Comma In Numbers
		self.envre = True #enable new var ref error
		self.rndpad = 2 #extra precision digits
		self.rnd = 23 #round to n decimals
		self.slz = True #suppress leading zeros
		self.fhhp = True #factorial Has Highest Precedence
		self.aaw = True #automatically Adjust Width
		self.axf = True #allow Experimental Features
		self.iris = -1 #infinite Recursion InputStr Ptr Snapshot
		self.excc = 0 #expression Call Counter
		self.dstd = True #for Decimal Suppress TickD
		self.defw = 32 #default Width
		self.showws = True #show Warnings
		self.enn = '' #Error notification
		self.wnn = [] #Warning notification
		self.inps = ''   #input Str is a READONLY variable
		self.insp = 0 #input str pointer
		self.look = ''
		self.cxt = 0
		
		self.ca = [] #command array
		self.ra = []
		self.mcas = 8 #max Command Array Size
		self.sdp()

		self.ldst()

		self.u5 = u5angaPC()
		
		self.miscelFunctionsList = [
				'nxp',
				'nextprime',
				'isp',
				'isprime',
				'tithi',
				'random',
				'setzone',
				'getzone',
				'sun',
				'ltithi',
				'today',
				'day',
				'factors',
				'int',
				'atan2',
				'pi',
				'e',
				'do',
				]

		sprec(self.rnd + self.rndpad)
	#enddef

	def degrees (self, val):
		degrees (val)

	def sdp (self):
		#set default parameters
		self.ep = True
		self.sci = False
		self.eng = False
		self.ins = False
		self.wns = False
		self.tba = True #take Base From Assignment
		self.twa = True #take Width From Assignment
		MPBF_DEGREES_MODE = self.deg = False #degrees mode. Default is radians

	def e (self, x):
		if x == []:
			return mpap(1).exp()
		return x[0].exp()

	def pi (self, x):
		if x == []:
			return mpap(1).pi()
		return x[0].pi()

	def atan2(self, l):
		x, y = l
		#dPY ("x=", x)
		#dPY ("y=", y)
		#dPY ("atan2=", x.atan2(y))
		return x.atan2(y)

	def int(self, l):
		if l == []:
			return 0
		return l[0].int()

	def endian(self, num, boundary=8):
		boundary = int(boundary)
		if boundary == 0:
			boundary = 8;
		copy = num
		result = mpap(0)
		while copy != 0:
			result <<= boundary
			result |= (copy & ((1<<boundary)-1))
			copy >>= boundary

		return result

	def isprime (self, l):
		return self.isp(self, l)

	def isp (self, l):
		if len(l) != 1:
			self.sher ("Error: wrong or missing parameters.")
			return False
		else:
			try:
				n = int(l[0])
			except:
				self.sher ("Error: wrong or missing parameters.")
				return False
		return isprime(n)
		#return gmpy2.is_prime(n)

	def nextprime (self, l):
		return self.nxp(self, l)

	def nxp (self, l):
		if len(l) != 1:
			self.sher ("Error: wrong or missing parameters.")
			return False
		else:
			try:
				n = int(l[0])
			except:
				self.sher ("Error: wrong or missing parameters.")
				return False
		return mpap(nextprime(n))
		#return mpap(gmpy2.next_prime(n))

	def ltithi (self, l):
		if l == []:
			yy, mm, dd = str(date.today()).split('-')
			startyr = int(yy)
			startm = 1
			endm = 12
			howmany = 30
		else:
			try:
				if len (l) == 1:
					startyr = l[0]
				elif len (l) == 2:
					startyr, startm = l
					endm = 12
					howmany = 30
				elif len (l) == 3:
					startyr, startm, endm = l
					howmany = 30
				elif len (l) == 4:
					startyr, startm, endm, howmany = l
				else:
					self.sher ("Error: wrong or missing parameters.")
					return ''

				startyr = int(startyr)
				startm = int(startm)
				endm = int(endm)
				howmany = int(howmany)
			except:
				self.sher ("Error: wrong or missing parameters.")
				return ''

		return self.u5.ltithi (startyr, startm, endm, howmany)

	def random (self, l):
		try:
			if l == []:
				length = 4 #4 bytes
			else:
				length = int(l[0])
			return mpap(eval('0x'+os.urandom(length).hex()))
		except:
			self.sher ("Error: unwanted parameters.")
			return mpap(0)

	def today (self, l):
		if l != []:
			self.sher ("Error: unwanted parameters.")
			return ''
		yy, mm, dd = str(date.today()).split('-')
		try:
			dd = int(dd)
			mm = int(mm)
			yy = int(yy)
		except:
			self.sher ("Error: Encountered problem with system date.")
			return ''
		return self.day ([dd, mm, yy])

	def day (self, l):
		try:
			dd, mm, yy = l
			dd = int(dd)
			mm = int(mm)
			yy = int(yy)
		except:
			self.sher ("Error: wrong or missing parameters.")
			return ''
			
		srise, s = self.u5.sun (dd, mm, yy)
		return ' ' + self.u5.vaaraList[self.u5.vaara(dd, mm, yy)] + \
				'vaara, ' + self.u5.tithiday (dd, mm, yy, srise) + \
				'\n ' + self.u5.dayList[self.u5.vaara(dd, mm, yy)] + \
				'day, ' + str(dd) + ' ' + \
				self.u5.monthList[mm-1] + ' ' + str(yy) + \
				'\n' + self.u5.dtithi (dd, mm, yy) + s

	def tithi (self, l):
		try:
			dd, mm, yy, hr = l
			dd = int(dd)
			mm = int(mm)
			yy = int(yy)
			hr = float(hr)
		except:
			self.sher ("Error: wrong or missing parameters.")
			return ''
			
		return self.u5.tithiday (dd, mm, yy, hr)

	def setzone (self, l):
		if l == []:
			zhr, latt, longt = [5.5, 12.9716, 77.5946] #Bangalore
		else:
			try:
				zhr, latt, longt = l
				zhr = float(zhr)
				latt = float(latt)
				longt = float(longt)
			except:
				self.sher ("Error: wrong or missing parameters.")
				return ''
			
		# Default location is Bangalore
		self.u5.setzone(zhr, latt, longt)
		return ' Set location to UTC+' + str(zhr) + ', Latitude: ' + str(latt) +\
				', Longitude: ' + str(longt)

	def getzone (self, l):
		if l != []:
			self.sher ("Error: wrong or missing parameters.")
			return ''
		# Default location is Bangalore
		#latt, longt, zhr = 12.9716, 77.5946, 5.5
		return ' Location is UTC+' + str(self.u5.zoneHour) + ', Latitude: ' + str(self.u5.latitude) +\
				', Longitude: ' + str(self.u5.longitude)

	def sun (self, l = [1, 1, 2019]):
		try:
			dd, mm, yy = l
		except:
			self.sher ("Error: wrong or missing parameters.")
			return ''

		srise, s = self.u5.sun(dd, mm, yy)
		return s

	def factors (self, l):
		value = l.pop()
		#print ("type of value is", type(value))
		return mpap(value).factors()

	##	n = int(value)
	##
	##	if n == 0:
	##		return '0'
	##
	##	#print ("n = ", n)
	##	result = set()
	##	result |= {int(1), n}
	##
	##	#def all_multiples(result, n, factor):
	##	#	z = n
	##	#	f = int(factor)
	##	#	while z % f == 0:
	##	#		if gmpy2.is_prime(f):
	##	#			result |= {f}
	##	#		z = z // f
	##	#		if gmpy2.is_prime(z):
	##	#			result |= {z}
	##	#		f += factor
	##	#	return result
	##	#
	##	#result = all_multiples(result, n, 2)
	##	#result = all_multiples(result, n, 3)
	##	#result = all_multiples(result, n, 5)
	##	#print ("intermediate result is ", result)
	##	
	##	for i in range(1, int(value.sqrt()), 2):
	##		i1 = int(i) + 1
	##		i2 = int(i) + 2
	##		#print ("i = ", i)
	##		#print ("i1 = ", i1)
	##		#print ("i2 = ", i2)
	##		if not n % i1:
	##			if gmpy2.is_prime(i1):
	##				result |= {i1}
	##			i1 = n // i1
	##			if gmpy2.is_prime(i1):
	##				result |= {i1}
	##		if not n % i2:
	##			if gmpy2.is_prime(i2):
	##				result |= {i2}
	##			i2 = n // i2
	##			if gmpy2.is_prime(i2):
	##				result |= {i2}
	##
	##	#result -= {n}
	##	#result -= {1}
	##
	##	#print (tuple (result))
	##	#print (result)
	##	return str(tuple (result))

	def caAppend (self, s):
		if len(self.ca) < self.mcas:
			self.ca.append(s)
		else:
			self.ca.append(s)
			self.ca = self.ca[1:]

	def showw (self, warnString):
		if warnString not in self.wnn and self.enn == '':
			#no error has happened already
			self.wnn.append(warnString)
		
	def sher (self, errString, overridePrevErr = False):
		#currentError is a mutable list
		#print ("------------------  ERROR  ----------------- ", errString, "with command: ", self.inps)
		#record only the first error
		if overridePrevErr == True or self.enn == '':
			self.enn = errString
		
		if overridePrevErr == True:
			#critical errors don't need to show warnings
			self.wnn = []

	def delall (self):
		self.stv = {}
		self.stw = {}
		self.stb = {}

		self.ldst()

	def delvar(self, var=''):
		if var != '':
			if var in self.stv.keys():
				del self.stv[var]
				del self.stw[var]
				del self.stb[var]
		#endif

	def insert (self, numStr, separator='_', skipDigits=4):

		numStrResult = numStr
		lenNumStr = len(numStr)
		if lenNumStr > skipDigits:
			numStrResult = numStr[-skipDigits:]
			while (lenNumStr > skipDigits):
				#dPY("insert: lenNumStr is ", lenNumStr)
				#dPY("insert: numStrResult is ", numStrResult)
				numStr = numStr[0:(lenNumStr - skipDigits)]
				numStrResult = numStr[-skipDigits:] + separator + numStrResult
				lenNumStr = lenNumStr - skipDigits
				#dPY("insert: lastly, lenNumStr is ", lenNumStr)

		#dPY("insert: numStrResult is ", numStrResult)
		return numStrResult

	def prettyPrint (self, numStr, base, ep=False, ins=False, wns= False):
		#dPY("prettyPrint: numStr is ", numStr)
		#dPY("prettyPrint: ep is ", ep)
		if len(numStr) > 1024: #FIXME make programmable instead of fixed 1024
			return numStr
		if ep == True:
			numStr = self.insert (numStr, '_', 4)
		elif wns == True and base == 'd':
			numStr = self.insert (numStr, ', ', 3)
		elif ins == True and base == 'd':
			if len (numStr) > 3:
				numStr = self.insert (numStr[:-3], ', ', 2) + ', ' + numStr[-3:]

		#dPY("prettyPrint: returning with numStr = ", numStr)
		return numStr

	def streverse (self, numStr):
		result = ''
		while numStr != '':
			result += numStr[-1:]
			numStr = numStr[0:-1]
		return result

	def getch(self):
		if self.insp == len(self.inps):
			#dPY ("------------ getcharacter: pre- insp is ", self.insp)
			#seeing end of input string
			self.look = ''
		else:
			self.look = self.inps[self.insp]
			#dPY ("getcharacter: pre-incr look is ", self.look)
			#dPY ("getcharacter: pre-incr pointer is ", self.insp)
			self.insp += 1
			#dPY ("getcharacter: post-incr pointer is ", self.insp)
	#enddef
		return self.look

	def looknext (self):
		if self.insp < len(self.inps):
			return self.inps[self.insp]
		else:
			return ''	

	def pseudomatch (self, expectlist):
		#takes in a list of strings/chars
		#and attempts to find all of them in the input string
		#starting at the current input string pointer
		#does not change the pointer
		if self.insp < len(self.inps):
			testStr = self.inps[self.insp:]
			pos = -1
			for elem in expectlist:
				pos = testStr.find(elem, pos + 1)
				if pos == -1:
					return False
			return True
		else:
			return False

	def sw (self):
		#skipwhite
		while self.look == ' ':
			self.getch()

		#dPY ("skipwhite: at the end, look is ", self.look, " pointer is ", self.insp)
	
	def match(self, c):
		if self.look == c:
			#dPY ("self.match: matching ", c)
			#dPY ("self.match: calling getcharacter...")
			self.getch()
			self.sw()
		else:
			if c == '':
				#dPY ("#####################Error: parser expected end of stream. self.look=", self.look)
				self.sher (f"Error: Unexpected '{self.look}' at end of line.")
			else:
				#dPY("match: non-null c is ", c)
				self.sher ("Error: parser expected '" + c + "', received '" + self.look + "'.")
		#dPY("returning from match -- look is ", self.look)
		
	def mnsw (self, c):
		#match No Skip white
		if self.look == c:
			#dPY ("self.match: calling getcharacter...")
			self.getch()
		else:
			self.sher ("Error: parser expected '" + c + "', received '" + self.look + "'.")
	
	def getvn(self):
		#get Variable Name
		#dPY ("getvn: just entered ... look is ", self.look)
		varName = ''
		while self.look.isalpha() or self.look.isdigit() or self.look == '_':
			varName +=self.look
			#dPY ("getVariableName: found look is ", self.look)
			self.getch()
		
		#dPY ("getVariableName: varName is ", varName)
		#dPY ("getVariableName: look is now ", self.look)
		#dPY ("getVariableName: pointer is now ", self.insp)
		self.sw()

		return varName

	def lsc (self, parseCommaDecPt = True):
		#look is spacer char
		return (self.look == "_") or (self.look == "," and self.dcn == False and parseCommaDecPt == True)

	def lsfc (self):
		#look is special float char
		return (self.look in ".eEfpnumkKMbBGTlLCci") and (self.look != '') 

	def getrmp (self, parseCommaDecPt=True):
		#dPY ("~~~~~~~~~~~ number starting ------------ look is ", self.look)
		#get Real MPAP
		#parseCommaDecPt is set to False when only integers are required to be input
		valStr = ''
		lastlook = ''
		if self.look == '':
			self.sher ("Error: Expected decimal number.")
			return mpap(0)

		#dPY ("##########  parseCommaDecPt = ", parseCommaDecPt)
		while self.look.isdigit() or self.lsfc() or self.lsc(parseCommaDecPt):
			#dPY("inside while loop -- self.look is ", self.look)
			if parseCommaDecPt == True:
				if self.look != '_' and self.look != ',' and self.look != ' ':
					valStr += self.look
			else:
				if self.look != '_' and self.look != ' ':
					valStr += self.look

			if 	parseCommaDecPt == False:
				if not self.look.isdigit() and not self.lsc(parseCommaDecPt):
					#dPY ("Error: Only integers allowed here. -- look is ", self.look)
					self.sher ("Error: Only integers allowed here.")
					
						
			lastlook = self.look
			self.getch()
			
			if (lastlook in "Ee") and (self.look in "+-"):
				valStr += self.look
				self.getch()

		#dPY ("getRealMPAP: =====X===== valStr is now", valStr)
		if lastlook in "Ee" and lastlook != '':
			self.sher ("Error: Missing exponent.")
			return mpap(0)

		expModifier = 0
		l = ['f', 'p', 'n', 'u', 'm', '_', 'k', 'Mi', 'b']
		fx = -1 #first match from left
		for c in l:
			#print ("char is", c)
			x = valStr.find(c)
			if x >= 0:
				#print ("found", c, "at position", x)
				expModifier += (-15 + l.index(c) * 3)
				if fx == -1:
					fx = x
		if fx != -1:
			valStr = valStr[:fx]

		fx = -1 #first match from left
		for c in ['B', 'bi', 'Bi']:
			x = valStr.find(c)
			if x >= 0:
				expModifier += 9
				if fx == -1:
					fx = x
		if fx != -1:
			valStr = valStr[:fx]
		
		l = ['l', 'c']
		fx = -1 #first match from left
		for c in l:
			#print ("char is", c)
			x = valStr.lower().find(c)
			if x >= 0:
				#print ("found", c, "at position", x)
				expModifier += (5 + l.index(c) * 2)
				if fx == -1:
					fx = x
		if fx != -1:
			valStr = valStr[:fx]

		manMultiplier = 1
		l = ['K', 'M', 'G', 'T']
		fx = -1 #first match from left
		for c in l:
			#print ("char is", c)
			x = valStr.find(c)
			if x >= 0:
				#print ("found", c, "at position", x, "lindex is ", l.index(c))
				manMultiplier *= (1024**(l.index(c) + 1))
				expModifier += ((l.index(c) + 1) * 3)
				if fx == -1:
					fx = x
		if fx != -1:
			valStr = valStr[:fx]
		#print ("manMultiplier is", manMultiplier)

		if valStr == '':
			#dPY("getRealMPAP: ================================= valStr == NULLLLL", valStr)
			return mpap(0)
	
		valStr = valStr.lstrip('0')
		if valStr == '' or valStr.find('.') == 0:
			valStr = '0' + valStr
		#print ("----------------------------------getRealMPAP: =====B===== valStr is now", valStr)

		value = mpap (valStr)
		try:
			#value = mpap (valStr)
			pass
		except:
			self.sher ("Error: Illegal number. ERROR E203")
			return mpap(0)
		#dPY ("getrmp: =====C===== value is now", value)
		value.Mantissa *= manMultiplier
		value.Exponent += expModifier 
		#dPY ("getrmp: =====C===== value is now", value)
		#dPY( "~~~~~~~~~~getrmp: value is ", value, "and type of value is ", type(value))
		self.sw()
		return value

	def getBinaryNumber (self):

		if self.look not in "01" and not self.lsc():
			self.sher ("Error: Expected binary bit, received '" + self.look + "'.")
			return mpap(0)
		
		valStr = ''
		#get the number first, and then flag illegal binary number
		while self.look in '01 _':
			if self.look == '':
				break

			if not self.lsc():
				valStr += self.look
			
			self.getch()

		if valStr == '':
			valStr = '0'
	
		try:
			value = mpap(int('0b'+valStr, 0))
		except (NameError, TypeError, ValueError, AttributeError, OverflowError, SyntaxError):
			self.sher ("Error: Illegal binary number " + valStr + "'.")
			return mpap(0)

		return mpap(value)

	def getInteger (self, parseCommaDecPt = True):
		#dPY ("getInteger: start.")

		valStr = ''
		while self.look.isdigit() or self.lsc(parseCommaDecPt):
			#dPY ("getInteger: look is ", self.look, "...")
			if self.look == '':
				break

			if not self.lsc(parseCommaDecPt):
				valStr += self.look

			self.getch()

		if valStr == '':
			valStr = '0'
	
		try:
			value = int(valStr)
		except (NameError, TypeError, ValueError, AttributeError, OverflowError):
			self.sher ("Error: Illegal number " + valStr + ". ERROR 101.")
			return mpap(0)

		self.sw()
		#dPY ("getInteger: returning with value ", value, "...")
		return value


	def getHexNumber (self):

		if not self.look.isdigit() and not self.look.lower() in "abcdef" and not self.lsc(parseCommaDecPt=False):
			#no comma in hex number
			self.sher ("Error: Expected hex number, received '" + self.look + "'.")
			return mpap(0)
		
		valStr = ''
		while self.look.isdigit() or self.look == '_' or (self.look.lower() in "abcdef") or self.lsc(parseCommaDecPt=False):
			if self.look == '':
				break

			if not self.lsc(parseCommaDecPt=False):
				valStr += self.look

			self.getch()
			#dPY("valStr is ", valStr)

		if valStr == '':
			valStr = '0'
	
		#dPY("Finally valStr is ", valStr)
		try:
			value = mpap(int('0x'+valStr, 0))
		except (NameError, TypeError, ValueError, AttributeError, OverflowError, SyntaxError):
			self.sher ("Error: Illegal hex number " + valStr + "'.")
			return mpap(0)

		return mpap(value)

	def getOctalNumber (self):

		if self.look not in "01234567" and not self.lsc():
			self.sher ("Error: Expected octal number, received '" + self.look + "'.")
			return mpap(0)
		
		valStr = ''
		#get the number first, and then flag illegal octal number
		while  self.look.lower() in "01234567 _":
			if self.look == '':
				break

			if not self.lsc():
				valStr += self.look

			self.getch()

		if valStr == '':
			valStr = '0'
	
		try:
			value = mpap(int('0o'+valStr, 0))
		except (NameError, TypeError, ValueError, AttributeError, OverflowError, SyntaxError):
			#dPY("valStr is ", valStr)
			value = mpap(0)
			self.sher ("Error: Illegal octal number " + valStr + "'.")
		return value

#catList has these fields
# ISLVALUE == 1 if this cat is the first of a sequence of assignments --
# will be actually used to assign values to variables if varNames are present
# [VARNAME -- will be updated with RVALUE if isLValue == 1
# VALUE -- used if isLValue == 0
# BASE -- 'd', 'h', 'o' or 'b'
# MAXPOS -- used with VARNAME or VALUE. Will be (WIDTH of VALUE - 1) if isLValue == 0
# MINPOS -- used with VARNAME or VALUE. Will be 0 if isLValue == 0
#		]*
	def cat (self):
		#dPY ("---- cat: calling procvn")
		allList = list(self.procvn(parseCommaDecPt = False))
		if len(allList) == 0:
			self.sher ("Error: expected variable or number.")
			return mpap(0), 0, 'd', False, []			
		else:
			value, width, base, varName, maxBitPos, minBitPos = allList
		#print ("---- cat AA: returned from procvn with value: ", (allList[0]), " now look is ", self.look)
		#print ("---- cat AA: seen ',', procvn returned value ", allList[0])
		#print ("---- cat AA: seen ',', procvn returned width ", allList[1], "type width is ", type(allList[1]))
		#print ("---- cat AA: seen ',', procvn returned varName ", allList[3])
		#print ("---- cat AA: seen ',', look is ", self.look)

		if allList[1] == 0:
			width = self.defw
			if self.enn == '':
				if varName != "#NULLVARIABLENAME#":
					pass
					#print (f"---- cat: Warning: AA Width of {allList[3]} unspecified.")
					#self.showw (f"Warning: Width of {allList[3]} unspecified. Will assume {self.defw}.")
				else:
					if self.look != '{':
						pass
						#Don't show warning for replication count
						#print (f"---- cat: Warning: AA Width of {allList[3]} unspecified. Will assume {self.defw}.")
						#self.showw (f"Warning: Width unspecified.")
		#first number or variable's base is the base of the catenation
		if varName == "#NULLVARIABLENAME#":
			isLValue = False
		else:
			isLValue = True
	
		while self.look == ',':
			self.match(',')
			if self.look == ',':
				#dPY ("########## ERROR F745 look is ", self.look)
				self.sher ("Error: missing number. ERROR F745")
				return mpap(0), 0, 'd', True, [mpap(0), 0, 'd', "#NULLVARIABLENAME#", -1, -1]

			#dPY("---- cat: calling procvn...")
			returnList = list(self.procvn(parseCommaDecPt = False))
			#dPY("---- cat: done procvn...  look is ", self.look)
			if self.look != '}' and self.look != ',':
				#at this point, there can be another comma-separated term
				#or the end of the line (closing brace)
				#dPY ("########## ERROR F741 look is ", self.look, " current value = ", returnList[0])
				self.sher ("Error: incorrect format. ERROR F741")
				return mpap(0), 0, 'd', True, [mpap(0), 0, 'd', "#NULLVARIABLENAME#", -1, -1]

			#dPY ("---- cat BB: seen ',', procvn returned value ", returnList[0])
			#dPY ("---- cat BB: seen ',', procvn returned width ", returnList[1], "type width is ", type(returnList[1]))
			#dPY ("---- cat BB: seen ',', procvn returned varName ", returnList[3])
			if len(returnList) == 0:
				self.sher ("Error: expected variable or number after ','.")
				return mpap(0), 0, 'd', True, [mpap(0), 0, 'd', "#NULLVARIABLENAME#", -1, -1]
		
			#dPY('')
			#dPY ("---- cat BB: Error Notif. = ", self.enn, " width = ", returnList[1])
			#dPY('')
			varName = returnList[3]
			localWidth = 0
			if returnList[1] == 0:
				#width is 0
				localWidth = self.defw
				if self.enn == '':
					if varName != "#NULLVARIABLENAME#":
						pass
						#print (f"---- cat: Warning: BB Width of {varName} unspecified.")
						#self.showw (f"Warning: Width of {varName} unspecified.")
					else:
						if self.look != '{':
							pass
							#Don't show warning for replication count
							#print (f"---- cat: Warning: BB Width of {varName} unspecified.")
							#self.showw (f"Warning: Width unspecified.")

			else:
				localWidth = int(returnList[1])

			value = (value << localWidth) + returnList[0]
			width += localWidth
			#dPY ("catenation: setting value to ", value, "width to ", width)
			if varName == "#NULLVARIABLENAME#":
				thisIsLValue = False
			else:
				thisIsLValue = True
			
			isLValue = isLValue and thisIsLValue

			for item in returnList:
				allList.append(item)

			#dPY("catenation: Appended returnList to ", allList)
			#dPY("catenation: isLValue is ", isLValue)
			#dPY("catenation: width is ", width)
	
		#endwhile

		#dPY ("---- cat: returning with allList (value width base isLValue allList) ", value , width , base, isLValue, allList)
		#dPY ("catenation: returning width of type ", type(width ))
		
		#dPY ("#############################returning from catenation: ---  value is ", value, " width is ", width, " varName is ", varName)
		return value, width, base, isLValue, allList

	def sublist (self, l, size):
		#output sublists of list l 
		#each of length size
		for i in range (0, len(l), size):
			yield l[i:i+size]

	def vexfunceval(self, value, varName):
		if varName == 'ln':
			return mpap(value).log()
		elif varName == 'log10':
			return mpap(value).log()/mpap(10).log()
		elif varName == 'log':
			#print ("vexfunceval: calling log")
			return mpap(value).log()
		elif varName == 'sqrt':
			return mpap(value).sqrt()
		elif varName == 'exp':
			return mpap(value).exp()
		elif varName == 'digits':
			return mpap(value).digits()
		elif varName == 'tan':
			return mpap(value).tan()
		elif varName == 'sin':
			return mpap(value).sin()
		elif varName == 'cos':
			return mpap(value).cos()
		elif varName == 'acos':
			return mpap(value).acos()
		elif varName == 'asin':
			return mpap(value).asin()
		elif varName == 'atan':
			return mpap(value).atan()
		elif varName == 'asinh':
			return mpap(value).asinh()
		elif varName == 'acosh':
			return mpap(value).acosh()
		elif varName == 'atanh':
			return mpap(value).atanh()
		elif varName == 'sinh':
			return mpap(value).sinh()
		elif varName == 'cosh':
			return mpap(value).cosh()
		elif varName == 'tanh':
			return mpap(value).tanh()
		else:
			self.sher (f"Error: unknown mathematical function '{varName}'.")
			return mpap(0)

	def procv(self):
	
		#dPY ("processVariables: look is ", self.look)
		#dPY ("processVariables: calling getVariableName...")
		varName = self.getvn()
		#dPY ("procv: returned from getvn. look is ", self.look)
		#dPY ("procv: returned from procv... with varName as ", varName)
		
		newVariableFound = False
		maxBitPos = -1
		minBitPos = -1
		width = 0
		base = 'd' 
	
		#dPY ("processVariables: varName is ",varName)
		if varName in self.abv:
			return self.stv[varName], 0, 'd', "#NULLVARIABLENAME#", -1, -1
		elif varName in self.miscelFunctionsList:
			#a vex function
			#dPY ("processVariables: varName is in miscelFunctionsList", varName)
			self.dcn = True
			lookForParens = False
			if self.look == '(':
				lookForParens = True
				#dPY ("processVariables: lookForParens is", lookForParens)
				self.match('(')
			arg = []
			if True:
			#try:
				i = 0
				while self.look != ')' and lookForParens == True:
					#dPY ("processVariables while loop: self.look is", self.look)
					if i == 0:
						#base and width are taken from the first argument
						value, width, base = self.expr()
					else:
						value = self.expr()[0]
						if self.insp == self.iris and self.excc > 2:
							self.sher ("Error: wrong or missing parameters passed to function.")
							self.excc = 0 
							return mpap(0), 0, 'd', "#NULLVARIABLENAME#", 0, 0
					arg.append(value)
					if self.look == ',':
						self.match(',')
					elif self.look == '':
						break
					i += 1
				if lookForParens == True:
					self.match(')')
				#dPY("arg list is ", str(arg), " varName = ", varName)
				if varName == 'tithi':
					value = self.tithi(arg)
				elif varName == 'random':
					value = self.random(arg)
				elif varName == 'setzone':
					value = self.setzone(arg)
				elif varName == 'getzone':
					value = self.getzone(arg)
				elif varName == 'sun':
					value = self.sun(arg)
				elif varName == 'today':
					value = self.today(arg)
				elif varName == 'ltithi':
					value = self.ltithi(arg)
				elif varName == 'day':
					value = self.day(arg)
				elif varName == 'factors':
					value = self.factors(arg)
				elif varName == 'int':
					value = self.int(arg)
				elif varName == 'atan2':
					value = self.atan2(arg)
				elif varName == 'pi':
					value = self.pi(arg)
				elif varName == 'e':
					value = self.e(arg)
				elif varName == 'isp':
					value = self.isp(arg)
				elif varName == 'nxp':
					value = self.nxp(arg)
				elif varName == 'do':
					#dPY ("seeing do function, arg is ", arg, lvl=10)
					value = self.do(arg)
				#dPY ("value is ", value)
			#except (NameError, TypeError, ValueError, AttributeError, OverflowError, SyntaxError):
			#	value = mpap(0)
			#	self.sher ("Error: error executing function '" + varName + '(' + str(arg) + ")'. Result is not-a-number.")
			#except (VexError):
			#	value = mpap(0)
			#	self.sher ("Error: error executing function '" + varName + "()'. Missing parameters.")
			self.dcn = False
			#dPY ("XXXX. value is ", value)

		elif self.look == '(':
			self.dcn = True
			self.match('(')
			if self.look != ')':
				value, width, base = self.expr()
			else:
				#handle parentheses enclosing null parameters
				if varName in self.mpapFunctionsList:
					self.sher ("Error: expected value within parentheses.")
				else:
					self.sher (f"Error: Unknown function '{varName}'.")
				value, width, base = mpap(0), 0, 'd'
			#dPY ("processVariables: varName=", varName)
			#dPY ("processVariables: value=", value)
			self.match(')')
			value, width, base = self.procbs (value, width, base)
			value = self.vexfunceval(value, varName)
			#dPY ("vexfunceval returned: ", value)
			try:
				pass
				#dPY ("processVariables: calling function varName", varName)
			except (NameError, TypeError, ValueError, OverflowError, AttributeError):
				value = mpap(0)
				self.sher (f"Error: executing mathematical function '{varName}'.")
			self.dcn = False
		else:
			#a variable name
			reDimensionVar = False #set the width of variable afresh
			#dPY ("############processVariables: seeing a variable ", varName, "...")
			maxBitPos = -1
			minBitPos = -1
			if varName in self.stv.keys():

				#dPY ("processVariables: variable ", varName, "already exists...")
	
				if self.look == ':':
					self.match(':')
					reDimensionVar = True
					width = self.getInteger(parseCommaDecPt = False)
					if width > 0:
						maxBitPos = width -1
						minBitPos = 0
					else:
						width = 0
				elif self.look == '[':
					#Verilog-style bit field specifier
					self.match('[')

					if self.axf == 1:
						try:
							err = ''
							maxBitPos = self.expr()[0]
							if maxBitPos.isComplex():
								err = ' - cannot have complex number here'
								raise ValueError
							maxBitPos = int(maxBitPos)
							if maxBitPos < 0:
								raise ValueError
						except (NameError, TypeError, ValueError, AttributeError, OverflowError):
							self.sher (f"Error: Illegal index{err}. ERROR E201")
							return mpap(0), 0, 'd', "#NULLVARIABLENAME#", -1, -1
					else:
						maxBitPos = self.getInteger()
					#dPY ("Received maxBitPos = ", maxBitPos)
					if self.look == ':':
						self.match(':')
						if self.nums() == False and self.axf == 0:
							self.sher ("Expected: integer.")
						else:
							if self.axf == 1:
								try:
									err = ''
									minBitPos = self.expr()[0]
									if minBitPos.isComplex():
										err = ' - cannot have complex number here'
										raise ValueError
									minBitPos = int(minBitPos)
									if minBitPos < 0:
										raise ValueError
								except (NameError, TypeError, ValueError, AttributeError, OverflowError):
									self.sher (f"Error: Illegal lower index{err}. ERROR E207")
									return mpap(0), 0, 'd', "#NULLVARIABLENAME#", -1, -1
							else:
								minBitPos = self.getInteger()
						
						#dPY ("Received minBitPos = ", minBitPos)
					
					self.match(']')
					if minBitPos > maxBitPos:
						self.sher ("Error: Larger lower index. ERROR A205")
					
					if maxBitPos == minBitPos:
						#treat as single specifier case
						minBitPos = -1
					
				#endif	   
				if maxBitPos == -1:
					#No Verilog-style bit field specifier
					width = self.stw[varName]
					base = self.stb[varName]
					value = self.stv[varName]
					
					#dPY("processVariables: No Verilog-style bit field specifier.")
					#dPY("processVariables: seeing an existing variable ", varName, " with value ", value, " and  ", base, " and type ", type(value))
					#dPY("processVariables: seeing an existing type of self.stv[varName] ", type(self.stv[varName]))
				else:
					width = self.stw[varName]
					base = self.stb[varName]
					value = self.stv[varName]

					if minBitPos == -1:
						#One max position Verilog-style bit field specifier
						#dPY("processVariables: minBitPos = -1. Seeing an existing variable ", varName, " with value ", self.stv[varName], "...")
						#dPY("processVariables: minBitPos = -1. maxBitPos is ", maxBitPos)
						try:
							value = mpap((int(value) >> maxBitPos) % 2)
						except (NameError, TypeError, ValueError, AttributeError, OverflowError):
							value = mpap(0)
							self.sher ("Error: Illegal bit index. ERROR 9.")
						
						width = 1
						
						#base already set to self.stb[varName]
						#base = self.stb[varName]
						#dPY ("processVariables: Existing variable. Max position Verilog-style bit field specifier...")
						#dPY("processVariables: One max position Verilog-style bit field specifier base is now ", base)
						#dPY ("processVariables: maxBitPos is ", maxBitPos, " ,value is ", value)
					else:
						#Both max and min position Verilog-style bit field specifier found
						if minBitPos > maxBitPos:
							self.sher ("Error: expected smaller 'downto' index.")
							return mpap(0), 0, 'd', "#NULLVARIABLENAME#", -1, -1
						
						if reDimensionVar == True:
							assw = maxBitPos - minBitPos + 1
							if assw != self.stw[varName]:
								self.stw[varName] = assw
								self.showw ("Warning: updated width of variable " + varName + " to " + str(self.stw[varName]))
						elif self.twa == True:
							#not redimensioning
							## ?? REVIEW CODE FIXME
							self.stw[varName] = width

						#dPY ("^^^^^^^^^^^^^processVariables: maxBitPos is ", maxBitPos, " ,minBitPos is ", minBitPos, " ,self.stw[varName] is ", self.stw[varName])
						if self.stw[varName] != 0 and self.stw[varName] < (maxBitPos - minBitPos + 1):
							#dPY ("^^^^^^^WARN^^^^^^processVariables: maxBitPos is ", maxBitPos, " ,minBitPos is ", minBitPos, " ,self.stw[varName] is ", self.stw[varName])
							self.showw ("Warning: existing width " + str(self.stw[varName]) + f" of variable {varName} is smaller than [" + str(maxBitPos) + ":" + str(minBitPos) + "] bit width specified.")
						elif width == 0:
							bl = int(value).bit_length()
							if (maxBitPos - minBitPos + 1) > bl:
								self.showw ("Warning: width not specified, but [" + str(maxBitPos) + ":" + str(minBitPos) + "] exceeds " + str(bl) + " needed.")
							
						#dPY ("^^^^^^^^^^^^^processVariables: reDimensionVar is ", reDimensionVar, 
						#		" ,width is ", width)
						if  width > maxBitPos - minBitPos + 1 and reDimensionVar == False:
							self.showw ("Info: Slice [" + str(maxBitPos) + ":" + str(minBitPos) +"] of variable '" + varName + "' accessed.")

						#dPY ("processVariables: width is ", width)
						width = maxBitPos - minBitPos + 1

						try:
							value = mpap((int(value) >> minBitPos) % (1<<width) )
						except (NameError, TypeError, ValueError, AttributeError, OverflowError):
							value = mpap(0)
							self.sher ("Error: Illegal operation!. ERROR 10.")
							return mpap(0), 0, 'd', "#NULLVARIABLENAME#", -1, -1
						
						#base already set to self.stb[varName]
						#base = self.stb[varName]
						#dPY ("processVariables: Existing variable. Both max and min position Verilog-style bit field specifier...")
						#dPY ("processVariables: maxBitPos is ", maxBitPos, " value is ",value)
					
			else:
				#dPY (f"####### PROCV VARNAME {varName} not in SymTable")
				if self.envre == False:
					#dPY ("creating a variable ", varName)
					#create this variable
					self.stv[varName] = mpap(0)
					self.stw[varName] = 0
					self.stb[varName] = 'd'
					
				reDimensionVar = False
				value = mpap(0)
				width = 0
				base = 'd'
				#dPY ("---####### PROCV VARNAME not in SymTable look is ", self.look)
				if self.look == ':':
					#dPY ("---####### PROCV VARNAME not in SymTable, calling getInteger FOUND LOOK : look is ", self.look)
					self.match(':')
					reDimensionVar = True
					width = self.getInteger(parseCommaDecPt = False)
					#dPY ("---####### PROCV VARNAME not in SymTable, returned from getInteger width is ", width)
					if width > 0:
						maxBitPos = width -1
						minBitPos = 0
					else:
						width = 0
					#dPY ("---####### PROCV VARNAME not in SymTable, returned from getInteger look is ", self.look)
				elif self.look == '[':
					self.match('[')

					if self.axf == True:
						try:
							err = ''
							maxBitPos = self.expr()[0]
							if maxBitPos.isComplex():
								err = ' - cannot have complex number here'
								raise ValueError
							maxBitPos = int(maxBitPos)
							if maxBitPos < 0:
								raise ValueError
						except (NameError, TypeError, ValueError, AttributeError, OverflowError):
							self.sher (f"Error: Illegal number{err}. ERROR E203")
							return mpap(0), 0, 'd', "#NULLVARIABLENAME#", -1, -1
					else:

						maxBitPos = self.getInteger()

					#dPY ("Received maxBitPos = ",maxBitPos)
					if self.look == ':':
						self.match(':')
						#dPY ("Matched :!")
						if self.nums() == False and self.axf == False:
							self.sher ("Error: Expected positive integer.")
							return mpap(0), 0, 'd', "#NULLVARIABLENAME#", -1, -1
						else:

							if self.axf == True:
								try:
									err = ''
									minBitPos = self.expr()[0]
									if minBitPos.isComplex():
										err = ' - cannot have complex number here'
										raise ValueError
									minBitPos = int(minBitPos)
									if minBitPos < 0:
										raise ValueError
								except (NameError, TypeError, ValueError, AttributeError, OverflowError):
									self.sher (f"Error: Illegal lower index{err}. ERROR E205")
									return mpap(0), 0, 'd', "#NULLVARIABLENAME#", -1, -1
							else:
								minBitPos = self.getInteger()
						
						#dPY ("Received minBitPos = ", minBitPos)
					
					self.match(']')
					#dPY ("matched ']'... look is now ", self.look)
					#dPY ("creating a variable ", varName, " -- found max/min pos ", maxBitPos, ':', minBitPos)
					if minBitPos > maxBitPos:
						self.sher ("Error: Larger downto index.")
						return mpap(0), 0, 'd', "#NULLVARIABLENAME#", -1, -1
					
					if maxBitPos < 0 and minBitPos < 0:
						self.sher ("Error: Indices required.")
						return mpap(0), 0, 'd', "#NULLVARIABLENAME#", -1, -1
					else:
						width = maxBitPos + 1
						if self.envre == False:
							self.stw[varName] = width
					#endif
					#dPY ("creating a variable ", varName, " -- width is ", width)
	
				#endif
				if self.envre == False:
					self.showw ("New '" + varName + "'.")
				newVariableFound = True
			#endif -- variable name parsed

			#dPY("#####assignment or conditional operators newVariableFound is ", newVariableFound)
			#dPY ("look is ", self.look)
			#assignment or conditional operators
			if self.look == '<':
				#dPY ("look is ", self.look)
				#dPY ("found < ------------------ ", self.look)
				if self.looknext() == '<':
					#left-shift operator -- the '<<' will be handled in term
					pass
				else:
					self.mnsw('<')
					value = self.cmpop ('<', value)
					#dPY ("for LT or LTEQ op, value0 is ", value0)
					width = 0
					base = 'n'
			elif self.look == '>':
				if self.looknext() == '>':
					#right-shift operator -- the '>>' will be handled in term
					pass
				else:
					self.mnsw('>')
					value = self.cmpop ('>', value)
					width = 0
					base = 'n'
			elif self.look == '=':
				self.mnsw('=')
				#dPY ("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~assignment: look is ", self.look)
				if self.look == '=':
					#dPY ("look is ", self.look, "~~~~~~~~~~~~~ found ==")
					#found '=='
					self.match('=')
					value = self.cmpop ('=', value)
					width = 0
					base = 'n'
				else:
					#assignment operator
					#assignment operator single '='
					self.sw()
					#handle this error specially - space(s) between '='
					#dPY ("Found =, in processVariables... calling expression...")
					value, width, base = self.expr()
					#dPY ("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~assignment returned from expression -- = ... width is ", width, "base=", base, "type of value is ", type(value))
					#dPY ("maxBitPos is ", maxBitPos)
					#dPY ("minBitPos is ", minBitPos)
					if maxBitPos == -1:
						#dPY ("maxBitPos is -1")
						#No Verilog-style bit field specifier
						
						if newVariableFound == True or self.tba == True:
							self.stb[varName] = base
						
						#dPY ("width of RHS is  ", width)
						#print ("stw is  ", self.stw[varName])

						if newVariableFound == True or self.twa == True:
							if width > 0: #only if assignment width is defined
								self.stw[varName] = width

						if newVariableFound == False:
							if width > self.stw[varName] and width > 0:
								self.stw[varName] = width 
								self.showw ("Warning: upsized width of variable " + varName + " to " + str(self.stw[varName]))
								#print ("Warning: upsized width of variable ", varName, " to ", self.stw[varName])
							
						#print ("~~~~~1~~~~~~~~ value is ", value)

						#print ("----------width is ====================== ", width)
						#print ("----------base is ====================== ", base)
						W1 = (mpap(1)<<width)
						W2 = mpap(1<<width)
						#print ("----------W1 is ====================== ", W1)
						#print ("----------W2 is ====================== ", W2)
						try:
							if base != 'n':
								if value >= (mpap(1)<<width) and width > 0:
									value = mpap(value) % mpap(1<<width)
									self.showw ("Warning: expected number less than " + str(1<<value) + ". Will be truncated.")
						except:
							value = mpap(0)
							self.sher ("Error: Illegal number. ERROR E205")
							return mpap(0), 0, 'd', "#NULLVARIABLENAME#", -1, -1

						#endif

						#update variable value only if no errors have occurred
						#dPY ("assigning STV --  value=", value, "base=", base, "type of value is ", type(value))
						if self.enn == '':
							self.stv[varName] = value
							self.stw[varName] = width
							self.stb[varName] = base
						#else retain old value or 0 value for a newly created variable

						#print ("variable is  ", varName)
						#dPY ("~~~~~2~~~~~~~~ value is ", value)
					else:
						#dPY ("---------------maxBitPos is not -1", lvl=100)
						#dPY ("---------------self.vex.tba = ", self.tba, lvl=100)
						if minBitPos == -1:
							#dPY ("minBitPos is -1", lvl=100)
							#One max position Verilog-style bit field specifier
							if newVariableFound == False:
								if maxBitPos >= self.stw[varName] and self.stw[varName] > 0:
									self.stw[varName] = maxBitPos + 1
									self.showw ("Warning: updated width of variable " + varName + " to " + str(self.stw[varName]))
							else:
								self.stw[varName] = maxBitPos + 1
							
							#dPY ("Single bit Verilog-style bit field specifier... maxBitPos =", maxBitPos, " width is ", width)
							if not value.isInt():
								self.sher ("Error: expected single bit for Verilog-style bit assignment. ERROR 23")
								return mpap(0), 0, 'd', "#NULLVARIABLENAME#", -1, -1
							if value > mpap(1):
								value = value & 0b1
								self.showw("Warning: expected bit (0 or 1) for RH value Will be truncated.")
							
							try:
								value = mpap (value) & 0b1
								shiftMask = (1 << maxBitPos)
							except (NameError, TypeError, ValueError, AttributeError, OverflowError):
								self.sher ("Error: Illegal bit index. ERROR 11.")
								return mpap(0), 0, 'd', "#NULLVARIABLENAME#", -1, -1
							
							if newVariableFound == True:
								self.stv[varName] = mpap(0)

							if value == 1:
								if self.enn == '':
									self.stv[varName] = self.stv[varName] | shiftMask
							else:
								if self.enn == '':
									self.stv[varName] = self.stv[varName] & ~shiftMask

							#dPY("--------------------------", lvl=100)
							width = 1
							if newVariableFound == True or self.tba == True:
								#for newly created variable, assign base, else preserve old base (unless taking base from assignment)
								#print ("new XX variable created is ", newVariableFound)
								dPY("processVariables -- assignment: -- after assignment, base is ", base, lvl=100)
								self.stb[varName] = base
							else:
								base = self.stb[varName]
							#dPY ("---------------maxBitPos is not -1 type self.stv[varName] =", type(self.stv[varName]))
							#dPY("---------------processVariables -- assignment: One max position Verilog-style bit field specifier -- last after assignment, base is ", base)
						else:
							#dPY ("minBitPos is not -1")
							#dPY("Both max and min position Verilog-style bit field specifier found")
							#Multi bit Verilog-style bit field specifier

							#dPY ("width is ", width, "maxBitPos is ", maxBitPos)

							assw = maxBitPos - minBitPos + 1
							#dPY ("assignmentWidth is ", assw)

							if assw < 1:
								self.sher ("Error: Illegal bit index (negative). ERROR 21.")
								return mpap(0), 0, 'd', "#NULLVARIABLENAME#", -1, -1
							elif assw < width:
								self.showw ("Warning: Widths of LHS variable slice and RHS don't match.")

							#dPY ("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~now width is ", width, "maxBitPos is ", maxBitPos)
							#print ("stw is ", self.stw[varName], " bool.newVariableFound is ", newVariableFound)

							if not value.isInt():
								self.sher ("Error: expected single bit for Verilog-style bit assignment. ERROR 1001")
								return mpap(0), 0, 'd', "#NULLVARIABLENAME#", -1, -1
							#dPY ("Got varName=", varName, "value=", value, "assignmentWidth is ", assw)

							try:
								intValue = 	int (value)
								if intValue >= (1<<assw) and assw > 0:
									value = mpap(intValue % (1<<assw))
									self.showw ("Warning: More than " + str(assw) + " bits of LHS variable required. RHS value will be truncated.")
									#dPY ("warning AAA value is updated to ", value)
							except:
								self.sher ("Error: Illegal number. ERROR E202")
								return mpap(0), 0, 'd', "#NULLVARIABLENAME#", -1, -1
							
							#dPY ("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~At middle: varName=", varName, " value=", value, 
							#		" assw=", assw, " width=", width, " newVariableFound=", newVariableFound)
							#iterate through variable and zero out the bit fields [maxBitPos:minBitPos]
							if newVariableFound == True:
								self.stv[varName] = mpap(0)

							i = minBitPos
							while i <= maxBitPos:
								if (self.stv[varName] >> i) & 0x1 == 1:
									try:
										if self.enn == '':
											self.stv[varName] = self.stv[varName] - (1<<i)
									except (NameError, TypeError, ValueError, AttributeError, OverflowError):
										self.sher ("Error: Illegal bit index: ERROR 6.")
										return mpap(0), 0, 'd', "#NULLVARIABLENAME#", -1, -1

								i += 1
							#endwhile 

							if newVariableFound == False:
								if ((maxBitPos + 1) > self.stw[varName]) and self.stw[varName] > 0:
									self.stw[varName] = maxBitPos + 1
									self.showw ("Info: updated width of variable " + varName + " to " + str(self.stw[varName]) + ".")
								if self.twa == True:
									if width > 0 and self.stw[varName] == 0: #only if assignment width is defined
										self.stw[varName] = width
										self.showw ("Info: updated width of variable " + varName + " to " + str(self.stw[varName]) + ".")
							elif newVariableFound == True:
								if self.twa == True and width > 0:
									self.stw[varName] = width
								else:
									self.stw[varName] = maxBitPos + 1
							#dPY ("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~stw is ", self.stw[varName])
							#print ("stw is now ", self.stw[varName])
							#print ("after all: stw is ", self.stw[varName])
							#print ("after all width is ", width)
							
							#dPY("Zeroed out bit field -- stv[", varName, "] = ", self.stv[varName])

							if newVariableFound == True or self.tba == True:
								#for newly created variable, assign base, else preserve old base
								#dPY ("new AA variable created is ", newVariableFound)
								self.stb[varName] = base

							#dPY("Pt. A: varName=", varName, " stv[", varName, "] = ", self.stv[varName])
							if self.enn == '':
								#update value of existing variable
								if type(self.stv[varName]) == bool:
									if self.stv[varName] == True:
										tempValue = mpap(1)
									elif self.stv[varName] == False:
										tempValue = mpap(0)
								else:
									tempValue = self.stv[varName]
									#dPY("tempValue=", tempValue, "varName=", varName)

								try:
									self.stv[varName] = mpap(int (tempValue) + (int (value) << minBitPos))
								except:
									self.sher ("Error: Illegal number. ERROR E202")
									return mpap(0), 0, 'd', "#NULLVARIABLENAME#", -1, -1

							#else, value keeps the right hand side assignment value
							#dPY("At ending: minBitPos=", minBitPos, " maxBitPos=", maxBitPos)
							#dPY("At ending: varName=", varName, " stv[", varName, "] = ", self.stv[varName])
						#endif minBitPos
					#endif maxBitPos
					newVariableFound = False #assignment completed
				#endif look == '=' second level
			else:
				#to handle expressions like {x,y} = <expr>
				if self.pseudomatch(['==']) == False and\
						self.pseudomatch(['>=']) == False and\
						self.pseudomatch(['<=']) == False and\
						self.pseudomatch(['!=']) == False:
					#dPY ("---------------procv: future match of '==' is False")
					if self.pseudomatch(['=']) == True:
						#dPY ("---------------procv: future match of '==' is True")
						newVariableFound = False #some assignment will happen in future
			#endif look == '='

		if newVariableFound == True and self.envre == True:
			self.sher (f"Error: Variable '{varName}' accessed before assignment.", overridePrevErr = True)
		#dPY ("=========PROCV  -- now returning: value ", value, ', type value is ', type(value), "maxBitPos is ", maxBitPos, lvl=11)
		return value, width, base, varName, maxBitPos, minBitPos

	def expo(self):
		#dPY("expo: look is ", self.look)
		#dPY("expo: calling factor...")
		if self.iuo (self.look):
			value, width, base = self.una()[0:3]
			#dPY ("expo A:  value is ", value, " of type ", type(value))
		else:
			value, width, base = self.factor()[0:3]
			#dPY ("expo AA:  value is ", value, " of type ", type(value))

			if self.look == '!' and self.fhhp == True:
				self.mnsw('!')

				if self.look == '=':
					#inequality operator
					#found '!='
					self.match('=')
					value = self.cmpop ('!', value)
					width = 0
					base = 'n'
				else:
					if not value.isInt() or value < 0:
						self.sher ("Error: expected positive integral argument for factorial.")
						return mpap(0), 0, 'd'
					else:
						try:
							value = mpap(self._factorial(int(value)))
							#dPY( "expo: _factorial returned with ", value)
						except (NameError, TypeError, ValueError, AttributeError, OverflowError):
							self.sher ("Error: illegal factorial.")
							return mpap(0), 0, 'd'
					
				self.sw()

		while self.look == chr(127):
			modulus = 0
			self.match(chr(127))
			#dPY ("raising value to Nth power")
			if self.look == '%':
				self.match('%')
				if self.look == '[':
					self.match('[')
					#modular exponentiation
					returnList = self.expr()
					modulus = returnList[0]
					self.match(']')
				else:
					self.sher ("Error: required modulus for modular exponentiation.")
					return mpap(0), 0, 'd'

			returnList = self.factor()
			exp = returnList[0]
			#dPY ("Nth power value/exp are ", value, exp)
			#dPY ("Nth power types of value/exp are ", type(value), type(exp))

			if modulus == 0:
				if exp == int(exp) and value == int(value):
					#some numbers that give reasosnably fast integer results
					#dPY ("both exp and value are ints...", lvl=11)
					try:
						value = int(value) ** int(exp)
						value = mpap(value)
					except ValueError:
						self.sher ("Error: internal math error for exponentiation (numbers too big).")
						return mpap(0), 0, 'd'
					except:
						self.sher ("Error: internal math error for exponentiation.")
						return mpap(0), 0, 'd'
				else:
					#dPY ("one or both of exp and value are fractions...", lvl=11)
					if exp != int(exp) or value != int(value):
						#either exponent or value is integer
						base = 'L' #big integer with loss of precision or any fraction
						#will need to show result as fraction
					if True:
						value = mpap(value) ** mpap(exp)
						print ("B. value is now ", value)
					try:
						print ("")
					except:
						print ("Error: type (value)=", type(value), "type(exp)=", type(exp))
						self.sher ("Error: internal math error for exponentiation or result is too big (> ~1.1878e+4932)")
						return mpap(0), 0, 'd'
					
			else:
				#modular exponentiation
				value = value.modexp (exp, modulus)

			if width > 0 and value >= (1 << width):
				self.showw ("Warning: Value of expo exceeds width specified, will be truncated to " + str(width) + "bits.")

		#dPY("expo: returning with value: ", value, "base ", base, "and width: ", width, "type of value ", type(value))
		#dPY ("expo C: type(value) is ", type(value), lvl=11)
		return value, width, base

	def validateNum (self, v, w):
		if w > 0:

			try:
				t = int(v)
				if t  >= (1 << w) and w > 0:
					#dPY ("validateNum: v is ", v, "t is ", t, "w is ", w)
					self.showw ("Warning: Value truncated to " + str(w) + " bits.")
					value = mpap(t % (1 << w))
				else:
					value = mpap(t)
			except (NameError, TypeError, ValueError, AttributeError, OverflowError):
				self.sher ("Error: BODH Expression error.")
				return mpap(0), 0, 'd'
		else:
			value = v
		return value

	def getmp (self):
		return gprec()

	def rstmp(self):
		#reset MPAP precision
		rprec()

	def setmp(self):
		#set MPAP precision
		sprec(self.rnd + self.rndpad)

	def pbodh (self, specifierWidth, base='h', parseCommaDecPt = True):
		#Process BODH Numbers
		#dPY ("pbodh: look is ", self.look)
		try:
			sw = int(specifierWidth)
		except (NameError, TypeError, ValueError, AttributeError, OverflowError):
			self.sher ("Error: illegal width.")
			return mpap(0), 0

		#dPY ("pbodh: specifierWidth = ", specifierWidth)
		self.mnsw (base)
		if self.look == '(':
			self.match('(')
			if self.look != ')':
				temp, tempWidth, tempBase = self.expr()
			else:
				self.sher ("Error: expected value within parentheses.")
				return mpap(0), 0
			self.match(')')

			#dPY ("pbodh: --- back from expression. temp is ", temp, " type(temp) is ", type(temp))
			#dPY ("pbodh: ---  sw is ", sw)
			#dPY("100. procn - 'h(expression()): temp is ", temp, "width is ", tempWidth, "base is ", tempBase)
			
			#modulus the specifierWidth
			value = self.validateNum (temp, sw)	
		else:
			if base == 'h':
				temp = self.getHexNumber()
			elif base == 'b':
				temp = self.getBinaryNumber()
			elif base == 'o':
				temp = self.getOctalNumber()
			else:
				if self.look == ' ':
					self.sher ("Error: Expected decimal number.")
					return mpap(0), 0
				temp = self.getrmp(parseCommaDecPt) #commas are not part of numbers
			#dPY("########### get**Number returned ", temp, "sw is ", sw)
			value = self.validateNum (temp, sw)	
		#dPY("pbodh: returning with value: ", value, "look is ", self.look)
		return value, sw

	def procn(self, parseCommaDecPt = True):
		#Process Numbers

		#dPY ("procn: look is ", self.look)
		#dPY ("procn: calling getRealMPAP...")
		value = self.getrmp(parseCommaDecPt)
		#dPY ("procn: getRealMPAP returned ", value, "of type ", type(value))
		#dPY ("procn: after returning from getRealMPAP, look is ", self.look)

		if self.look == "'":
			#Verilog-style width specifier has decimal point!
			if not value.isInt() or value < 0:
				self.sher ("Error: expected integer Verilog-style width specifier. ERROR 5")
				return mpap(0), 0, 'd'
			#endif

			self.mnsw ("'")
			if self.look in 'bodh':
				base = self.look
				value, width = self.pbodh (value, base, parseCommaDecPt)
				#print ("procn: BODH returned", value, width)
			else: #no 'd' or 'h' or 'd'
				self.sher ("Error: Expected 'h', 'o', 'b', or 'd' base indicator")
				return mpap(0), 0, 'd'
			#endif
		else:
			#just plain decimal number
			width = 0
			base = 'd'
			#dPY("procn: else ---: ", value, " and width: ", width, "type of value ", type(value))
	
		self.sw()

		#dPY("procn: returning with value: ", value, " and width: ", width, "type of width ", type(width))
		#dPY("procn: returning with value: ", value, "look is ", self.look)
		return value, width, base

	#enddef procn

	def procvn (self, parseCommaDecPt = True):
		#parseCommaDecPt -- if True, commas can be placed in decimal
		#numbers
		#dPY("Entered procvn... ")

		value = mpap(0)
		width = 0
		base = 'd'
		varName = "#NULLVARIABLENAME#"
		maxBitPos = -1
		minBitPos = -1

		if self.enn != '':
			#dPY ("Seen error -- now returning with ------------------ ERROR", self.enn)
			return value, width, base, varName, maxBitPos, minBitPos
	
		#dPY ("procvn: Just entered... look is ", self.look)
		isLValue = 0
		if self.look == '[':
			#dPY ("~~~~~~~~~~~ look = [ ------------ look is ", self.look)
			#imaginary number
			#multiply by i
			self.match('[')
			value, width, base= self.expr()
			base = 'd' #force base to decimal
			#dPY ("procvn: complex: expr returned: ", value.__repr__())
			value = mpap (Mantissa=-value.IM, Exponent=value.IE, IM=value.Mantissa, IE=value.Exponent, InternalAware = True)
			#dPY ("procvn: complex: value set to: ", value.__repr__())
			self.match(']')
			
		elif self.look == '{':
			#dPY ("~~~~~~~~~~~ look = { ------------ look is ", self.look)
			self.match('{')
			catList = self.cat()
			if len (catList) > 0:
				value, width, base, isLValue, allList = catList
			#dPY ("procvn: returned from catenation with value of type: ", type(value))
			#dPY ("procvn: returned from catenation with catList: value = ", catList[0])
			#dPY ("procvn: returned from catenation with catList: catList = ", catList)
			#dPY('')
			#dPY ("procvn: returned from catenation with catList: allList = ", allList)
			#dPY('')
			if self.look == '{':
				self.match('{')
				try:
					replicationCount = value
				except:
					self.sher ("Error: incorrect replication.")
					return mpap(0), 0, 'd', "#NULLVARIABLENAME#", -1, -1
				#get base from the inner number
				catList = self.cat()
				if len (catList) != 0:
					value, width, base = catList[0:3]

				#dPY("procvn: --- replicationCount=", replicationCount)
				#dPY("procvn: --- inner value=", str(value))
				#dPY("procvn: --- inner width=", str(width))
				runningValue = mpap(0)
				for i in range(int(replicationCount)):
					#width is of the inner number
					runningValue = value + (runningValue << width)
				
				value = runningValue

				#get replicated width
				width = int(replicationCount * width)
				#dPY("procvn: --- width = ", width)
				
				self.match('}')
				self.match('}')
			else:
				self.match('}')
				#dPY("Found right brace")
				#get the variable list from
				if self.look == '=':
					self.match('=')
					value, width, base = self.expr()
					#dPY ("######## ===== procvn: returned from expr with value = ", value, " width = ", width)
				
					if isLValue == False:
						self.sher ("Error: can only assign values to variables.")
						return mpap(0), 0, 'd', "#NULLVARIABLENAME#", -1, -1
					else:
						#assign to LValue
						#dPY ("procvn: matched first { with }: allList = ", allList)
						#dPY('')
						allList.reverse()
						#dPY ("procvn: reversed allList = ", allList)
						#dPY('')

						#make a list of sublists of allList, each containing
						#min, max, varname, base, width, value
						listOfSublists = list(self.sublist(allList, 6))
						#dPY ("######## ===== procvn: listOfSublists = ", listOfSublists, lvl=10)
						runningValue = mpap(value)
						itemNum = 0
						for item in listOfSublists:
							itemNum += 1
							mn, mx, vn, b, w, v = item
							#extract value from RHS
							#dPY("######## ===== procvn: mx=", mx, " mn=", mn, " vn=", vn, " b=", b, " w=", w, " v=", v)
							#dPY ("######## ===== procvn: runningValue = ", value)
							vw = 0
							if vn in self.stw.keys():
								#vn already exists
								if self.stw[vn] != 0:
									vw = self.stw[vn]
									mx = vw - 1
									mn = 0
							if vw == 0:
								if mx == -1 and mn == -1:
									if itemNum < len(listOfSublists):
										self.showw (f"Warning: Width of {vn} unspecified. Will assume {self.defw}.")
									else:
										self.showw (f"Warning: Width of {vn} unspecified.")
									vw = self.defw
									mx = vw - 1
									mn = 0
								else:
									vw = int(mx - mn + 1)
							#dPY ("######## ===== procvn: varWidth=" + str(vw), " type of vw is ", type(vw), "for var=", vn, lvl=10)
							#dPY ("######## ===== procvn: width=" + str(width), " type of vw is ", type(width), "for var=", vn, lvl=10)
							try:
								assv = mpap(int(runningValue) % (1<<vw))
								if vw > 0:
									#show warning only for the variable in the most significant position
									if int(runningValue) >= (1<<vw) and itemNum == len(listOfSublists):
										self.showw ("Warning: " + str(runningValue) + f" is larger than can be fit in {vw} bits of variable {vn}.")
								#dPY ("######## ===== procvn: runningValue = ", runningValue)
								#dPY ("######## ===== procvn: vw = ", vw)
								#dPY ("######## ===== procvn: assv = ", assv)
							except (NameError, TypeError, ValueError, AttributeError, OverflowError):
								self.sher ("Error: math error with '" + str(value) + "' and left shift.")
								return mpap(0), 0, 'd', "#NULLVARIABLENAME#", -1, -1
									
							#dPY ("######## ===== procvn: assignmentValue=", assv)
							#prepare value for the next assignment to the next variable
							try:
								runningValue = mpap(int(runningValue) >> vw)
								#dPY ("######## ===== procvn: after shift right by ", vw, " bits, new runningValue = ", value)
							except (NameError, TypeError, ValueError, AttributeError, OverflowError):
								self.sher ("Error: math error with '" + str(value) + "' and right shift.")
								return mpap(0), 0, 'd', "#NULLVARIABLENAME#", -1, -1
							#dPY ("new value=" + str(value))
							
							if vn not in self.stv.keys():
								#dPY('')
								#dPY ("######## ===== procvn: about to create variable with name = ", vn)
								#dPY ("######## ===== procvn: Error Notif  = ", self.enn)
								#dPY('')
								if self.enn == '': #don't create variable in case an earlier variable access error was seen
									self.stv[vn] = mpap(0)
									self.stb[vn] = 'd'
									self.stw[vn] = w
							else:
								#if old width is less than the bit field [maxBitPos:minBitPos], increase the width
								if vw > self.stw[vn] and self.stw[vn] > 0 and self.twa == True:
									#dPY("WARNING: A will be overridden by bit range ... vw = ", vw, f" self.stw[{vn}] = ", self.stw[vn], lvl=10)
									self.showw ("Warning: width " +  str(self.stw[vn]) + " will be overridden by bit range [" + str(mx) + ":" + str(mn) + "].")
									self.stw[vn] = vw
							#endif
				
							#iterate through variable and zero out the bit fields [maxBitPos:minBitPos]
							i = mn
							if vn in self.stv.keys():
								while i <= mx:
									if (int(self.stv[vn]) >> i) & 0x1 == 1:
										try:
											self.stv[vn] = mpap(int(self.stv[vn]) - (1<<i))
										except (NameError, TypeError, ValueError, AttributeError, OverflowError):
											#since we see an error, must delete the Symbol Table entry
											#created earlier
											del self.stv[vn]
											del self.stb[vn]
											del self.stw[vn]
											self.sher ("Error: Illegal bit index. ERROR 5.")
											return mpap(0), 0, 'd', "#NULLVARIABLENAME#", -1, -1
									#endif
									i += 1
								#endwhile 
								self.stv[vn] = self.stv[vn] + (assv<<mn)
								self.stb[vn] = base
								if self.stw[vn] > 0:
									assumed = 'assumed'
									stwidth = self.stw[vn]
								else:
									assumed = ''
									stwidth = self.defw
								if self.stv[vn] > (1 << stwidth):
									self.showw ("Warning: " + assumed + "width of variable " + vn + " is too small, "+  str(stwidth) +  ". Will snip upper bits of result.")
									self.stv[vn] = mpap(int(self.stv[vn]) % (1 << self.stw[vn]))
							else:
								self.sher (f"Error: Variable '{vn}' accessed before assignment.", overridePrevErr = True)
								return mpap(0), 0, 'd', "#NULLVARIABLENAME#", -1, -1
		
							#dPY ("New stv[vn]=", self.stv[vn])
						#endfor item in reversedAllList
					#endif
				#endif look
			#endif
			
		elif self.nums() == True:
			#dPY ("~~~~~~~~~~~ number starting ------------ look is ", self.look)
			value, width, base = self.procn(parseCommaDecPt)
			#dPY ("procvn: --- back from procn. value is ", value)
			#dPY ("procvn: --- back from procn. value is ", value, " type(value) is ", type(value))
		elif self.vns(): #variable name starting
			#dPY ("~~~~~~~~~~~ variable starting ------------ look is ", self.look)
			#dPY ("procvn: --- calling procv.")
			value, width, base, varName, maxBitPos, minBitPos = self.procv()
			#dPY ("procvn: --- back from procv. value is ", value, "varName is ", varName, "width is ", width)
			#dPY ("procvn: --- back from procv. value is ", value, " type(value) is ", type(value), "base is ", base, lvl=10)
		else:
			#dPY ("======procvn: else -- look is ", self.look)
			value, width, base= self.expr()
			#dPY ("procvn: --- back from expression. value is ", value, " type(value) is ", type(value))
		
		#dPY ("procvn ======== calling procbs look is ", self.look)
		value, width, base = self.procbs (value, width, base)
		#dPY ("procvn ========  returned from procbs look is ", self.look)

		#dPY("------procvn... NOW returning with value ", value.__repr__(), " and type value ...", type(value), lvl=11)
		#dPY (value, width, base, varName, maxBitPos, minBitPos)
		return value, width, base, varName, maxBitPos, minBitPos

	def factor (self):
		#dPY("factor: look is ", self.look)
		if self.look == '(':
			#dPY ("factor: calling self.match...")
			self.match('(')
			#dPY("factor: matched (. Now look is ", self.look)
			#dPY ("factor: calling expression...")
			if self.look != ')':
				returnList = self.expr()
			else:
				#handle parentheses enclosing null parameters
				self.sher ("Error: expected value within parentheses.")
				return [mpap(0), 0, 'd']
			#dPY ("factor: returned from expression... with returnList ", returnList)
			self.match(')')
			value, width, base = returnList[0:3]
			value, width, base = self.procbs (value, width, base)
			#dPY ("factor A:  value is ", value, " of type ", type(value))
			returnList = [value, width, base]
		else:
			#dPY ("factor: calling procvn...")
			returnList = list(self.procvn())
			value, width, base = returnList[0:3]
			#dPY ("factor B:  value is ", value, " of type ", type(value), lvl=11)
			#dPY ("factor: returned from procvn... with returnList ", returnList)
			#dPY ("factor: returned from procvn... with value ", value)
		
		return returnList

	def ismulop (self, c):
		if self.look == '*' or self.look == '/' or self.look == '<' or self.look == "\\" or\
				self.look == '>' or self.look == '%' or self.look == '&' or self.look == chr(127) or\
				self.look == '!' or self.look == '=':
			return True
		else:
			return False

	def term (self):
		#dPY("term: look is ", self.look)
		#dPY("term: calling red...")
	
		value, width, base = self.red()

		#dPY ("term: returned from red... with type (value) ", type (value))

		while self.ismulop(self.look):
			#dPY ("term: inside 'while ismulop'... look is ", self.look)
			if self.look == '>':
				#dPY ("term: matching '>'")
				self.mnsw ('>')
				if self.look == '>':
					#found '>>'
					self.match('>')
					exp = self.red()[0]
					if not exp.isInt() or exp < 0:
						self.sher ("Error: expected postive left-shift argument.")
						return mpap(0), 0, 'd'

					if exp < 0 or value < 0:
						self.sher ("Error: expected postive right-shift argument.")
						return mpap(0), 0, 'd'
					else:
						value = value >> exp
				else:
					value = self.cmpop ('>', value)
					width = 0
					base = 'n'

			elif self.look == '<':
				#dPY ("term: matching '<'")
				self.mnsw('<')
				if self.look == '<':
					#found '<<'
					self.match('<')
					exp = self.red()[0]
					#dPY("++++++++++++++++++LSHIFT operator: value ----->", exp, "type is ", type(exp))
					if not exp.isInt() or exp < 0:
						self.sher ("Error: expected postive left-shift argument.")
						return mpap(0), 0, 'd'

					if exp < 0 or value < 0:
						self.sher ("Error: expected postive left-shift argument.")
						return mpap(0), 0, 'd'
					else:
						value = (value << exp)
					
				else:
					value = self.cmpop ('<', value)
					width = 0
					base = 'n'
				
			elif self.look == '=':
				#dPY( ("term: matching '='"))
				#can only be the equality operator
				self.mnsw('=')
				if self.look == '=':
					self.match('=')
					#dPY( ("term: matching '=='"))
					value = self.cmpop ('=', value)
					width = 0
					base = 'n'
					#dPY ("term: returned from comparison == with type value ", type(value))
				else:
					self.sw()
					#dPY ("term: look is ", self.look)
					if self.look == '=':
						self.sher ("Error: expected equality operator '=='.")
						return mpap(0), 0, 'd'
					else:
						self.sher ("Error: Cannot assign to a constant lvalue.")
						return mpap(0), 0, 'd'
			elif self.look == '*':
				#dPY( ("term: matching '*'"))
				self.match('*')
				#dPY( "term: calling red with matched *")
				mul, mulwidth, mulbase = self.red()
				if (width == 0 or mulwidth == 0) and self.aaw == True:
					width = 0

				widthForMult = width
				if width == 0:
					widthForMult = self.defw

				mulwidthForMult = mulwidth
				if mulwidth == 0:
					mulwidthForMult = self.defw
				
				if value == int(value) and mul == int(mul):
					try:
						value = int(value) * int(mul)
						value = mpap(value)
					except (NameError, TypeError, AttributeError, SyntaxError, ValueError, OverflowError):
						self.sher ("Error: illegal multiplication operation.")
						return mpap(0), 0, 'd'
				else:
					try:
						#dPY("term: : value is ", value)
						value =  mpap(value) * mpap(mul)
					except (NameError, TypeError, AttributeError, SyntaxError, ValueError, OverflowError):
						self.sher ("Error: illegal multiplication operation.")
						return mpap(0), 0, 'd'
						#dPY("term: done multiplication: value is ", value)
					
				if width > 0 and value >= (1 << width):
					self.showw ("Warning: Value of term exceeds width specified, will be truncated to " + str(width) + " bits.")
				
			elif self.look == '!':
				#dPY("term: ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~value is ", value)
				self.mnsw('!')
				#dPY( "term: matching '!'")

				if self.look == '=':
					#inequality operator
					#found '=='
					self.match('=')
					value = self.cmpop ('!', value)
					width = 0
					base = 'n'

				elif self.fhhp == False:
					#factorial operator '!' has same precedence as * and / -- handle
					#it here and not in function expo
					#dPY( "##################################term: calling _factorial with matched value ", value)
					if not value.isInt() or value < 0:
						self.sher ("Error: expected positive argument for factorial.")
						return mpap(0), 0, 'd'
					try:
						value = self._factorial(value)
						#dPY( "term: _factorial returned with ", value)
					except (NameError, TypeError, ValueError, AttributeError, OverflowError):
						self.sher ("Error: illegal factorial.")
						return mpap(0), 0, 'd'
					
					self.sw()
				#endif	
			elif self.look == '&':
				#dPY("term: matching '&'")
				self.match('&')
				if self.look == '&':
					#found '&&'
					self.match('&')
					#dPY("term: calling red with matched &&")
					reduc = self.red()[0]
					#dPY("value1 is ", value, "reduc is ", reduc, lvl=11)
					try:
						value = value and reduc
						if value == 0:
							value = False
						else:
							value = True
						base = 'n'
					except (NameError, TypeError, ValueError, AttributeError, OverflowError, SyntaxError):
						self.sher ("Error: illegal logical and.")
						return mpap(0), 0, 'd'
					#dPY("result of && is ", value, lvl=11)
				else:
					#dPY("term: calling red with matched &")
					secondValue, secondWidth, secondBase = self.red()
					if (width == 0 or secondWidth == 0) and self.aaw == True:
						width = 0
					try:
						value = value & secondValue
					except (NameError, TypeError, ValueError, AttributeError, OverflowError, SyntaxError):
						self.sher ("Error: illegal bitwise and.")
						return mpap(0), 0, 'd'
					#dPY("result of & is ", value)
				
			elif self.look == '\\':
				#dPY( "term: matching '\'")
				self.match("\\")
				if self.look == '\\':
					#match \\ as well!
					self.match("\\")
				#dPY( "term: calling red with matched \\")
				div = self.red()[0]
				if div != 0:
					try:
						if value == int(value) and div == int(div):
							value = int(value) // int(div)
							value = mpap(value)
						else:
							value = value // div
					except:
						self.sher ("Error: illegal division.")
						return mpap(0), 0, 'd'
				else:
					self.sher ("Error: Division by 0!")
					return mpap(0), 0, 'd'

			elif self.look ==  '/':
				#dPY( "term: matching '/'")
				self.match('/')
				if self.look == '%':
					self.match('%')
					if self.look == '[':
						#modular inversion followed by multiplication with
						#the numerator
						#1 /[11] 7 is modular inverse of 7 mod 11
						#4 /[11] 7 is modular inverse of 7 mod 11 multiplied by 4, product mod 11
						self.match('[')
						returnList = self.expr()
						modulus = returnList[0]
						self.match(']')
						div = self.red()[0]
						if modulus == 0 or div == 0:
							self.sher ("Error: illegal modular inversion.")
							return mpap(0), 0, 'd'
						value = value * div.modinv(modulus)
						value = value % modulus
					else:
						self.sher ("Error: required modulus for modular inversion.")
						return mpap(0), 0, 'd'
				else:
					doIntDiv = False
					if self.look ==  '/':
						#double // is Python integer division
						self.match('/')
						doIntDiv = True
					div = self.red()[0]
					if div != 0:
						try:
							if doIntDiv == True:
								if value == int(value) and div == int(div):
									value = int(value) // int(div)
									value = mpap(value)
								else:
									value = value // div
							else:
								v = mpap(value) / mpap(div)
								value = mpap(v)
						except (NameError, TypeError, ValueError, AttributeError, OverflowError, SyntaxError):
							if doIntDiv == False:
								self.sher ("Error: illegal division.")
								return mpap(0), 0, 'd'
							else:
								self.sher ("Error: illegal integer division.")
								return mpap(0), 0, 'd'
					else:
						self.sher ("Error: Division by 0!")
						return mpap(0), 0, 'd'

			elif self.look == '%':
				#dPY( "term: matching '%'")
				self.match('%')
				div = self.red()[0]
				#dPY( "#####-----------##### term: returned from red with divisor div")
				if div != 0:
					try:
						value = value % div
					except (NameError, TypeError, ValueError, AttributeError, OverflowError, SyntaxError):
						self.sher ("Error: illegal remainder operation.")
						return mpap(0), 0, 'd'
				else:
					self.sher ("Division by 0!")
					return mpap(0), 0, 'd'
			else:
				self.sher ("Error: expected multiplicative operator.")
				return mpap(0), 0, 'd'
		#endwhile

		#dPY( "#####-----------##### term: returning with value ", value, lvl=11)
		#dPY( "term: returning with value ", value, "and type(value)", type(value), lvl=11)
		return value, width, base

	def inite(self):
		#Initialize Evaluator
		self.getch()
		self.sw()

	def iro (self, c):
		#is reduction operator
		#Verilog reduction operator -- |, &, ^
		return (c == '^' or c == '|' or c == '&' or c == '!')

	def iuo (self, c):
		#is unary operator
		return (c == '+' or c == '-' or c == '~')

	def iao (self, c):
		#is additive operator
		return (c == '+' or c == '-' or c == '^' or c == '|')

	def nums (self):
		#'hAB or 'd12 or 1001 are valid numbers
		#numbers cannot start with '_'
		#dPY ("======================= look is ", self.look)
		return (self.look.isdigit() or self.look == "'" or  self.look == '.')

	def vns (self):
		#var Name Starting
		#variable names can start with '_'
		return (self.look.isalpha() or self.look == '_')

	def una (self):

		unaryOp =  self.look
		self.match(self.look)
		value, width, base = self.expo()
		#dPY("una: returned from expo value is ", value, "type of value is ", type(value))

		if unaryOp == '~':
			value = self.douo(value, '~', 'bitwise inversion')
		elif unaryOp == '-':
			value = self.douo(value, '-', 'negation')
		#else, for unary '+', just return the incoming number
		return value, width, base

	def red (self):
		#reduction
		#dPY("red: called with look ", self.look)
		if self.iro(self.look):
			rop = self.look
			self.match(self.look)
		
			#dPY("red: found rop, now calling expo... look is self.look")
			returnList = self.expo()
			value, width, base = returnList[0:3]
			#dPY("TEST red: returned from expo... with value ", value, width, base)
			if not value.isInt():
				self.sher ("Error: Cannot reduce non-integers. ERROR 17.")
				return mpap(0), 0, 'd'
				#dPY("red: rop is ", rop)
			elif rop == '!':
				#dPY("red Z@@@@@@@@@@@@Z: Unary logical NOT !, value is ", value)
				value = self.douo(value, '!', 'logical negation')
				#invert

			elif rop == '|':
				running = mpap(0)
				#dPY("red|: At first running to running. value is value")
				while value > 0:
					running = (value & 0x1) | running
					#dPY("red|: set running to ", running)
					value = (value >> 1)
					#dPY("red|: set value to ", value)
				
				value = running
				#dPY("red|: Finally, value is ", value)

			elif rop == '&':
				running = mpap(1)
				#dPY("red&: At first running to running. value is value")
				while value > 0:
					running = (value & 0x1) & running
					#dPY("red&: running to ", running)
					value = (value >> 1)
					#dPY("red&: value to value")
				
				value = running
				#dPY("red&: Finally, value is ", value)
			elif rop == '^':
				running = mpap(0)
				#dPY("red^: At first running to running. value is ", value)
				while value > 0:
					running = (value & 0x1) ^ running
					#dPY("red&: running to ", running)
					value = (value >> 1)
					#dPY("red&: value to value")
				
				value = running
				#dPY("red&: Finally, value is ", value)
			else:
				self.sher ("Error: expected reduction operator.")
				return mpap(0), 0, 'd'
		else:
			#dPY("red: calling expo... look is ", self.look)
			value, width, base = self.expo()
			#dPY("TEST2 expression: returned from expo... with value ", value, width, base)
			#dPY("red: returned from expo value is ", value, "type of value is ", type(value))
		
		#dPY("red: expo returned value ", value, "base ", base)
		#dPY ("red: returning from red... with type (value) ", type (value))
		return value, width, base

	def procbs (self, value, width, base):
		#Process Bit Slices
		maxBitPos = -1
		minBitPos = -1

		#dPY ("======== entered procbs look is ", self.look)
		if type(value) == bool or type(value) == set or type(value) == str:
			return value, width, base

		if self.look == '[':
			self.match('[')
			try:
				maxBitPos = int(self.expr()[0])
				if maxBitPos < 0:
					raise VexError
			except VexError:
				self.sher ("Error: Negative indices not allowed.")
				return mpap(0), 0, 'd'
			except:
				self.sher ("Error: Illegal index.", True)
				return mpap(0), 0, 'd'
			if self.look == ':':
				self.match(':')
				try:
					minBitPos = int(self.expr()[0])
					if minBitPos < 0:
						raise VexError
				except VexError:
					self.sher ("Error: Negative indices not allowed.")
					return mpap(0), 0, 'd'
				except:
					self.sher ("Error: Illegal lower index.", True)
					return mpap(0), 0, 'd'
			self.match(']')

		if maxBitPos != -1:
			if minBitPos != -1:
				if minBitPos > maxBitPos:
					self.sher ("Error: Larger lower index.")
					return mpap(0), 0, 'd'
				elif maxBitPos == minBitPos:
					#treat as single specifier case
					#handle in the "if minBitPos == -1" clause
					minBitPos = -1

			if minBitPos == -1:
				#One max position Verilog-style bit field specifier
				try:
					value = mpap((int(value) >> maxBitPos) % 2)
				except (NameError, TypeError, ValueError, AttributeError, OverflowError):
					self.sher ("Error: Illegal bit index. ERROR 1221.")
					return mpap(0), 0, 'd'
			else:
				#Both max and min position Verilog-style bit field specifier found
				if minBitPos > maxBitPos:
					self.sher ("Error: expected smaller 'downto' index. ERROR 1221.")
					return mpap(0), 0, 'd'
				if minBitPos >= 0 and maxBitPos >= 0:
				
					assw = maxBitPos - minBitPos + 1
					if width < assw and width != 0:
						self.showw ("Warning: width" + str(width) + " is less than bit range  [" + str(maxBitPos) + ":" + str(minBitPos) + "].")
					elif width == 0:
						bl = int(value).bit_length()
						if assw > bl:
							self.showw ("Warning: width not specified, but [" + str(maxBitPos) + ":" + str(minBitPos) + "] exceeds " + str(bl) + " needed.")
				
					#dPY("processBitSlices ------- assignmentWidth=", assw, "width", )
					if width > assw and self.twa == True:
						#dPY("WARNING: B will be overridden by bit range ... ", lvl=10)
						self.showw ("Warning: width " +  str(width) + " will be overridden by bit range [" + str(maxBitPos) + ":" + str(minBitPos) + "].")
		
					if self.twa == True and width > 0:
						width = assw

					try:
						vslcd = mpap((int(value) >> minBitPos) % (1<<assw)) #value sliced
						if value > vslcd:
							self.showw ("Info: value " + str(value) + " sliced to " + str(vslcd))
							value = vslcd
					except (NameError, TypeError, ValueError, AttributeError, OverflowError):
						self.sher ("Error: Illegal bit slice operation!. ERROR 1221.")
						return mpap(0), 0, 'd'

		return value, width, base

	def douo (self, value, op, opName):
		#do unary ops
		#dPY("douo: found ", op)
		try:
			if op == '-':
				value = -mpap(value)
			elif op == '!':
				#print ("value received is ", value)
				if bool(int(value)) == False:
					value = True
				else:
					value = False
				#print ("value returned is ", value)
			elif op == '~':
				value = ~mpap(value)
		except (NameError, TypeError, ValueError, AttributeError, OverflowError):
			value = mpap(0)
			self.sher ("Error: illegal operand type with " + opName + " operator.")

		return value
	
	def dobo (self, value, op, opName):
		secondValue, secondWidth, secondBase = self.term()
		try:
			if value == int(value) and  secondValue == int(secondValue):
				try:
					if op == '+':
						value = int(value) + int(secondValue)
						value = mpap(value)
					elif op == '^':
						value = int(value) ^ int(secondValue)
						value = mpap(value)
					elif op == '|':
						value = int(value) | int(secondValue)
						value = mpap(value)
					elif op == '||':
						value = bool(value) or bool(secondValue)
					elif op == '-':
						value = int(value) - int(secondValue)
						value = mpap(value)
				except (NameError, TypeError, ValueError, AttributeError, OverflowError):
					value = mpap(0)
					self.sher ("Error: illegal operand type with " + opName + " operator.")
			else:
				try:
					if op == '+':
						value = mpap(value) + mpap(secondValue)
					elif op == '^':
						value = mpap(value) ^ mpap(secondValue)
					elif op == '|':
						value = mpap(value) | mpap(secondValue)
					elif op == '||':
						value = bool(mpap(value)) or bool(mpap(secondValue))
					elif op == '-':
						value = mpap(value) - mpap(secondValue)
				except (NameError, TypeError, ValueError, AttributeError, OverflowError):
					value = mpap(0)
					self.sher ("Error: illegal operand type with " + opName + " operator.")
		except:
			value = mpap(0)
			self.sher ("Error: illegal operands with " + opName + " operator.")

		return value, secondWidth
		
	def expr (self):
		
		#dPY("expression: look is ", self.look)

		#this is to handle infinite recursion
		#dPY("expression: excc is ", self.excc)
		if self.insp == self.iris and self.excc > 2:
			#insp hasn't progressed since last call to expression
			#this will lead to infinite recursion and stack overflow
			dPY ("expression: will lead to infinite recursion and stack overflow excc = ", self.excc)
			dPY ("expression: will lead to infinite recursion and stack overflow insp = ", self.insp)
			dPY ("expression: will lead to infinite recursion and stack overflow insp = ", self.insp)
			#dPY ("----------ERROR enn is ", self.enn)
			self.sher ("Error: cannot evaluate input.")
			self.excc = 0 
			return mpap(0), 0, 'd'

		self.iris = self.insp
		self.excc += 1
		
		#dPY("expression: calling term...")
		value, width, base = self.term()
		#dPY("expression: returned from term... with value ", value, width, base, lvl=11)
		#dPY("expression: after returning from term, look is ", self.look)
		#dPY("expression: returned from term... with type (value) ", type(value), lvl=11)

		while self.iao(self.look):
			#print ("look is addop ", self.look)

			if self.look == '+':
				self.match('+')
				value, secondWidth = self.dobo(value, '+', 'addition')
				if (width == 0 or secondWidth == 0) and self.aaw == True:
					width = 0
				if width > 0 and value >= (1 << width):
					self.showw ("Warning: Value of expression exceeds width specified, " + str(width) + ". Will be truncated to " + str(width) + "bits.")

			elif self.look == '^':
				self.match('^')
				#### dPY("expression: found ^, calling term")
				value, secondWidth = self.dobo(value, '^', 'excl. or')
				if (width == 0 or secondWidth == 0) and self.aaw == True:
					width = 0

			elif self.look == '|':
				self.match('|')
				if self.look == '|':
					self.match('|')
					value, secondWidth = self.dobo(value, '||', 'logical or')
					if (width == 0 or secondWidth == 0) and self.aaw == True:
						width = 0
					base = 'n'
				else:
					value, secondWidth = self.dobo(value, '|', 'bitwise or')
					if (width == 0 or secondWidth == 0) and self.aaw == True:
						width = 0
		
			elif self.look == '-':
				self.match('-')
				#print ("look is MINUS ", self.look)
				value, secondWidth = self.dobo(value, '-', 'subtraction')
				if (width == 0 or secondWidth == 0) and self.aaw == True:
					width = 0
			else:
				self.sher ("Error: expected additive operator.")
				value = mpap(0)
				return value, 0, 'd'
			#endif
		#endwhile

		#dPY ("~~~~~~~~~~~~~~~~~~~~expression: ~~~~~~~~~~~~~~~~~~~~~~~~~~~ value is ", value, " of type ", type(value))
		
		if width != 0:
			#only for integers whose width is specified
			try:
				value = mpap(int(value) % int((1<<width)))
			except:
				self.sher ("Error: Expression error.")
				return mpap(0), 0, 'd'
		
		#dPY ("expression: YYY ", value, width, base)
		#dPY ("expression: YYY type of value", type(value))

		#dPY ("~~~~~~~~~~~~~~~~~~~~expression: ~~~~~~~~~~~~~~~~~~~~~~~~~~~ now value is ", value)

		#dPY ("expression: ZZZ returning with value ", value, width, base, lvl=11)
		#dPY("at end of expression: look is ", self.look)
		#dPY ("expression: ZZZ returning with value of type ", type(value))

		#print ("done with expression. look is ", self.look)
		return value, width, base


	def ev (self, s):

		#'#' is a comment start indicator
		#split on '#' and take only the first part
		#eval string
		es = s.split('#')[0]
		#dPY("evaluate: User es is ", es)

		#the raise-to operator ** is replaced by a single char chr(127)
		es = es.replace('**', chr(127))

		#dPY( "evaluate: at start es is ", es)
		self.insp = 0
		self.iris = -1
		r = []
		#dPY ( "evaluate: at start es is ", es)
		
		if es != '':
			#use the unsplit inps for computation
			self.inps = es
			self.inite()

			#MicroPython-specific code
			sprec(self.rnd + self.rndpad)
			startTime = time.time()
			#dPY("====================", lvl=10)
			#dPY("startTime is ", startTime)
			returnList = self.expr()
			#dPY("done with expression, look is ", self.look)
			#endTime = time.time()
			#dPY("endTime is ", endTime, lvl=11)
			self.cxt = (time.time() - startTime)*1000
			#dPY("cxt is ", self.cxt)
			
			if self.enn == '':
				value, width, base = returnList[0:3]
				dPY( "4.A evaluate: value is ", value.__repr__(), "and type of value is ", type(value), "  base = ", base, lvl=11)
				if base == 'n':
					if value == 0:
						r = [' ans = False']
						value = False
					else:
						r = [' ans = True']
						value = True
					self.stv['ans'] = value
					self.stw['ans'] = width
					self.stb['ans'] = base 
					self.vir['ans'] = False
				if type(value) == type(None):
					#catchall for bugs
					self.sher ("Error: Unknown function or command.")
					return ['', '', '', '', "Error: Unknown function or command.", '']
				elif type(value) == str:
					self.stv['ans'] = value
					self.stw['ans'] = width
					self.stb['ans'] = base 
					self.vir['ans'] = False
					return ['', value, '', '', '', '']
				elif type(value) == bool:
					self.stv['ans'] = value
					self.stw['ans'] = width
					self.stb['ans'] = base 
					self.vir['ans'] = False
					return [' ans = ', str(value), '', '', '', '']
				elif value.isNone() == False and value.isNaNInf() == False:
					#print ("APBF_PRECISION = ", gprec())
					if abs(value) < mpap(1, -self.rnd):
						value = mpap(0)

					#dPY ("3.X. evaluate: value is ", repr(value), "width is ", width, "base is ", base, "self.rnd is ", self.rnd, lvl=11)
					if self.rnd < 10000:
						if width > 0 and value >= (1<<width):
							self.showw ("Warning: Value exceeds width of data, " + str(width) + ". Will be truncated to " + str(width) + "bits.")
							#dPY ("Warning: Value exceeds width of data, will be truncated to ", width, "bits.")
							value = value % (1<<width)
							#dPY("3. evaluate: value is ", value, "max value for this width is ", (1 << width))
						
						if width > 0 and value < 0:
							#negative numbers
							value = value % (1<<width)
							#dPY("4. evaluate: value is ", value, "max for this width is ", (1 << width), lvl=11)
					
						#dPY( "4AABB. evaluate: value is ", value, "and type of value is ", type(value), lvl=11)
						#dPY( "4AABB. evaluate: rounded value is ", value.re().nround(self.rnd), lvl=11)

						#dPY("#### + width ~~~~~~~~~~~~~~~~ width is ", width)
						if value < 0 and value.isInt():
							if width > 0:
								value = value + (1<<width)
							elif base != 'd':
								#width = 0 and hex or binary
								value = value + (1<<32)
					
					#dPY ("BEGIN QWER. value.Imaginary Mantissa = ", value.IM)
					#dPY("-----------------######################------------------", lvl=10)
					#dPY ("before rounding with preci=", self.rnd, "value=", value, "isInt=", value.isInt(), 
					#	"type of value is ", type(value), "base = ", base, lvl=11)
					vIsInt = value.isInt() and base != 'L'
					#dPY ("vIsInt = ", vIsInt, " ## value.isIntIm() = ", value.isIntIm(), lvl=100)
					if (vIsInt == False or value.isIntIm() == False):
						#Round off floating point numbers
						#dPY ('++Clause A')
						#dPY ('++++Clause A.2.1 REAL value=', value, lvl=10)
						im = mpap(0)
						if value.isComplex():
							#dPY ('++++Clause A.1')
							im = value.im()
							#dPY ('++++Clause A.2.2 IMAG value=', value, lvl=10)
							if im.Exponent < 0:
								im = im.nround(self.rnd)
							else:
								ve = im.Exponent
								val = mpap(im)
								val.Exponent = 0
								val = val.nround(self.rnd)
								im = mpap(val.Mantissa, im.Exponent, InternalAware=True)

						re = value.re()
						if value.Exponent < 0:
							value = re.nround(self.rnd)
							#dPY ("A. doing rounding with preci=", self.rnd, "value=", value, "type of value is ", type(value), lvl=10)
						else:
							ve = re.Exponent
							val = mpap(re)
							#print (" @@@1 val = ", val)
							val.Exponent = 0
							val = val.nround(self.rnd)
							#print (" @@@2 val = ", val)
							value = mpap(val.Mantissa, value.Exponent, InternalAware=True)
							#dPY ("B. doing rounding with preci=", self.rnd, "value=", value, "type of value is ", 
							#	type(value), lvl=100)
						
						#attach the imaginary component found earlier
						#for real nos., im = 0
						value = value.im(im)
						#dPY ("ZZ after rounding with preci=", self.rnd, "value=", value, "type of value is ", type(value), 
						#		" value.Exponent = ", value.Exponent, " vIsInt=", vIsInt,
						#		lvl=100)
						if (abs(value.Exponent) <= self.rnd or (value.isComplex() and abs(value.IE) <= self.rnd)):
							#display 'small' numbers as int -- 1.0 as 1
							vIsInt = value.isInt()

					if value.Exponent < -self.rnd:
						value.Mantissa = value.Exponent = 0
					if value.IE < -self.rnd:
						value.IM = value.IE = 0

					self.stv['ans'] = value
					self.stw['ans'] = width
					self.stb['ans'] = base 
					self.vir['ans'] = vIsInt 
					#dPY ("after rounding with preci=", self.rnd, "value=", value.__repr__(), " is int = ", vIsInt, lvl=10)
					r = [' ans = '] + self.prnv(var = 'ans', vi = vIsInt)
					#print (f"ev: r returned by PRNV = {r}")
				
				if type(value) != bool and type(value) != str and type(value) != type(None):
					if value.isNaNInf() == True:
						self.enn = "Error: result is not a number or is undefined."
					elif value.isNone() == True:
						#print of result has been done by the function such as factors
						r = ['', '', '']

			self.match('')

			#r list has at this point 4 elements (strings) for the value
			if self.wnn != [] and self.showws == True:
				#add a null error string and the warning string
				r += ['', self.wnn.pop()]
			else:
				r += ['', '']
			#r list has at this point 4 elements (strings) for the value
			#a null error string and a warning string

			if self.enn != '':
				r = ['', '', '', '', self.enn] 
				if self.wnn != []:
					r += ["Also: " + self.wnn.pop()]
				else:
					r += ['']
			#dPY("6. evaluate: r is ", r, lvl=100)
				#r list has at this point 4 null strings for the value
				#an error string and a warning string if applicable

			#if ** operator has been used, replace the chr(127) substituted earlier for it
			es = es.replace(chr(127), '**')
			#dPY( "6.1 evaluate: es is now ", es)
			#have one additional null command

		#if length of r is 3, there are no warnings or errors
		#if length of r is 5, there can be an error msg in r[3] and a warning msg in r[4]
		#if r[3] is '', print r[0:3] as the answer and if r[4] is '', print r[4] as warning
		#print("ev: 7. evaluate: r is ", r)
		
		self.enn = ''
		self.wnn = []
		
		return r

	def prnv (self, var='ans', vi = False):
		#print Vars

		value =  self.stv[var]
		width =  self.stw[var]
		base =  self.stb[var]

		if type(value) != mpap:
			#for bool etc.
			return [str(value), '', '']

		expo = value.Exponent

		if APBF_LAST_OP_DIGITS_LEN > 10000:
			#dPY ("prnv: returning ZXY ... value is ", value)
			return [value.flexstr(sci=False), '', '']

		#vi = vi or len(str(value.Mantissa)) == (expo + 1) 
		lvi = value.getMantissaLength()
		vi = vi or (lvi  == (expo + 1))
		#right term to ensure that Mantissa has all significant 
		#digits, i.e., is not rounded off to lower precision

		#dPY (lvl=10)
		#dPY ("prnv: entered: value is ", value.__repr__() , " of type ", type(value), " of base ", base,
		#	" is integer=", vi, lvl=11)
		#dPY ("prnv: entered: of type ", type(value), " of base ", base,
		#	" is integer=", vi, lvl=10)

		if value.isComplex():
			if self.sci == False and self.rnd <= 33:
				#sci 
				#dPY ("prnv: returning B ... value is ", value)
				return [value.flexstr(sci=False), '', '']
			else:
				#dPY ("prnv: returning C ... value is ", value)
				return [value.flexstr(sci=True), '', '']

		#lvi = len(str(value.Mantissa))

		#dPY ("prnv: intermediate ... value is ", value, lvl=100)
		#dPY('')
		#dPY("---------VexMicro---------- value is ", value.__repr__(), " base is ", base, " valIsInt is ", vi, lvl=10)
		#dPY('')
		em = 0
		#dPY("---------VexMicro---------- base is ", base, " valIsInt is ", vi, lvl=100)
		if base == 'd' or base == 'L':
			if self.eng == True:
				if lvi <= 15 and lvi > 12:
					value = [str(value / 1099511627776), '', '']
					em = 4
				elif lvi <= 12 and lvi > 9:
					value = [str(value / 1073741824), '', '']
					em = 3
				elif lvi <= 9 and lvi > 6:
					value = [str(value / 1048576), '', '']
					em = 2
				elif lvi <= 6 and lvi > 3:
					#dPY ("lvi is ", lvi)
					value = [str(value / 1024), '', '']
					em = 1
				else:
					value = [str(value), '', '']
				#dPY ("7. ---------VexMicro---------- prnv: value is ", value, lvl=100)
			else:
				#dPY ("4. ---------VexMicro---------- prnv: value is ", value, "vi is ", vi, "self.sci is ", self.sci, lvl=100)
				if vi:
					value = [str(int(value)), '', '']
				else:
					vm, ve = value.sci()
					if ve != 0:
						if self.rnd > 33 or ve > self.rnd:
							#value = vm + chr(251) + str(ve)
							value = [vm, ' ' + chr(0x2219) + ' 10', str(ve)]
						elif self.sci == True:
							#value = vm + chr(251) + str(ve)
							value = [vm, ' ' + chr(0x2219) + ' 10', str(ve)]
						else:
							value = [value.flexstr(sci=False), '', '']
					else:
						value = [vm, '', '']
					#dPY ("5. ---------VexMicro---------- prnv: vm is ", vm, "vi is ", vi, "value is ", value, lvl=100)

			if expo > 3 and vi == False:
				#numbers with long fractional parts are returned
				#dPY ("prnv: returning 1 ... value is ", value, lvl=100)
				return value
		else:
			#dPY("6.Z1: value is ", value, " vi = ", vi, " base = ", base, lvl=100)
			s = str(self.dec2xxx(int(value), dec2what=base))
			#print ("6.ZZ1: -- width = ", width, " -- len(s) = ", len(s), " -- vi = ", vi, " -- self.slz = ", self.slz, " string s = ", s)
			if vi == True or (base == 'h' or base == 'b'):
				if width > 0 and self.slz == False:
					if base == 'h':
						diff = int(width / 4) - len(s)
						if width % 4 != 0:
							diff += 1
					else:
						diff = int(width) - len(s)
					#width is greater than length of integer
					#pad with leading zeros
					s = '0'*diff + s
					#dPY("6.Z1.2: diff is ", diff, lvl=100)
			value = [s, '', '']


		#dPY("6.Z2: width is ", width)

		#dPY ("2. base is ", base)
		#dPY("AA: value  is ", value)

		#dPY("calling prettyPrint: easyprint is ", self.ep)
		#dPY("QW: value  is ", value)
		isNeg = False
		if (self.ep or self.ins or self.wns) == True:
			if value[0].find('-') == 0:
				value[0] = value[0][1:]
				isNeg = True
			dotMatch =  value[0].find ('.')
			if dotMatch == -1:
				dotMatch = len(value[0])
			#do PP for integer part but not fractional part
			value[0] = self.prettyPrint (value[0][:dotMatch], base, self.ep,\
					self.ins,\
					self.wns) + value[0][dotMatch:]
			if isNeg == True:
				value[0] = '-' + value[0]
			#dPY ("2. value[0] is ", value[0])

		if value[0] == '':
			value[0] = '0'

		#print ("vi is ", vi)
		if vi or (base == 'h' or base == 'b'):
			if self.dstd == False or base != 'd' or width != 0:
				if width > 0:
					value[0] = str(width) + "'" + base + value[0]
				elif base != 'n' and base != 'L' and base != 'I':
					value[0] = "'" + base + value[0]
		#print ("width is ", width)
			
		if self.eng == True:
			value[0] += " kMGT"[em]

		#dPY ("prnv: returning ... value is ", value, lvl=100)
		return value


	def do(self, l):
		try:
			if len (l) > 1:
				raise ValueError
			lc = int(l[0])
		except:
			self.sher ("Error: illegal loop count for do statement")
			return mpap(0)

		inpss = self.insp - 1
		if lc > 0:
			evs =  self.inps[inpss:]
			#dPY ("---- evalStr is ", evalStr)

			#remove the comments
			evsls = evs.split('#')

			#get all commands in the same line
			evsl = evsls[0].split(';')

			value = '0'
			for i in range (lc):
				#dPY("do: -------- i is ", i)
				#dPY ("Continuing with evalStr ", evalStr)
				
				for s in evsl:
					value = self.ev(s.strip())
				#dPY("do: -------- expression returned value ", value)
		else:
			#do <expression> -- implicit loop count of 1
			#dPY("do: -------- doing vanilla expression")
			value = self.ev(self.inps[inpss:])

		return value


