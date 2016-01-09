'''
Exam Preparation for lecture # 8
'''

import re
import sys
from collections import Counter
from math import log
import numpy


GREEN_CLR = '\033[32m'
YELLOW_CLR = '\033[33m'
PURPLE_CLR = '\033[35m'
END_CLR = '\033[0m'


k = 0.75
b = 0.0


class InvertedIndex:

    def __init__(self):
        """
                Create an empty inverted index.
        """
        self.inverted_lists = dict()
        self.records = dict()
        self.term_frequency = dict()
        self.DL = dict()
        self.doc_id = 0
        self.AVDL = 0
        self.num_terms = 0  # Number of terms
        self.num_docs = 0  # Number of documents
        self.terms = [] # an array containing all the terms in the document

    def read_from_file(self, file_name):
        """
        Construct InvertedIndex from given file_name. The format of the file
        is one record per line.
        >>> ii = InvertedIndex()
        >>> ii.read_from_file("example.txt")
        >>> ii.terms
        ['internet', 'web', 'surfing', 'beach']
        >>> sorted(ii.inverted_lists.items())
        [('beach', [4, 5, 6]), ('internet', [1, 2, 4]), ('surfing', [1, 2, 3, 4, 4, 5, 6]), ('web', [1, 3, 4])]
        """

        with open(file_name) as file:
            for line in file:
                self.doc_id += 1
                self.records[self.doc_id] = line.replace('\n', '')
                document_words = re.split("\W+", line)
                self.DL[self.doc_id] = len(document_words)
                for term in document_words:
                    term = term.lower()
                    if len(term) > 0:
                        """ Check if word seen for the first time
                        create an empty inverted list for it """

                        if term not in self.inverted_lists:
                            self.inverted_lists[term] = list()
                            self.term_frequency[term] = dict()
                            self.terms.append(term)

                        self.inverted_lists[term].append(self.doc_id)

                        if self.doc_id in self.term_frequency[term].keys():
                            self.term_frequency[term][self.doc_id] += 1
                        else:
                            self.term_frequency[term][self.doc_id] = 1

            # Number of documents is the last value of doc_id.
            self.num_docs = self.doc_id
            self.num_terms = len(self.inverted_lists)

            # Don't append multiple document ids in the inverted index lists
            # if len(self.inverted_lists[word]) == 0 or \
            #	self.inverted_lists[word][-1] != doc_id:
            #	self.inverted_lists[word].append(doc_id)

    def build_term_document_matrix(self):
        """ Build the term-document matrix from the already built inverted index """
        A = numpy.zeros((self.num_terms, self.num_docs)) # creating a matrix with a lot of zeros 
        for i,term in enumerate(self.terms):
        	for doc_id in self.inverted_lists[term]:
        		A[i,doc_id-1] += 1
        return A


    def merge(self, l1, l2):
        """ Given two given inverted list. Merge them in a sorted order. """
        #l1 = [[1, 1], [3, 2], [4, 1], [6, 1]]
        #l2 = [[2, 1], [3, 1], [5, 1], [7, 2]]

        merged_list = list()
        i, j = 0, 0

        while i < len(l1) and j < len(l2):
            if l1[i][0] < l2[j][0]:
                merged_list.append(l1[i])
                i += 1
            elif l1[i][0] == l2[j][0]:
                merged_list.append([l1[i][0], l1[i][1] + l2[j][1]])
                i += 1
                j += 1
            else:
                merged_list.append(l2[j])
                j += 1

        if i < len(l1):
            merged_list = merged_list + l1[i:len(l1)]
        if j < len(l2):
            merged_list = merged_list + l2[j:len(l2)]

        return merged_list

    def bm_25(self, tf, df, N, AVDL, DL):
        return tf * (k + 1) / (k * (1 - b + b * DL / AVDL) +
                               tf) * log((N / df), 2)

    def process_query(self, query):
        """ TODO: Process Query Method """
        result_list = list()
        bm_25_scores = list()
        for word in re.split("\W+", query):
            word = word.lower()
            if word in self.inverted_lists.keys():
                for document_id in list(self.term_frequency[word].keys()):
                    tf = self.term_frequency[word][document_id]
                    df = len(self.inverted_lists[word])
                    N = self.doc_id
                    bm25 = self.bm_25(
                        tf, df, N, self.AVDL, self.DL[document_id])
                    bm_25_scores.append([document_id, bm25])
                result_list = self.merge(result_list, bm_25_scores)

        return sorted(result_list, key=lambda x: x[1], reverse=True)

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
        A = self.build_term_document_matrix() #Building the Term Document Matrix
        numpy.set_printoptions(formatter = {"float":lambda x : "%2.0f" %x})
        print(A)
        q= numpy.array([0,1,1,0]) # Query Array. To be done automatically
        print(q)
        print()
        scores = q.dot(A)
        print(scores)
        self.AVDL = sum(self.DL.values()) / self.doc_id
        # print(self.inverted_lists)
        # print(list(self.term_frequency['docum'].keys()))
        # print(self.DL)
        # print(self.doc_id)
        # print(self.AVDL)

        while True:
            message = "> Enter the Query ('exit' for quitting): "
            query = input(message)
            if query == "exit":
                break
            hits = self.process_query(query)
            if any(hits):
                self.print_output(hits[:3], query)
            else:
                print("no hits")

        print("")


if __name__ == "__main__":
    ii = InvertedIndex()
    ii.main()
