import plex

class ParseError(Exception):
	""" A user defined exception class, to describe parse errors. """
	pass

class MyParser:
	""" A class encapsulating all parsing functionality
	for a particular grammar. """
	
	def create_scanner(self,fp):
		""" Creates a plex scanner for a particular grammar 
		to operate on file object fp. """

		# define some pattern constructs
		notop = plex.Str("not")
		andop = plex.Str("and")
		orop = plex.Str("or")
		true = plex.NoCase(plex.Str("true","t","1")) 
		false = plex.NoCase(plex.Str("false","f","0"))
		equals = plex.Str("=")

		letter = plex.Range("AZaz")
		digit = plex.Range("09")

		variable = letter + plex.Rep(letter | digit)
		parenthesis = plex.Str("(",")")
		keyword = plex.Str("print")		
		space = plex.Any(" \t\n")

		# the scanner lexicon - constructor argument is a list of (pattern,action ) tuples
		lexicon = plex.Lexicon([
			(notop,plex.TEXT),
			(andop, plex.TEXT),
			(orop,plex.TEXT),
			(true,'TRUE'),
			(false,'FALSE'),
			(equals, plex.TEXT),
			(parenthesis,plex.TEXT),
			(space,plex.IGNORE),
			(keyword, plex.TEXT),
			(variable, 'VAR')
			])
		
		# create and store the scanner object
		self.scanner = plex.Scanner(lexicon,fp)
		
		# get initial lookahead
		self.la,self.val = self.next_token()


	def next_token(self):
		""" Returns tuple (next_token,matched-text). """
		
		return self.scanner.read()		


	def position(self):
		""" Utility function that returns position in text in case of errors.
		Here it simply returns the scanner position. """
		
		return self.scanner.position()


	def match(self,token):
		""" Consumes (matches with current lookahead) an expected token.
		Raises ParseError if anything else is found. Acquires new lookahead. """ 
		
		if self.la==token:
			print("TOKEN: ",self.val)
			self.la,self.val = self.next_token()
			
		else:
			raise ParseError("found {} instead of {}".format(self.la,token))


	def parse(self,fp):
		""" Creates scanner for input file object fp and calls the parse logic code. """
		
		# create the plex scanner for fp
		self.create_scanner(fp)
		self.stmt_list()
		
		# call parsing logic
		# self.session()

	def stmt_list(self):
		if self.la=='VAR' or self.la=='print':
			self.stmt()
			self.stmt_list()
		elif self.la is None: #yparxei keno sto first
			return
		else:
			raise ParseError("Error In function stmt_list(): variable or print expected")


	def stmt(self):
		if self.la=='VAR':
			# print(self.val)
			self.match('VAR')
			# print(self.la)
			self.match('=')
			# print(self.la)
			self.expr()
		elif self.la=='print':
			self.match('print')
			self.expr()
		else:
			raise ParseError("Error In function stmt(): variable or = or print expected")


	def expr(self):
		if self.la=='(' or self.la=='VAR' or self.la=='TRUE' or self.la=='FALSE' or 'not':
			self.term()
			self.term_tail()
		else:
			raise ParseError("Error In function expr(): ( or variable or boolean or not expected")


	def term_tail(self):
		if self.la=='or':
			self.orop()
			self.term()
			self.term_tail()
		elif self.la==')' or self.la=='VAR' or self.la == 'print': #apo to follow set tou term_tal
			return 
		elif self.la is None:
			return	
		else:
			raise ParseError("Error In function term_tail(): 'or' or ) or variable or print expected")

	def term(self):
		if self.la=='(' or self.la=='VAR' or self.la=='TRUE' or self.la=='FALSE' or 'not':
			self.notop()
			self.factor()
			self.factor_tail()
		else:
			raise ParseError("Error In function term(): ( or variable or boolean or not expected")

	def factor_tail(self):
		if self.la=='and':
			self.andop()
			self.notop() #ama exei
			self.factor()
			self.factor_tail()
		if self.la == 'VAR' or  self.la == 'or'  or  self.la == ')'  or  self.la == 'print' : #apo to follow set tou factor_tail
			return
		if self.la is None:
			return
		else:
			# print(self.la)
			raise ParseError("Error In function factor_tail(): and or 'or' or variable or ) or print expected")

	def factor(self):
		if self.la=='(':
			self.match('(')
			self.expr()
			self.match(')')
			# return e
		elif self.la=='VAR':
			self.match('VAR')
			# return('VARIABLE')
		elif self.la=='TRUE' or self.la=='FALSE':
			self.boolean()
		else:
			raise ParseError("Error in function factor(): ( or variable or boolean expected")


	def boolean(self):
		if self.la=='TRUE':
			self.match('TRUE')
			# return('TRUE')
		elif self.la=='FALSE':
			self.match('FALSE')
			# return('FALSE')
		else:
			raise ParseError("Error in function boolean(): true or false expected")


	def orop(self):
		if self.la=='or':
			self.match('or')
			# return('or')
		else:
			raise ParseError("Error in function orop(): 'or' expected")

	def andop(self):
		if self.la=='and':
			self.match('and')
			# return('and')
		else:
			raise ParseError("Error in function andop(): 'and' expected")

	def notop(self):
			if self.la=='not':
				self.match('not')
				# return('not')
			else:
				return

# the main part of prog

# create the parser object
parser = MyParser()

# open file for parsing
with open("myparser.txt","r") as fp:

	# parse file
	try:
		parser.parse(fp)
	except plex.errors.PlexError:
		_,lineno,charno = parser.position()	
		print("Scanner Error: at line {} char {}".format(lineno,charno+1))
	except ParseError as perr:
		_,lineno,charno = parser.position()	
		print("Parser Error: {} at line {} char {}".format(perr,lineno,charno+1))