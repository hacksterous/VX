#!/usr/bin/python

#(c) Anirban Banerjee 2018
#License: GPL version 3 (version three) or any later version
#https://www.gnu.org/licenses/gpl.html
#(c) Anirban Banerjee 2015-2019
#License: GNU GPL Version 2

#<genericspecifier> = TICK[b|h|d]
#<morecommand> = [<expression>]*
#<command> = [<command><EQUALS><morecommand>]*
#<expression> = [0-9]*<genericspecifier><mathexpression>
#
#<mathexpression> = [PLUS|MINUS]? <term> [PLUS|MINUS term]*
#<term> =factor [[STARSTAR|STAR|FSLASH]factor]*
#<factor> =LPAREN expr RPAREN | IDENT | REALNUMBER | VARNAME EQUALS <mathexpression>
#IDENT::=VARNAME | FUNCTION
#FUNCTION::=[sin|cos|tan|exp|ln|log]LPAREN<mathexpression>RPAREN
#VARNAME::=letter [letter|digit|UNDERSCORE]*
#REALNUMBER::= [digit]*[DECPOINT][digit]*

#=======================================#
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QFileDialog, QActionGroup, QMessageBox, QFontDialog
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFontMetrics, QFont, QFontDatabase, QColor
import VXUI
from VexMicroPC import VexMicroPC
import argparse
import os
import sys
import re
import time
import traceback

class VXCoreError (Exception):
	pass

def handleGUIException(excType, excValue, excTraceback):
	try:
		logError = False
		with open ('VX.log', 'w+') as f:
			f.write (''.join(traceback.format_exception(excType, excValue, excTraceback)))
			f.write('=========================================\n')
			f.close()
		if self.fullLockFileName != '':
			os.remove(self.fullLockFileName)
	except:
		logError = True

	errMsg = 'Error: Fatal exception, VX will close.'
	if logError == True:
		errMsg += '\nError log file could not be created.'
	else:
		errMsg += '\nPlease send VXX.log to <anirbax@gmail.com>.'
	print (errMsg+''.join(traceback.format_exception(excType, excValue, excTraceback)))
	if logError == False:
		sys.exit(1)

sys.excepthook = handleGUIException

def chop (string, length):
	choppedList = [string[i:i+length] for i in range(0, len(string), length)]
	return choppedList

def dPY(*args, lvl=10):
	if lvl < 11:
		return
	s = ''
	for arg in args:
		s = s + ' ' + str(arg)
	print(s)

HELP = """
 :exit, :quit - exits VX.
 :help, ?, :? - prints this help.
 : - repeats previous command.
 :<command-number> - repeats command number <command-number>.
 :set <command> 
 :unset <command>
	where <command> can be
		sci: For numbers less than 1e24, use scientific notation for display
		eng: For numbers less than 1e15, use engineering notation for display [M is 1024*1024 = 1048576, etc.]
		fhp: Factorial operator '!' has higher precedence than multiply/divide.
		adw: Automatically adjust width when width is unspecified
		dstd: suppress Verilog 'd for decimal numbers
		bfa: base is assigned from right-hand side assignment
		wfa: width of variable is assigned from right-hand side assignment
		slz: suppress leading zeros
		showw: show warnings
		wns: western numeral separator
		ins: Indian numeral separator
		vns: Verilog-style underscore digit separator
		nns: no numerical separator
	
 :do <loop times> <multi-cmd> - repeats command that follows <loop times>.
	 <multi-cmd> have multiple commands separated by ';'s
 :ls - lists all variables.
 ans - prints last result.
 :del - deletes variable or list of variables (separated by comma or space).
 :delall - deletes all user variables.
 :cls - clears screen.
 :clear - clears screen.
 :reset - clears screen and resets command history.
 :runtime - prints time take to execute the last command in seconds.
 :r, :run, :exec, :e <file name> - runs command transcript from file
 :p, :prec, :precision <integer> -- set decimal precision to <integer>
 :w, :write, :s, :save - writes out command transcript to file (does not overwrite existing file)
 :w!, :write!, :s!, :save! - writes out command transcript to file (overwrites existing file)

 Comment
 -------
 The '#' character is used as a comment. Any input following
 the comment character is ignored.

 Values
 ------
 Widths are specified using Verilog-like syntax
 that also specify the base of the number. Examples:
 8'b101
 32'h5a_1234

 Base Conversion
 ---------------
 To hexadecimal:
 x= 32'd1234 #Assign as decimal
 x= 32'h(x) #Convert to 32-bit hexadecimal

 Verilog Catenation
 ------------------
 {8{1'b1}} 
	results in 8'b1111_1111

 8{{1'b1}} returns an error.
	'Error: parser expected end of stream.'

 {8{1'b10}} 
 returns 
	8'b0000_0000
	Warning: Value 'b 0010  will be truncated to  1  bits.

 {8{2'b10}}
 returns
	16'b1010_1010_1010_1010

 Assignment
 ----------
 Any alphanumeric character and the underscore, not starting with a number
 can be a variable name. Assignment examples:

 x = 10
 _ = 10'b1		#variable _ is 10-bits wide (taken from assignment)
 zz = 32'hab	#zz is 32-bits wide (taken from assignment)
 qq:8 = 32'h6	#qq is declared to be of width 8 which will override the assignment
 qw = {1'd1, {8{1'b1}}} #qw is 9'd511
 we = {1, {8{1'b1}}}
 {we:4, wy:5} = {1'b0, {8{1'b1}}} #we  is 4'b111 and wy is 5'b11111

 Complex numbers
 ---------------
	A + [B] means
	A + im * B where
	im is the square root of -1.
	Functions that suppot complex number inputs are:
		sqrt
		pow
		exp
		log
		sin
		cos
		tan
		sinh
		cosh
		tanh
		asin
		acos
		atan

 Modular Arithmetic
 ------------------
	Modular exponentiation example
		r = random(256) #r is a 2048-bit random number
		M = nxp(r) #next prime number
		power = 100000
		3**%[M] power  #3 to the power of 'power' modulus M
		3**%[nxpa](nxpa-1) # equals 1 -- Fermat's Little Theorem
		nnxpa = nxp(nxpa)
		3**%[nnxpa](nnxpa-1) #equals 1 for any prime nnxpa

	Modular inverse example
		r = random(256) #r is a 256-byte (2048-bit) random number
		M = nxp(r) #next prime number
		value = 100000
		1/%[M] value  #inverse of 'value' modulus M
		5/%[M] value  #inverse of 'value' modulus M multiplied by 5, and the product modulus M

 Exponent shorthands -
		'f' - multiplier of 1e-15
		'p' - multiplier of 1e-12
		'n' - multiplier of 1e-9
		'u' - multiplier of 1e-6
		'm' - multiplier of 1e-3
		'k' - 1 thousand, multiplier of 1,000
		'mi' - 1 million, multiplier of 1,000,000
		'B', 'bi' - 1 billion, multiplier of 1,000,000,000
		'l, 'L' - 1 lakh, multiplier of 1,00,000
		'c, 'C' - 1 crore, multiplier of 100,00,000
		'K' - 1 kilo, multiplier of 1024
		'M' - 1 mega, multiplier of 1048576
		'G' - 1 giga, multiplier of 1073741824
		'T' - 1 tera, multiplier of 1099511627776

Parsing is left-to-right, with 
		A + B + C + D 
being equivalent to 
		A + (B + (C + D))
and
	ans ++ 1
is equivalent to
	ans + (+1)
Also,
	ans --- 1
is equivalent to
	ans -(-(-1))

Examples:
#1>	111[19:0] * 3 * x[9:0] = 1 
is equivalent to 
#1>	111[19:0] * 3 * (x[9:0] = 1)
the assignment operation within parentheses returns
a value of 1, the width of variable 'x' having been
updated to 10 and 'x' assigned a value of 1.
The expression is equivalent to these two commands:
#1>	x[9:0] = 1
#2>	111 * 3 * 1


Comparison:
#> 2.99 > 2.999
returns
	False

False has a value of 0 in numerical expressions and True
has a value of 1.

#> 2.99 > 2.999+1
is same as
#> 2.99 > (2.999+1)
and returns
	False
#> (2.99 > 2.999)+1
gives
	1

Slicing numbers into bit vectors:
#> ((int(pi)*'h11)[3:0])[1:0]
gives
	3 """

class Error(Exception):
	pass

class DebugError (Error):
	pass

class qVX(QtWidgets.QMainWindow, VXUI.Ui_VXCalculator):
 
	def __init__(self, parent=None):

		super(qVX, self).__init__(parent)
		self.setupUi(self)
		self.lightTheme = True

		self.promptColorLight = 'blue'
		self.promptColorDark = 'white'
		self.textInfoColorLight = '#1098ea'  #(16, 152, 234)
		self.textInfoColorDark = 'yellow' #(216, 252, 34)
		self.textNormalColorLight = 'black' #(0, 0, 0)
		self.textNormalColorDark = 'white' #(255, 255, 255)
		self.textErrorColorLight = 'red' #(255, 0, 0)
		self.textErrorColorDark = '#ff6400' #(255, 100, 0)

		self.expandFontNamesList = []
		self.fullLockFileName = ''

		#dPY ("VXFile is ", self.VXFile)

		self.metaCmdDescription = {
				'sci': 'For numbers less than 1e24, use scientific notation for display',
				'eng': 'For numbers less than 1e15, use engineering notation for display',
				'fhp': "Factorial operator '!' has higher precedence than multiply/divide.",
				'adw': "Automatically adjust width when width is unspecified",
				'dstd': "suppress Verilog 'd for decimal numbers",
				'bfa': 'base is assigned from right-hand side assignment',
				'wfa': 'width of variable is assigned from right-hand side assignment',
				'slz': 'suppress leading zeros',
				'showw': 'show warnings',
				'wns': 'western numeral separator',
				'ins': 'Indian numeral separator',
				'vns': 'Verilog-style underscore digit separator',
				'nns': 'no numerical separator',
				#'': '',
				#'': '',

				}

		self.allCommands = ':fs:fsize:del:ls:set:defw:unset:cls:reset:print:help:do:delall:exec:run:history:font:quit:runtime:precision:save:w!:write!:save!'

		self.completionEntryListOrig = [
			'pi',
			'e',
			'sun',
			'day',
			'today',
			'tithi',
			'ltithi',
			':ls',
			':set',
			':defw',
			':unset',
			':cls',
			':reset',
			':print',
			':help',
			':do',
			':del',
			':delall',
			':exec',
			':run',
			':history',
			':font',
			':quit',
			':runtime',
			':precision',
			':save',
			':w!',
			':write'
			]

		self.autoExpandContext = 'NONE'

		self.listOfMetaCommands = [':unset', ':reset', ':set', ':f', ':font', ':exit', ':q' , ':quit', ':help', ':run', ':r', ':s', ':write', ':exec', ':save',
				'save!', ':s!', ':write!', ':w!', ':exec', ':save', ':precision', ':prec', ':p',
				':ls', ':del', ':delall', ':cls', ':clear', ':runtime', '?', ':?']

		self.mouseLeftClickCount = 0

		self.unEnteredCommand = ''
		self.printMaxWidth = 90
		self.currentLineNumber = 0
		self.mouseClicked = False
		self.mouseClickLineNumber = 0
		self.promptStr = "#1> "
		# A "-1" in the size parameter instructs wxWidgets to use the default size.
		# In this case, we select 200px width and the default height.

		self.dirName = ''
		self.fileName = ''
		self.inputStr = ''

		self.VX = VexMicroPC()
		self.timer = QTimer()
		self.setInitialFont()

		if os.path.isfile('.vex'):
			#self.inputStr = ":run .vex #startup file .vex found\n"
			#self.editorText.insertPlainText (self.inputStr)
			self.executeFile('.vex')
			self.writePrompt()
			self.VX.ca = []
			self.indexHistory = 0 #no valid command
			self.VX.ra = []
			self.VX.stv ['ans'] = '0'
		else:
			#when there is no startup script, start with a prompt
			self.writePrompt()

		self.menuClear.triggered.connect(self.doClear)
		self.menuOpen.triggered.connect(self.fileOpen)
		self.menuSave.triggered.connect(self.fileSaveAsGUI)
		self.menuExit.triggered.connect(self.fileOpen) #FIXME
		self.menuEnableNewVarRefError.triggered.connect(self.enableNewVarRefErrorHandler)
		self.menuSuppressTickD.triggered.connect(self.suppressTickDHandler)
		self.menuSuppressZeros.triggered.connect(self.suppressLeadingZeros)
		self.menuTakeBaseFromAssignment.triggered.connect(self.takeBaseFromAssignment)
		self.menuTakeWidthFromAssignment.triggered.connect(self.takeWidthFromAssignment)
		self.menuNoEasyPrinting.triggered.connect(self.noEasyPrinting)
		self.menuEasyPrinting.triggered.connect(self.easyPrinting)
		self.menuIndianNumSeparator.triggered.connect(self.indianNumSeparator)
		self.menuWesternNumSeparator.triggered.connect(self.westernNumSeparator)
		self.menuShowWarnings.triggered.connect(self.showWarnings)
		self.menuDarkTheme.triggered.connect(self.showWarnings) #FIXME
		self.menuFont.triggered.connect(self.fontSelect)
		self.menuHelp.triggered.connect(self.showHelp)
		self.menuAbout.triggered.connect(self.helpAbout)
		self.editorText.installEventFilter(self)
		self.editorText.viewport().installEventFilter(self)
		self.editorText.setFocus()

	def setTitleArgs (self, title='', argTuple=()):
		self.title = title
		self.VXFile = argTuple

		#dPY ("INIT: self.VXFile is ...", self.VXFile)
		if self.VXFile != '':
			self.dirName = os.path.dirname(self.VXFile)
			fileName = os.path.basename(self.VXFile)
			fullFileName = os.path.join(dirName, fileName)
			#dPY ("MAIN: fullFileName is", fullFileName, "type is ", type(fullFileName))
			self.fullLockFileName = fullFileName+'.lock'
			if os.path.isfile(self.fullLockFileName):
				if os.name == 'nt':
					self.fullLockFileName = self.fullLockFileName.lower()
				os.remove(self.fullLockFileName)

			self.inputStr = ":run " + str(fullFileName).strip()
			self.editorText.insertPlainText (self.inputStr)
			self.doInputCommand()

		self.completionEntryList = self.completionEntryListOrig + list(self.VX.stv.keys())

	def strpart(self, string, length):
		return (string[0+i:length+i] for i in range(0, len(string), length))

	def setTextColor (self, which, attr=None, attrColor='white'):
		pass

	def writeInfo (self, text, what=3):
		if what == 0: #info
			self.editorText.setTextColor (QColor(self.getThemeColors(self.lightTheme)[2]))
		elif what == 1: #error
			self.editorText.setTextColor (QColor(self.getThemeColors(self.lightTheme)[1]))
		elif what == 2: #warning
			self.editorText.setTextColor (QColor('orange'))
		#default is normal -- 3
		self.editorText.insertPlainText (text)
		self.editorText.setTextColor (QColor(self.getThemeColors(self.lightTheme)[0]))

	def writeError (self, text):
		self.writeInfo (text, 1)

	def writeWarning (self, text):
		self.writeInfo (text, 2)

	def writeValue (self, man, exp):
		self.editorText.insertPlainText (man)
		self.editorText.insertPlainText (exp + '\n')

	def getWordToLeft (self):
		opsList = ['+', '/', '*', '-', '&', '|', '^', '~', '!', '%', ')', '(']
		currentPos = self.editorText.GetInsertionPoint()
		currChar = self.editorText.GetRange (currentPos-1, currentPos)
		if currChar != '':
			ordCurrChar = ord(currChar)
		else:
			ordCurrChar = 0
		delimiterToLeft = (ordCurrChar <= 32) or currChar in opsList
		lineNumber = self.editorText.PositionToXY(currentPos)[2]
		posS = self.editorText.XYToPosition (len(self.promptStr), lineNumber)
		lineString = self.editorText.GetRange (posS, currentPos)
		#dPY ("==== getWordToLeft: lineString is ", lineString, "delimiterToLeft is ", delimiterToLeft)

		currentLineStrArray = []
		currentLineStrWordArray = lineString.split()
		for clsw in currentLineStrWordArray:
			for o in opsList:
				if clsw.find(o) >= 0:
					#exception in the case of overwrite commands!
					if clsw.find (':w!') == -1 and clsw.find (':s!') == -1 and\
							clsw.find (':write!') == -1 and clsw.find (':save!') == -1:
						currentLineStrArray += clsw.split(o)

		if currentLineStrArray == []:
			currentLineStrArray = lineString.split()
		
		#dPY ("==== getWordToLeft: currentLineStrArray is ", currentLineStrArray)
		#return last element
		popped = ''
		poppedFront = ''
		if len(currentLineStrArray) > 0:
			popped = currentLineStrArray.pop()
			poppedFront = currentLineStrArray.pop()

		return (poppedFront, popped, delimiterToLeft, currentPos)

	def handleTabExpand (self, cursor):
		text = cursor.block().text()
		currentPos = self.editorText.GetInsertionPoint()
		lineNumber = self.editorText.PositionToXY(currentPos)[2]
		posS = self.editorText.XYToPosition (len(self.promptStr), lineNumber)
		lineString = self.editorText.GetRange (posS, currentPos)

		earlierWordToLeft, wordToLeft, delimiterToLeft, currentPos = self.getWordToLeft()
		#dPY ("delimiterToLeft is ", delimiterToLeft, "word to left is ", wordToLeft, "earlier word to left is ", earlierWordToLeft)

		if earlierWordToLeft == ":set" or earlierWordToLeft == ":unset":
			self.autoExpandContext = 'SET_UNSET'
		elif earlierWordToLeft == ":run" or earlierWordToLeft == ":exec" or\
				earlierWordToLeft == ":write!" or earlierWordToLeft == ":save!" or\
				wordToLeft == ":s!" or earlierWordToLeft == ":w!":
			self.autoExpandContext = 'RUN_FILE'
		elif earlierWordToLeft == ":font" or earlierWordToLeft == ":f":
			#if we have got a randomized font list, no need to randomize again
			if self.autoExpandContext != 'FONT':
				self.expandFontNamesList = self.getShortFontNameList()
			self.autoExpandContext = 'FONT'

		if delimiterToLeft == True:
			if wordToLeft == ":set" or wordToLeft == ":unset":
				self.autoExpandContext = 'SET_UNSET'
			elif wordToLeft == ":run" or wordToLeft == ":w!" or\
					wordToLeft == ":s!" or wordToLeft == ":w!" or\
					wordToLeft == ":save!" or earlierWordToLeft == ":w!" or\
					wordToLeft == ":r" or earlierWordToLeft == ":write!" or\
					wordToLeft == ":exec" or earlierWordToLeft == ":save!":
				self.autoExpandContext = 'RUN_FILE'
			elif wordToLeft == ":font" or wordToLeft == ":f" or\
					earlierWordToLeft == ":font" or earlierWordToLeft == ":f":
				#if we have got a randomized font list, no need to randomize again
				if self.autoExpandContext != 'FONT':
					self.expandFontNamesList = self.getShortFontNameList()
				self.autoExpandContext = 'FONT'
			else:
				self.autoExpandContext = 'NONE'
		else:
			if earlierWordToLeft == ":r" or earlierWordToLeft == ":exec" or\
					wordToLeft == ":s!" or earlierWordToLeft == ":w!" or\
					wordToLeft == ":exec" or earlierWordToLeft == ":save!" or\
					earlierWordToLeft == ":run":
				self.autoExpandContext = 'RUN_FILE'
			elif earlierWordToLeft == ":font" or earlierWordToLeft == ":f":
				self.autoExpandContext = 'FONT'
			elif earlierWordToLeft == ":set" or earlierWordToLeft == ":unset":
				self.expandFontNamesList = self.getShortFontNameList()
				self.autoExpandContext = 'SET_UNSET'
			else:
				self.autoExpandContext = 'NONE'
		#endif

		#dPY ("autoExpandContext is == ", self.autoExpandContext)
		if self.autoExpandContext == 'SET_UNSET':
			myList = [
				'sci',
				'eng',
				'fhp',
				'adw',
				'dstd',
				'bfa', 
				'wfa', 
				'slz', 
				'showw',
				'wns', 
				'ins', 
				'vns', 
				'nns']
		elif self.autoExpandContext == 'FONT':
			myList = self.expandFontNamesList
		elif self.autoExpandContext == 'RUN_FILE':
			#dPY ("\n-----------------autoExpandContext is ", self.autoExpandContext, "wordToLeft is ", wordToLeft, "earlierWordToLeft is ", earlierWordToLeft)
			#myList = os.listdir ('.') 
			if delimiterToLeft == True:
				myList = [f for f in os.listdir('.') if re.match(r'.*\.vex$', f)]
			else:
				dirname = os.path.expanduser(os.path.dirname (wordToLeft))
				m = re.match(r'.*\/\/$', dirname)
				#dPY ("dirname is ", dirname)
				try:
					myList = [dirname + '/' + os.path.basename(f) for f in os.listdir(dirname) if re.match(r'.*\.vex$', f)]
				except FileNotFoundError:
					if os.path.exists (dirname):
						myList = []
					else:
						myList = [f for f in os.listdir('.') if re.match(r'.*\.vex$', f)]
			#dPY ("delimiterToLeft is ", delimiterToLeft)
		else:
			myList = self.completionEntryList 

		if delimiterToLeft == False:
			#dPY ("delimiterToLeft is FALSE and wordToLeft is ", wordToLeft)
			tempList = []
			for e in myList:
				if e.find (wordToLeft) == 0: #word in list starts with wordToLeft
					tempList.append (e)
			myList = tempList

		completionString = ''
		#dPY ("myList is ", myList)
		self.editorText.insertPlainText('\n')
		if len (myList) > 1:
			i = 0
			for e in myList:
				if self.autoExpandContext == 'SET_UNSET':
					self.setTextColor('setunset')
				elif self.autoExpandContext == 'FONT':
					self.setTextColor('font')
				elif self.autoExpandContext == 'RUN_FILE':
					self.setTextColor('runfile')
				else:
					self.setTextColor('tabexpdefault')

				if i % 10 == 9:
					self.editorText.insertPlainText(e + '\n')
				else:
					self.editorText.insertPlainText(e + '  ')
				i += 1
			if i % 10 != 0:
				self.editorText.insertPlainText('\n')
		elif len(myList) > 0:
			loneWord = myList[0]
			completionString = loneWord[len(wordToLeft):] + ' '

		#dPY ("completionString is ", completionString)

		self.setTextColor('normal')

		self.currentLineNumber = self.editorText.PositionToXY(self.editorText.GetLastPosition())[2]
		#dPY ("handleTabExpand ------ at end self.currentLineNumber is ", self.currentLineNumber)
		self.writePrompt()
		if lineString != '':
			self.editorText.insertPlainText(lineString)
			if completionString != '':
				#dPY ("===================== completionString is ", completionString)
				self.editorText.insertPlainText(completionString)

	def handleContextPopupMenuClick (self, event=None):
		idSelected = event.GetId()
		obj = event.GetEventObject()
		label = obj.GetLabel(idSelected)
		#dPY ("handleContextPopupMenuClick -------- with label=", label)
		self.editorText.insertPlainText(label)

	def enableNewVarRefErrorHandler (self, event):
		self.VX.envre = self.menuEnableNewVarRefError.isChecked()

	def suppressTickDHandler (self, event):
		self.VX.dstd = self.menuSuppressTickD.isChecked()

	def suppressLeadingZeros (self, event):
		self.VX.slz = self.menuSuppressZeros.isChecked()

	def takeBaseFromAssignment (self, event):
		self.VX.tba = self.menuTakeBaseFromAssignment.isChecked()

	def takeWidthFromAssignment (self, event):
		self.VX.twa = self.menuTakeWidthFromAssignment.isChecked()

	def easyPrinting (self, event):
		self.VX.ep = True
		self.VX.ins = False
		self.VX.wns = False
		self.menuNoEasyPrinting.setChecked(False)
		self.menuEasyPrinting.setChecked(True)
		self.menuIndianNumSeparator.setChecked(False)
		self.menuWesternNumSeparator.setChecked(False)

	def noEasyPrinting (self, event):
		self.VX.ep = False
		self.VX.ins = False
		self.VX.wns = False
		self.menuNoEasyPrinting.setChecked(True)
		self.menuEasyPrinting.setChecked(False)
		self.menuIndianNumSeparator.setChecked(False)
		self.menuWesternNumSeparator.setChecked(False)

	def indianNumSeparator (self, event):
		self.VX.sci = False
		self.VX.eng = False

		self.VX.ep = False
		self.VX.ins = True
		self.VX.wns = False
		self.menuSuppressTickD.setChecked(True)
		self.suppressTickDHandler(None)
		self.menuNoEasyPrinting.setChecked(False)
		self.menuEasyPrinting.setChecked(False)
		self.menuIndianNumSeparator.setChecked(True)
		self.menuWesternNumSeparator.setChecked(False)

	def westernNumSeparator (self, event):
		self.VX.sci = False
		self.VX.eng = False
		self.VX.ep = False
		self.VX.ins = False
		self.VX.wns = True
		self.menuSuppressTickD.setChecked(True)
		self.suppressTickDHandler(None)
		self.menuNoEasyPrinting.setChecked(False)
		self.menuEasyPrinting.setChecked(False)
		self.menuIndianNumSeparator.setChecked(False)
		self.menuWesternNumSeparator.setChecked(True)

	def VXCommandHandler (self, vexCmd='', truth='True'):
		if vexCmd in self.metaCmdDescription.keys() and vexCmd != '':
			if vexCmd == 'fhp':
				self.VX.fhhp = truth
			elif vexCmd == 'sci':
				self.VX.sci = truth
				self.bottomCheckBoxSCI.SetValue(truth)
				if self.VX.eng == True and truth == True:
					self.VX.eng = False
			elif vexCmd == 'eng':
				if self.VX.sci == True and truth == True:
					self.bottomCheckBoxSCI.SetValue(False)
					self.VX.sci = False
				self.VX.eng = truth
			elif vexCmd == 'adw':
				self.VX.aaw = truth
			elif vexCmd == 'dstd':
				self.VX.dstd = truth
				self.menuSuppressTickD.setChecked(truth)
			elif vexCmd == 'bfa':
				self.VX.tba = truth
				self.menuTakeBaseFromAssignment.setChecked(truth)
			elif vexCmd == 'wfa':
				self.VX.twa = truth
				self.menuTakeWidthFromAssignment.setChecked(truth)
			elif vexCmd == 'slz':
				self.VX.slz = truth
				self.menuSuppressZeros.setChecked(truth)
			elif vexCmd == 'showw':
				self.VX.showws = truth
				self.menuShowWarnings.setChecked(truth)
			elif vexCmd == 'wns':
				#dPY ("truth is ", truth)
				self.VX.ep = not truth
				self.VX.ins = not truth
				self.VX.wns = truth
				self.menuSuppressTickD.setChecked(truth)
				self.menuEasyPrinting.setChecked(not truth)
				self.menuIndianNumSeparator.setChecked(not truth)
				self.menuWesternNumSeparator.setChecked(truth)
				self.menuNoEasyPrinting.setChecked(not truth)
			elif vexCmd == 'ins':
				self.VX.ep = not truth
				self.VX.ins = truth
				self.VX.wns = not truth
				self.menuSuppressTickD.setChecked(truth)
				self.menuNoEasyPrinting.setChecked(not truth)
				self.menuIndianNumSeparator.setChecked(truth)
				self.menuWesternNumSeparator.setChecked(not truth)
				self.menuEasyPrinting.setChecked(not truth)
			elif vexCmd == 'vns':
				self.VX.ep = truth
				self.VX.wns = not truth
				self.VX.ins = not truth
				self.menuEasyPrinting.setChecked(truth)
				self.menuIndianNumSeparator.setChecked(not truth)
				self.menuWesternNumSeparator.setChecked(not truth)
				self.menuNoEasyPrinting.setChecked(not truth)
			elif vexCmd == 'nns':
				self.VX.wns = not truth
				self.VX.ins = not truth
				self.VX.ep = not truth
				self.menuNoEasyPrinting.setChecked(truth)
				self.menuIndianNumSeparator.setChecked(not truth)
				self.menuWesternNumSeparator.setChecked(not truth)
				self.menuEasyPrinting.setChecked(not truth)
			self.writeInfo (f'Info: parameter \'{vexCmd}\' ({self.metaCmdDescription[vexCmd]}) has been set to {truth}.\n', what=0)
			return True
		elif vexCmd == '':
			self.setTextColor('setunset')
			self.editorText.insertPlainText (f" sci  : (For numbers less than 1e24, use scientific notation for display) is {self.VX.sci}.\n")
			self.editorText.insertPlainText (f" eng  : (For numbers less than 1e15, use engineering notation for display) is {self.VX.eng}.\n")
			self.editorText.insertPlainText (f" fhp  : (Factorial operator '!' has higher precedence than multiply/divide) is {self.VX.fhhp}.\n")
			self.editorText.insertPlainText (f" adw  : (Automatically adjust width when width is unspecified) is {self.VX.aaw}.\n")
			self.editorText.insertPlainText (f" dstd : (For decimal suppress 'd) is {self.VX.dstd}.\n")
			self.editorText.insertPlainText (f" bfa  : (Variable base is taken from assignment RHS) is {self.VX.tba}.\n")
			self.editorText.insertPlainText (f" wfa  : (Variable width is taken from assignment RHS) is {self.VX.twa}.\n")
			self.editorText.insertPlainText (f" slz  : (Suppress leading zeroes) is {self.VX.slz}.\n")
			self.editorText.insertPlainText (f" showw: (Show warnings) is {self.VX.showws}.\n")
			self.editorText.insertPlainText (f" wns  : (Comma-separated groups of three digits) is {self.VX.wns}.\n")
			self.editorText.insertPlainText (f" ins  : (Comma-separated groups of two or three digits) is {self.VX.ins}.\n")
			self.editorText.insertPlainText (f" vns  : (Underscore-separated groups of 4 digits, bits or hexits) is {self.VX.ep}.\n")
			self.editorText.insertPlainText (f" nns  : (No separator used between digits) is {not self.VX.ep and not self.VX.ins and not self.VX.wns}.\n")
			return False
		else:
			self.writeError (f'Error: No such parameter: \'{vexCmd}\'.\n')
			return False

	def showWarnings (self, event):
		self.VX.showWarnings = self.menuShowWarnings.isChecked()

	def getThemeColors (self, lightTheme=True):
		return [self.textNormalColorLight, self.textErrorColorLight, self.textInfoColorLight]

	def getPromptColor (self, lightTheme=True):
		return self.promptColorLight

	def writePrompt (self):
		lca = len(self.VX.ca)
		self.promptStr = '#' + str(lca+1) + '>'
		
		self.font.setBold(True)
		self.editorText.setTextColor (QColor('blue'))
		self.editorText.setCurrentFont (self.font)
		self.editorText.insertPlainText(self.promptStr)
		self.font.setBold(False)
		self.editorText.setTextColor (QColor(self.getThemeColors(self.lightTheme)[0]))
		self.editorText.setCurrentFont (self.font)
		self.editorText.insertPlainText(' ')
		self.editorText.moveCursor(QtGui.QTextCursor.End)  #end of line
		

	def clearSelection (self):
		cursor = self.editorText.textCursor()
		if cursor.hasSelection():
			cursor.clearSelection()
			cursor.end()
			self.editorText.SetInsertionPoint(self.editorText.GetLastPosition())

	def clearLine (self, cursor):
		cursor.clearSelection()
		text = cursor.block().text()
		length = len(text) - len(self.promptStr) - 1
		
		cursor.movePosition(QtGui.QTextCursor.End, QtGui.QTextCursor.MoveAnchor)
		cursor.movePosition(QtGui.QTextCursor.Left, QtGui.QTextCursor.KeepAnchor, length)
		cursor.selectedText()
		cursor.removeSelectedText()
		self.editorText.setTextCursor(cursor)

	def fontSelect (self, event):
		dialog = QFontDialog()
		dialog.setCurrentFont (self.font)
		font, ok = dialog.getFont()
		if ok:
			self.font = font
			self.fontName = self.font.family()
			self.editorText.setFont(self.font)
			return True
		else:
			return False

	def getMaxLineChars (self):
		#chars = self.editorText.document().textWidth() // QFontMetrics(self.font).maxWidth()
		#print ("-- # self.editorText.document().textWidth() ", self.editorText.document().textWidth())
		#print ("QFontMetrics returned ", QFontMetrics(self.font).maxWidth())
		
		#if chars < 30:
		#	chars = 30
		#FIXME
		return 80

	def setFontSize (self, fontSize=0):
		try:
			fs = int(fontSize)
		except:
			return False
		if fs < 7:
			return False
		self.font.setPointSize(fs)
		self.editorText.setFont(self.font)
		return True
			
	def setFont (self, fontName=''):
		if fontName != '' and fontName in self.fontNameList:
			self.fontName = fontName
			self.font = QFont(self.fontName)
			self.editorText.setFont(self.font)
			return True
		else:
			return False

	def getShortFontNameList (self):
		ls = ['Cascadia Code', 
		'Source Code Pro',
		'Candara',
		'Cambria',
		'Consolas',
		'Liberation Mono',
		'Courier New',
		'Courier',
		'System',
		'Terminal']

		ls += self.fontNameList
			
		return ls

	def setInitialFont (self):
		self.fontEnum = QFontDatabase()
		self.fontNameList = self.fontEnum.families(self.fontEnum.WritingSystem())

		#dPY ("font -- ", fontName)

		if 'Source Code Pro' in  self.fontNameList:
			self.fontName = 'Source Code Pro'
		elif 'Cascadia Code' in  self.fontNameList:
			self.fontName = 'Cascadia Code'
		elif 'Candara' in  self.fontNameList:
			self.fontName = 'Candara'
		elif 'Cambria' in  self.fontNameList:
			self.fontName = 'Cambria'
		elif 'Consolas' in  self.fontNameList:
			self.fontName = 'Consolas'
		elif 'Liberation Mono' in  self.fontNameList:
			self.fontName = 'Liberation Mono'
		elif 'Courier New' in  self.fontNameList:
			self.fontName = 'Courier New'
		elif 'Courier' in  self.fontNameList:
			self.fontName = 'Courier'
		elif 'System' in  self.fontNameList:
			self.fontName = 'System'
		elif 'Terminal' in  self.fontNameList:
			self.fontName = 'Terminal'
		else: #choose first font in list
			self.fontName = self.fontNameList[0]

		#print ("self.fontName = ", self.fontName)
		self.font = QFont(self.fontName, 14)
		self.editorText.setFont (self.font)
		#print ("getMaxLineChars returned ", self.getMaxLineChars())

	def eventFilter(self, obj, event):
		if event.type() == QtCore.QEvent.KeyPress and obj is self.editorText and self.editorText.hasFocus():
			key = event.key()
			cursor = self.editorText.textCursor()
			cursorLine = cursor.blockNumber()
			cursorCol = cursor.columnNumber()
			text = cursor.block().text()
			blockCount = self.editorText.document().blockCount()
			if cursorLine < blockCount - 1:
				self.editorText.moveCursor(QtGui.QTextCursor.End)  #end of line
				#resample current line parameters
				cursor = self.editorText.textCursor()
				cursorLine = cursor.blockNumber()
				cursorCol = cursor.columnNumber()
				text = cursor.block().text()
				#print ("moving to end of last line")
			if key in (Qt.Key_Enter, Qt.Key_Return):
				self.autoExpandContext = 'NONE'
				self.editorText.moveCursor(QtGui.QTextCursor.End)  #end of line
				self.handleInput (execCmdFromFile=False, cmdFromFile=text[len(self.promptStr)+1:])
				self.clearSelection()
				return True #consume the return key
			elif key == Qt.Key_Delete:
				self.autoExpandContext = 'NONE'
				if cursorCol < len(text) and cursorCol > len(self.promptStr):
					return False
				else:
					self.clearSelection()
					return True
			elif key == Qt.Key_Right:
				self.autoExpandContext = 'NONE'
				if cursorCol < len(text): 
					return False
				else:
					self.clearSelection()
					return True
			elif key == Qt.Key_Tab:
				self.clearSelection()
				self.handleTabExpand()
				return True
			elif key in (Qt.Key_PageUp, Qt.Key_PageDown):
				self.autoExpandContext = 'NONE'
				self.clearSelection()
				return True
			elif key == Qt.Key_Home:
				self.autoExpandContext = 'NONE'
				self.clearSelection()
				cursor.movePosition(QtGui.QTextCursor.Left, QtGui.QTextCursor.MoveAnchor, len(text) - len(self.promptStr) - 1)
				self.editorText.setTextCursor(cursor)
				return True
			elif key == Qt.Key_Escape:
				self.dismissCommand()
			elif key == Qt.Key_Up:
				self.autoExpandContext = 'NONE'
				self.clearSelection()
				#dPY ("UP:: indexHistory is ", self.indexHistory, lvl=11)
				#dPY ("UP VX.ca is ", self.VX.ca, lvl=11)
				if self.indexHistory == len(self.VX.ca):
					self.unEnteredCommand = cursor.block().text()
					self.unEnteredCommand = self.unEnteredCommand[len(self.promptStr)+1:]
					#dPY ("--------------UP: unEnteredCommand is captured: ", self.unEnteredCommand)
				if self.indexHistory > 0:
					#dPY ("UP: indexHistory is ", self.indexHistory, "len ca is ", len(self.VX.ca))
					self.indexHistory -= 1
					#dPY ("UP: indexHistory decremented to ", self.indexHistory)
					self.clearLine (cursor)
					self.editorText.insertPlainText(self.VX.ca[self.indexHistory])
				return True

			elif key == Qt.Key_Down:
				self.autoExpandContext = 'NONE'
				self.clearSelection()
				#dPY ("DOWN: indexHistory is ", self.indexHistory, lvl=11)
				#dPY ("DOWN: VX.ca is ", self.VX.ca, lvl=11)
				if self.indexHistory < len(self.VX.ca):
					self.indexHistory += 1
					#dPY ("DOWN: indexHistory incremented to ", self.indexHistory, lvl=11)
				else:
					return True
	
				if self.indexHistory < len(self.VX.ca):
					self.clearLine (cursor)
					self.editorText.insertPlainText(self.VX.ca[self.indexHistory])
				else:
					#dPY ("DOWN: indexHistory is ", self.indexHistory, "at top")
					#dPY ("DOWN: unEnteredCommand is ", self.unEnteredCommand)
					self.clearLine (cursor)
					if self.unEnteredCommand != '':
						self.editorText.insertPlainText(self.unEnteredCommand)
				return True

			elif key == Qt.Key_Left or key == Qt.Key_Backspace:
				if cursorCol > len(self.promptStr) + 1:
					return False
				else:
					self.clearSelection()
					return True
			if int(event.modifiers()) == Qt.CTRL:
				if key == Qt.Key_O or key == Qt.Key_E:
					self.fileOpen()
				elif key == Qt.Key_D:
					self.dismissCommand()
				elif key == Qt.Key_S:
					self.fileSaveAsGUI()
				elif key == Qt.Key_N:
					self.VX.ca.append(":cls")
					self.doClear()
				elif key == Qt.Key_Q or key == Qt.Key_Escape:
					self.fileQuit()	
		return super().eventFilter(obj, event)

	def dismissCommand (self):
		self.clearSelection()
		self.autoExpandContext = 'NONE'
		cursor = self.editorText.textCursor()
		text = cursor.block().text()
		if text != '':
			self.editorText.moveCursor(QtGui.QTextCursor.End)  #end of line
			self.inputStr = ''
			self.doInputCommand()

	def mouseLeftTripleClick (self):
		self.mouseLeftClickCount = 0
		mouseLineText = self.editorText.GetLineText(self.mouseClickLineNumber)
		## hasCmdPrompt = re.compile ('^#\d+>')
		## hasCmdPromptMatch = hasCmdPrompt.match (mouseLineText)
		#dPY ("hasCmdPromptMatch is ", hasCmdPromptMatch)
		hasCmdPromptMatch = mouseLineText.find('#')
		## if hasCmdPromptMatch != None:
		if hasCmdPromptMatch == 0:
			posS = self.editorText.XYToPosition(len(self.promptStr), self.mouseClickLineNumber)
			#dPY ("hasCmdPromptMatch is true -- posS is", posS)
		else:
			posS = self.editorText.XYToPosition(0, self.mouseClickLineNumber)
		posE = self.editorText.XYToPosition (len(mouseLineText), self.mouseClickLineNumber)
		self.editorText.SetSelection(posS, posE)
		#dPY ("triple click!!!")
		#dPY ("posS is ", posS, "posE is ", posE, "mouse line ", self.mouseClickLineNumber)

	def mouseMotionCallback (self, event=None):
		if event.LeftIsDown() == True:
			event.Skip()

	def printVars (self, var=None):
		prnv = self.VX.prnv (var)
		return ' ' + var + ' = ' + prnv[0] + prnv[1] + prnv[2]

	def showHelp (self, event=None, fromCmdLine=False):
		self.editorText.moveCursor(QtGui.QTextCursor.End)  #end of line
			
		if fromCmdLine == False:
			self.clearLine(self.editorText.textCursor())
			self.editorText.insertPlainText (':help')

		self.setTextColor('help')

		for s in HELP.split('\n'):
			if s != '':
				self.editorText.insertPlainText (s + '\n')

		self.setTextColor('normal')

		if fromCmdLine == False:
			self.VX.ca.append(":help")

		self.VX.ra.append('Help text was printed.')

		if fromCmdLine == False:
			self.editorText.moveCursor(QtGui.QTextCursor.End)  #end of line
			self.indexHistory = len(self.VX.ca)
			self.writePrompt()

	def doClear (self, event=None):
		self.VX.ra.append('')

		self.editorText.moveCursor(QtGui.QTextCursor.End)  #end of line

		self.indexHistory = len(self.VX.ca)
		#self.writePrompt()

	def bottomCheckBoxHandler (self, event):
		if self.bottomCheckBoxDEG.isChecked() == True:
			self.VX.degrees(True)
		else:
			self.VX.degrees(False)
		if self.bottomCheckBoxSCI.isChecked() == True:
			self.VX.sci = True
		else:
			self.VX.sci = False

	def handleInput (self, execCmdFromFile=False, cmdFromFile=''):
		self.inputStr = cmdFromFile
		if execCmdFromFile == True:
			self.editorText.insertPlainText (cmdFromFile)

		inputStrList = self.inputStr.split('#')[0].split(';')
		#dPY("inputStrList is ", inputStrList)

		for s in inputStrList:
			self.inputStr = s
			#dPY("calling  doInputCommand ")
			self.doInputCommand (execCmdFromFile, cmdFromFile)

	def postCmdExec(self):
		self.currentLineNumber = self.editorText.textCursor().blockNumber()
		self.indexHistory = len(self.VX.ca)
		self.completionEntryList = self.completionEntryListOrig + list(self.VX.stv.keys())
		self.writePrompt()
		self.setTextColor('normal')

	def handleCommand (self, restOfCmd='', execCmdFromFile=False):
		#print ("restOfCmd = ", restOfCmd)
		restOfCmd = restOfCmd.strip()
		self.editorText.insertPlainText ('\n')
		if self.inputStr.find(':ls') == 0:
			self.setTextColor('ls')
			self.editorText.insertPlainText ('List of variables:\n')
			result = ''
			for var in self.VX.stv.keys():
				if var != 'ans' and var != 'True' and var != 'False':
					value = self.printVars(var)
					self.editorText.insertPlainText (value + '\n')
					result += value + '\n'
			self.VX.ra.append(result)
		elif self.inputStr == "?" or self.inputStr == ":he" or self.inputStr == ":?" or self.inputStr == ":help":
			#dPY("Found :help!!!")
			self.showHelp(fromCmdLine=True)
			self.VX.ra.append('')
		elif self.inputStr.find(":exit") == 0 or self.inputStr.find(":quit") == 0 or self.inputStr.find(":q") == 0:
			self.Destroy()
		elif self.inputStr.find(":set") == 0:
			self.VX.ra.append(f'Info: doing command: {self.inputStr}')
			self.VXCommandHandler(restOfCmd, True)
		elif self.inputStr.find(":unset") == 0:
			self.VX.ra.append(f'Info: doing command: {self.inputStr}')
			self.VXCommandHandler(restOfCmd, False)
		elif self.inputStr.find(':print') == 0 or self.inputStr.find(':pr') == 0:
			#print something
			self.editorText.insertPlainText (restOfCmd)
			self.editorText.insertPlainText ("\n")
			self.VX.ra.append(f"'{restOfCmd}'")
		elif self.inputStr.find(':p') == 0 or self.inputStr.find(':prec') == 0 or\
				self.inputStr.find(':precision') == 0:
			if restOfCmd == '':
				self.writeInfo ('Info: current precision is ' + str(self.VX.rnd) + '\n', what=0)
			else:
				try:
					self.VX.rnd = int(restOfCmd)
					self.VX.setmp()
					self.writeInfo ('Info: set precision to '  + str(restOfCmd) + '\n', what=0)
				except (NameError, TypeError, ValueError, AttributeError, OverflowError):
					self.writeError ('Error: illegal precision value ' + str(restOfCmd) + '\n')
			self.VX.ra.append(str(self.VX.rnd))
		elif self.inputStr.find(':del') == 0:
			if restOfCmd != '':
				varsToDelList = restOfCmd.split()
				cannotDelete = ''
				for varList in varsToDelList:
					varsToDelInnerList = varList.split(',')
					for var in varsToDelInnerList:
						if var != '' and var != 'e' and var != 'pi' and var != 'True' and var != 'False' and var != 'ans':
							self.VX.delvar(var)
						else:
							cannotDelete += var + ' '
					#end for
				if len(cannotDelete) != 0:
					self.writeError ('Error: could not delete these variables:\n  ' + cannotDelete)
					self.VX.ra.append('Error: could not delete these variables: ' + cannotDelete)
				else:
					self.VX.ra.append('Deleted variables: '+restOfCmd)
		elif self.inputStr.find(':delall') == 0:
			self.VX.delall()
			self.VX.ra.append('')
		elif self.inputStr == ":cls" or self.inputStr == ":clear":
			self.doClear()
		elif self.inputStr == ":reset":
			self.VX.ca = []
			self.VX.ra = []
			self.VX.stv ['ans'] = '0'
			self.doClear()
		elif self.inputStr == ":history" or self.inputStr == ":his" or self.inputStr == ":h":
			result = ''
			lca = len(self.VX.ca)
			for i in range(lca):
				s = ' #' + str(i+1) + '\t\t' + self.VX.ca[i] + '\n'
				self.editorText.insertPlainText (s)
				result += s
			self.VX.ra.append(result)
		elif self.inputStr.find(':fs') == 0 or self.inputStr.find(':fsize') == 0:
			#print ("-- restOfCmd = ", restOfCmd)
			if restOfCmd != '':
				fontChanged = self.setFontSize (restOfCmd)
				if fontChanged == True:
					self.writeInfo (f'Info: font size changed to {restOfCmd}\n', what=0)
				else:
					self.writeError (f'Error: font size could not be changed to {restOfCmd}\n')
			else:
				fontChanged = self.fontSelect(event=None)
		elif self.inputStr.find(':f') == 0 or self.inputStr.find(':font') == 0:
			if restOfCmd != '':
				fontChanged = self.setFont (restOfCmd)
				if fontChanged == True:
					self.writeInfo (f'Info: font changed to {restOfCmd}\n', what=0)
				else:
					self.writeError (f'Error: font could not be changed to {restOfCmd}\n')
			else:
				fontChanged = self.fontSelect(event=None)
		elif self.inputStr.find(':save!') == 0 or self.inputStr.find(':s!') == 0 or\
				self.inputStr.find(':write!') == 0 or self.inputStr.find(':w!') == 0:
			fileSaved = self.fileSaveAs(fullFileName=restOfCmd, overwrite=True, fromCmdLine=True)
		elif self.inputStr.find(':save') == 0 or self.inputStr.find(':s') == 0 or\
				self.inputStr.find(':write') == 0 or self.inputStr.find(':w') == 0:
			fileSaved = self.fileSaveAs(restOfCmd, overwrite=False, fromCmdLine=True)
		elif self.inputStr.find(':run') == 0 or self.inputStr.find(':r') == 0 or\
				self.inputStr.find(':exec') == 0 or self.inputStr.find(':e') == 0:
			execdFile = self.fileOpen(fullFileName=restOfCmd, fromCmdLine=True)
		elif self.inputStr.find(':defw') == 0:
			if restOfCmd == '':
				self.writeInfo (f"Info: Default width is {self.VX.defw} bits.\n", what=0)
			else:
				try:
					self.VX.defw = int(restOfCmd)
					self.writeInfo (f"Info: Default width set to {self.VX.defw} bits.\n")
					self.VX.ra.append(f"Default width set to {self.VX.defw} bits.")
				except (NameError, TypeError, ValueError, AttributeError, OverflowError, SyntaxError):
					self.writeError ("Error: Need integer value for variable width.\n")
					self.VX.ra.append('Error: could not set default value for variable width.')
		else:
			self.writeError (f'Error: Command \'{self.inputStr}\' not found.\n')

		if execCmdFromFile == False:
			self.postCmdExec()

	def doInputCommand (self, execCmdFromFile=False, cmdFromFile=''):
		self.inputStr = self.inputStr.split('#')[0].strip()
		self.unEnteredCommand = ''
		#print ("--------------")
		#print ("command array = ", self.VX.ca)
		#print ("inputStr = ", self.inputStr)
		#print ("--------------")
		if self.inputStr != '':
			self.VX.ca.append(self.inputStr)
			cmdList = self.inputStr.split()
			#print ("A. cmdList = ", cmdList)
			startCmd = cmdList[0]
			cmdList = self.inputStr.split(startCmd)
			#print ("B. cmdList = ", cmdList)
			if (self.allCommands.find(startCmd) >= 0 and startCmd.find(':') == 0) or (self.inputStr == '?'):
				self.handleCommand(cmdList[1], execCmdFromFile=execCmdFromFile)
				return

			if chr(0x2219)+' e' in self.inputStr or chr(0x2219)+'e' in self.inputStr:
				self.inputStr = self.inputStr.replace(' ', '')
				self.inputStr = self.inputStr.replace(chr(0x2219), '*1')
				#print ("FOUND =", self.inputStr)
			elif chr(0x2219)+' 10' in self.inputStr:
				self.inputStr = self.inputStr.replace(' ', '')
				self.inputStr = self.inputStr.replace(chr(0x2219)+'10', '*1e')
				#print ("FOUND =", self.inputStr)
			elif chr(0x2219)+'10' in self.inputStr:
				self.inputStr = self.inputStr.replace(' ', '')
				self.inputStr = self.inputStr.replace(chr(0x2219)+'10', '*1e')
				#print ("FOUND =", self.inputStr)
			try:
				rawValue = self.VX.ev(self.inputStr)
			except:
				#top level exception handler
				rawValue = ['', '', '', 
						"Error: Fatal exception, VX will close. Please send VexX.log (if available) to anirbax@gmail.com", 
						'']
				raise VexCoreError

			self.editorText.insertPlainText ('\n')
			#print ("rawValue = ", rawValue, " ~~ len = ", len(rawValue))
			## rawValue[0]: '  ans = '
			## rawValue[1]: mantissa
			## rawValue[2]: chr(0x2219) + ' 10'
			## rawValue[3]: exponent as superscript
			## rawValue[4]: error string
			## rawValue[5]: warning string
			if len(rawValue) > 4:
				if rawValue[4] == '':
					if rawValue[5] == '':
						self.writeValue (rawValue[0] + rawValue[1] + rawValue[2], rawValue[3])
				else:
					self.writeError (rawValue[4] + '\n')

			if rawValue[5] != '':
				self.writeValue (rawValue[0] + rawValue[1] + rawValue[2], rawValue[3])
				if 'Info:' in rawValue[5]:
					self.writeInfo (rawValue[5] + '\n', what=0) #info
				else:
					self.writeInfo (rawValue[5] + '\n', 2) #warning

			#if self.VX.getmp() > 10000:
			#	self.editorText.insertPlainText (value)
			#	self.editorText.insertPlainText ('\n')

			## if self.printMaxWidth < 150:

			#dPY("eval result is ", result)
			if self.VX.getmp() > 10000:
				self.VX.ra.append('Result too large (precision > 10000)')
			else:
				self.VX.ra.append(rawValue[0])
		else:
			self.editorText.insertPlainText ('\n')

		if execCmdFromFile == False:
			#when doInputCommand is called from a :run command
			#do not print the prompt again
			self.postCmdExec()
		self.editorText.moveCursor(QtGui.QTextCursor.End)  #end of line

	def executeFile (self, fullFileName='', showGuiErr=False):
		if os.name == 'nt':
			fullFileName = fullFileName.lower()
		if not os.path.isfile(fullFileName):
			fullFileName = self.dirName + fullFileName
			if not os.path.isfile(fullFileName):
				self.writeError("Error: File "+fullFileName+" not found.\n")
				return False
		#dPY ("######## executeFile: fullFileName=", fullFileName)	
		#open another file for writing called fullFileName+'.lock'
		if os.path.isfile(fullFileName+'.lock'):
			if showGuiErr == True:
				msg = QMessageBox()
				msg.setIcon(QMessageBox.Critical)
				msg.setText("Error: File "+fullFileName+" not found.")
				msg.setWindowTitle("File Not Found Error")
				retval = msg.exec_()
			self.writeError("Error: File "+fullFileName+" is already being executed.\n")
			return False
		else:
			lock = None
			try:
				lock = open(fullFileName+'.lock', 'wb')
			except (NameError, OSError):
				self.writeError("\nError: Failed to create lock for file "+fullFileName+".\n")
				try:
					lock.close()
					os.remove(fullFileName+'.lock')
				except:
					pass
				return False

			try:
				self.fullLockFileName = fullFileName+'.lock'
				with open(fullFileName, 'r', encoding="utf-8") as f:
					self.writeInfo ('Info: executing :run ' + fullFileName + '\n', what=0)
					for line in f:
						line = line.strip()
						if line != '' and line.find('#') != 0:
							#dPY("executeFile: doing ", line)
							self.postCmdExec()
							self.handleInput(execCmdFromFile=True, cmdFromFile=line)
							#indexHistory will be updated in handleInput
					f.close()
				lock.close()
				os.remove(fullFileName+'.lock')
				return True
			except (NameError, OSError):
				self.writeError("\nError: File "+fullFileName+" could not be executed.\n")
				try:
					lock.close()
					os.remove(fullFileName+'.lock')
				except:
					pass
				return False

	def fileOpen(self,event=None, fullFileName='', fromCmdLine=False):
		retVal = False
		if fullFileName == '':
			options = QFileDialog.Options()
			options |= QFileDialog.DontUseNativeDialog
			if self.dirName == '':
				self.dirName = os.path.expanduser('.')
			else:
				self.dirName = os.path.expanduser(self.dirName)
			fDialog = QFileDialog()
			fDialog.setDirectory(self.dirName)
			self.fileName, _ = fDialog.getOpenFileName(self,"Choose a Vex command file to run", "","*.vex", options=options)
			if self.fileName:
				#print(self.fileName)
				self.dirName = os.path.dirname(self.fileName)
				fullFileName = self.fileName
				self.fileName = os.path.basename(self.fileName)
				#store executable filenames in an array and check for recursive
				#executions from file
				
				self.VX.ca.append((self.VX.ca.pop() if len(self.VX.ca) > 0 else ':run') + ' ' + fullFileName)
				self.VX.ra.append('')
				if fromCmdLine == False:
					self.writeInfo (':run '+ fullFileName + '\n')
				#self.writeInfo ('Info: executing :run ' + fullFileName + '\n')
				dPY ("######## fileOpen A: fullFileName=", fullFileName)	

				if not os.path.isfile(fullFileName):
					if fromCmdLine == False:
						msg = QMessageBox()
						msg.setIcon(QMessageBox.Critical)
						msg.setText("Error: File "+fullFileName+" not found.")
						msg.setWindowTitle("File Not Found Error")
						retval = msg.exec_()
					self.writeError("Error: File "+fullFileName+" not found.\n")
					return False
				else:
					retVal = self.executeFile(fullFileName, showGuiErr=True)
			else:
				if fromCmdLine == False:
					self.writeInfo (':run\n')
					self.writeInfo ('Info: execution from file cancelled.\n', what=0)
					self.writePrompt()
				else:
					self.writeInfo ('Info: execution from file cancelled.\n', what=0)
				retVal = False
			self.indexHistory = len(self.VX.ca)
		else:
			if not os.path.isfile(fullFileName):
				if fromCmdLine == False:
					msg = QMessageBox()
					msg.setIcon(QMessageBox.Critical)
					msg.setText("Error: File "+fullFileName+" not found.")
					msg.setWindowTitle("File Not Found Error")
					retval = msg.exec_()
				self.writeError("Error: File "+fullFileName+" not found.\n")
				return False
			else:
				dPY ("######## fileOpen B: fullFileName=", fullFileName)	
				retVal = self.executeFile(fullFileName, showGuiErr=True)
		#endif
		return retVal

	def fileSaveAsGUI(self, event=None):
		self.VX.ca.append(":write")
		self.fileSaveAs(fullFileName='', overwrite=False, fromCmdLine=False)

	def fileSaveAs(self, fullFileName='', overwrite=False, fromCmdLine=False):
		#print ("----------- ENTERED fileSaveAs: fullFileName=", fullFileName, " overwrite=", overwrite)
		cmdText = ''
		self.editorText.moveCursor(QtGui.QTextCursor.End)  #end of line

		if fullFileName != '':
			#from command line
			if os.path.isfile(fullFileName+'.lock'):
				#file is opened for execution
				if fromCmdLine == False: #from pressing Ctrl-S or from menu
					self.writeInfo (':save\n')
				self.VX.ra.append('File is running or locked. Write cancelled.\n')
				self.writeError("Error: File "+fullFileName+" is running or locked.\n")
				self.writePrompt()
				return False

			#this part is executed when calling from command line
			if os.name == 'nt':
				fullFileName = fullFileName.lower()

			if os.path.isfile(fullFileName) and overwrite == False:
				#file exists
				if fromCmdLine == False: #from pressing Ctrl-S or from menu
					self.writeInfo (':save\n')
				self.writeError("Error: File "+fullFileName+" already exists. Command failed.\n")
				self.VX.ca.append(self.VX.ca.pop() + ' ' if overwrite==False else '! '+ fullFileName)
				self.VX.ra.append('File already exists. Write cancelled.')
				return False

		else: #fullFileName == '':
			options = QFileDialog.Options()
			options |= QFileDialog.DontUseNativeDialog
			if self.dirName == '':
				self.dirName = os.path.expanduser('.')
			else:
				self.dirName = os.path.expanduser(self.dirName)
			fDialog = QFileDialog()
			fDialog.setDirectory(self.dirName)
			self.fileName, _ = fDialog.getSaveFileName(self,"Choose a Vex command file to save as", "","*.vex", options=options)
			if self.fileName:
				overwrite = True
				if self.fileName[-4:].lower() != '.vex':
					self.fileName += '.vex'
				#print("SAVING ", self.fileName)
				self.dirName = os.path.dirname(self.fileName)
				fullFileName = self.fileName
				self.fullLockFileName = fullFileName+'.lock'
				self.fileName = os.path.basename(self.fileName)

				if os.name == 'nt':
					fullFileName = fullFileName.lower()

				self.VX.ca.pop()
				self.VX.ca.append(":write " + fullFileName)
			else:
				if fromCmdLine == False: #from pressing Ctrl-S or from menu
					self.writeInfo (':save\n')
				self.writeInfo ('Info: write to file cancelled.\n', what=0)
				if fromCmdLine == False: #from pressing Ctrl-S or from menu
					self.writePrompt()
				self.VX.ca.pop()
				self.VX.ca.append(":save " + fullFileName)
				self.VX.ra.append('Write to file cancelled.')
				return False
			#endif
			self.indexHistory = len(self.VX.ca)

		#endif

		infoText = 'Info: doing command :write '

		try:
			lock = open(fullFileName+'.lock', 'wb')
		except (NameError, OSError):
			self.writeError("\nError: Failed to create lock for file "+fullFileName+".\n")
			try:
				lock.close()
				os.remove(fullFileName+'.lock')
			except:
				pass
			if fromCmdLine == False: #from pressing Ctrl-S or from menu
				self.writeInfo (f':save {fullFileName}\n')
			self.writeError("Error: File "+fullFileName+" lock failed.\n")
			self.VX.ra.append('File lock failed. Write cancelled.')
			self.editorText.moveCursor(QtGui.QTextCursor.End)  #end of line
			return False

		try:
			with open(fullFileName, 'w', encoding="utf-8", newline='\n') as f:
				dPY ("WRITING TO FILE --------------- "+infoText + fullFileName)
				self.VX.ra.append(infoText + fullFileName)
				self.indexHistory = len(self.VX.ca)
				for i in range(len(self.VX.ca) - 1): #do not write the last command for cmdLine, which is :write
					cmd = '#' + str(i+1) + '>\n ' + self.VX.ca[i] + '\n'
					rsltList = self.VX.ra[i].split('\n')
					#dPY("cmd ", cmd, "rslt ", rslt)
					f.write(cmd)
					for rslt in rsltList:
						if rslt != '':
							f.write(' ## ' + rslt + '\n')
				f.close()

			if fromCmdLine == False: #from pressing Ctrl-S or from menu
				if overwrite == True:
					self.writeInfo (':write! ' + fullFileName + '\n')
				else:
					self.writeInfo (':write ' + fullFileName + '\n')

			self.writeInfo (infoText + fullFileName + '\n', what=0)

			try:
				lock.close()
				os.remove(fullFileName+'.lock')
				#print ("~~~~~~~~` ########## REMOVED SAVE LOCK")
			except:
				pass
			self.editorText.moveCursor(QtGui.QTextCursor.End)  #end of line
			if fromCmdLine == False: #from pressing Ctrl-S or from menu
				self.writePrompt()
			return True
		except OSError:
			self.writeError ("Error: File could not be saved.\n")
			if fromCmdLine == False: #from pressing Ctrl-S or from menu
				self.writePrompt()
			try:
				lock.close()
				os.remove(fullFileName+'.lock')
			except:
				pass
			self.editorText.moveCursor(QtGui.QTextCursor.End)  #end of line
			return False

	def fileQuit(self, event):
		self.VX.pybfend()
		self.Destroy()

	def helpAbout (self,e):
		# Create a message dialog box
		msg = QMessageBox()
		msg.setIcon(QMessageBox.Information)
		msg.setText("Verilog Expression Calculator VX Qt5 version v2022-2-27\n(c) 2018-2022 Anirban Banerjee")
		msg.setWindowTitle("About VX")
		retval = msg.exec_()

def VXCoreEntryPoint():
	parser = argparse.ArgumentParser(description='Vex')

	args, fileArgs = ('', '')
	args, fileArgs = parser.parse_known_args()

	vexFile = ''
	if len(fileArgs) != 0:
		vexFile = fileArgs[0]

	#dPY ("args is ", args)
	#dPY ("fileArgs is ", fileArgs)
	#dPY ("vexFile is ", vexFile)
	argTuple = (vexFile)

	app = QApplication(sys.argv)
	form = qVX()
	form.setTitleArgs ("Calculator VX", argTuple)
	form.show()
	app.exec_()

