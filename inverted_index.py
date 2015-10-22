'''
Copyright 2015 University of Freibrug
Hannah Bast <bast@cs.uni-freiburg.de>

Edits for Exercise-1

Numair Mansur <numair.mansur@gmail.com>
'''

import re

''' A simple inverted index'''

class InvertedIndex:

	def read_from_file(self,file_name):
		with open(file_name) as file:
			for line in file:
				for word in re.split("\W+", line):
					word = word.lower()
					print word


if __name__ == "__main__":
	ii = InvertedIndex()
	ii.read_from_file("example.txt")
