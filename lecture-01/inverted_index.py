'''
Exam Preparation for lecture # 1
'''

import re
import sys

class InvertedIndex:

	def __init__(self):
		"""
			Create an empty inverted index.
		"""
		self.inverted_lists = dict()


	def read_from_file(self,file_name):
		"""
		Construct InvertedIndex from given file_name. The format of the file 
		is one record per line.
		>>> ii = InvertedIndex()
		>>> ii.read_from_file("example.txt")
		>>> sorted(ii.inverted_lists.items())
		[('docum', [1, 2, 3]), ('first', [1]), ('second', [2]), ('third', [3])]
		"""
		doc_id = 0
		with open(file_name) as file:
			for line in file:
				doc_id += 1
				for word in re.split("\W+", line):
					word = word.lower()
					if len(word) > 0:
						""" Check if word seen for the first time
						create an empty inverted list for it """
						if not word in self.inverted_lists:
							self.inverted_lists[word]=list()
						self.inverted_lists[word].append(doc_id)

	def merge(self):
		""" TODO: Merge method """

	def process_query(self, query):
		""" TODO: Process Query Method """


	def main(self):
		""" TODO: Main Method """



if __name__ == "__main__":
	if len(sys.argv) != 2:
		print("Usage: python 3 inverted_index.py <file>")
		sys.exit()
	file_name = sys.argv[1]
	ii = InvertedIndex()
	ii.read_from_file(file_name)