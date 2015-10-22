'''
Copyright 2015 University of Freibrug
Hannah Bast <bast@cs.uni-freiburg.de>

Edits for Exercise-1

Numair Mansur <numair.mansur@gmail.com>
'''

import re
import sys

''' A simple inverted index'''

class InvertedIndex:

	def __init__(self):
		'''create and empty inverted index'''
		self.inverted_lists = dict()


	def read_from_file(self,file_name):
		'''Construct inverted index from given file.
		
		>>> ii = InvertedIndex()
		>>> ii.read_from_file("example.txt")
		>>> sorted(ii.inverted_lists.items())
		{}


		'''

		with open(file_name) as file:
			doc_id=0
			for line in file:
				doc_id += 1
				for word in re.split("\W+", line):
					word = word.lower()
					if len(word) > 0:
						''' If word seen for the first time, create empty list for it'''
						if not word in self.inverted_lists:
							self.inverted_lists[word] = list()
						self.inverted_lists[word].append(doc_id)

	
	def merge(self,list1,list2):
		'''Merge 2 lists using the Algorithm presented in the lecture'''
						
	

	def process_query(self,query_word):
		'''Process user's query word'''


if __name__ == "__main__":
	if len(sys.argv) != 2:
		print "Usage: python inverted_index.py <file>"
		sys.exit()

	file_name = sys.argv[1]
	ii = InvertedIndex()
	ii.read_from_file(file_name)
	for word, inverted_list in ii.inverted_lists.items():
		if word =="a":
			print("%s:%d" % (word,len(inverted_list)))
