'''
Exam Preparation for lecture # 2
'''

import re
import sys
from collections import Counter


GREEN_CLR = '\033[32m'
YELLOW_CLR = '\033[33m'
PURPLE_CLR = '\033[35m'
END_CLR = '\033[0m'

class InvertedIndex:

	def __init__(self):
		"""
			Create an empty inverted index.
		"""
		self.inverted_lists = dict()
		self.records = dict()


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
				self.records[doc_id] = line.replace('\n', '')
				for word in re.split("\W+", line):
					word = word.lower()
					if len(word) > 0:
						""" Check if word seen for the first time
						create an empty inverted list for it """
						if not word in self.inverted_lists:
							self.inverted_lists[word]=list()
						self.inverted_lists[word].append(doc_id)

	def merge(self,l1,l2):
		""" Given two given inverted list. Merge them in a sorted order. """
		#l1 = [1,3,3,4,6]
		#l2 = [2,3,5,7,7]
		merged_list = list()

		i,j = 0,0

		while i < len(l1) and j < len(l2):
			if l1[i] < l2[j]:
				merged_list.append(l1[i])
				i += 1
			else:
				merged_list.append(l2[j])
				j += 1
		if i < len(l1):
			merged_list = merged_list + l1[i:len(l1)]
		if j < len(l2):
			merged_list = merged_list + l2[j:len(l2)]

		return merged_list





	def process_query(self, query):
		""" TODO: Process Query Method """
		result_list = list()
		for word in re.split("\W+", query):
			word = word.lower()
			if word in self.inverted_lists.keys():
				result_list = self.merge(result_list,self.inverted_lists[word])
		document_ids = list(set(result_list))
		return Counter(result_list).most_common()


	def print_output(self, hits, query):
		for hit in hits:
			record_title = self.records[hit[0]].split('\t')[0]

			print('%s (# of keywords occurrences: %s)' %
				  (GREEN_CLR + record_title + END_CLR, hit[1]))

			keywords = [word.lower() for word in re.split("\W+", query)]
			description = self.records[hit[0]].split('\t')
			description = description[0] if len(description) == 1 \
				else description[1]

			# Highlighting keywords
			words = description.split(' ')
			for word in words:
				truncated_word = re.sub(r'[^\w]', '', word)
				if truncated_word.lower() in keywords:
					wrapped_word = YELLOW_CLR + truncated_word + END_CLR
					words[words.index(word)] = \
						word.replace(truncated_word, wrapped_word)
			print(' '.join(words), '\n')



	def main(self):
		"""Main Method """
		if len(sys.argv) != 2:
			print("Usage: python 3 inverted_index.py <file>")
			sys.exit()

		file_name = sys.argv[1]
		self.read_from_file(file_name)

		while True:
			message = "> Enter the Query ('exit' for quitting): "
			query = input(message)
			if query == "exit":
				break
			hits = self.process_query(query)
			if any(hits):
				self.print_output(hits[:3],query)
			else:
				print("no hits")

		print("")



if __name__ == "__main__":
	ii = InvertedIndex()
	ii.main()