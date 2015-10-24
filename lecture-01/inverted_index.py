"""
Copyright 2015 University of Freiburg
Hannah Bast <bast@cs.uni-freiburg.de>
"""

import re
import sys


class InvertedIndex:
    """ A simple inverted index, as explained in the lecture. """

    def __init__(self):
        """ Create an empty inverted index. """

        self.inverted_lists = dict()

    def read_from_file(self, file_name):
        """
        Construct inverted index from given file. The format is one record per
        line.

        >>> ii = InvertedIndex()
        >>> ii.read_from_file("example.txt")
        >>> sorted(ii.inverted_lists.items())
        [('docum', [1, 2, 3]), ('first', [1]), ('second', [2]), ('third', [3])]
        """

        with open(file_name) as file:
            doc_id = 0
            for line in file:
                doc_id += 1
                for word in re.split("\W+", line):
                    word = word.lower()
                    if len(word) > 0:
                    	if word == 'cool' and doc_id == 5327:
                    		print "FOUND COOL !!! in DOC ID: " + str(doc_id)
                    		print line
                        """ If a word is seen for first time, create an empty
                        inverted list for it. """
                        if word not in self.inverted_lists:
                            self.inverted_lists[word] = list()
                        self.inverted_lists[word].append(doc_id)

    def merge(self, l1, l2):
        """
        Merges two given inverted lists

        >>> ii = InvertedIndex()
        >>> l1 = [1, 3, 3, 4, 6]
        >>> l2 = [2, 3, 5, 7, 7]
        >>> ii.merge(l1, l2)
        [1, 2, 3, 3, 3, 4, 5, 6, 7, 7]
        """

        # The simpliest and naive implementation
        # return sorted(l1 + l2)

        merged_list = list()

        while len(l1) + len(l2) > 0:
            if len(l1) == 0:
                merged_list.extend(l2)
                l2 = list()
            elif len(l2) == 0:
                merged_list.extend(l1)
                l1 = list()
            else:
                if l1[0] < l2[0]:
                    merged_list.append(l1.pop(0))
                else:
                    merged_list.append(l2.pop(0))

        return merged_list

    def process_query(self, query):
        """
        Computes the list of ids of all records containing at least one word
        from the given query.
        """
        lists = list()
        merged_list = list()

        for word in re.split("\W+", query):
            word = word.lower()
            if any(word):
                if word in self.inverted_lists.keys():
                    lists.append(self.inverted_lists[word])

        for i in range(len(lists)):
            merged_list = self.merge(merged_list, lists[i])

        list_of_pairs = [[record_id, merged_list.count(record_id)]
                         for record_id in sorted(set(merged_list))]

        list_of_pairs = sorted(list_of_pairs, key=lambda x: x[1], reverse=True)

        return list_of_pairs

    def main(self):
        """  """
        if len(sys.argv) != 2:
            print("Usage: python3 inverted_index.py <file>")
            sys.exit()

        file_name = sys.argv[1]
        self.read_from_file(file_name)

        # print(ii.inverted_lists)

        while True:
            query = raw_input('Enter the query (enter "exit" for quitting): ')
            if query == 'exit':
                break

            result = ii.process_query(query)

            if any(result):
                print(result[:3])
            else:
                print('No hits')


if __name__ == "__main__":
    ii = InvertedIndex()
    ii.main()
    print ii.inverted_lists['cool']