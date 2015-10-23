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
                        """ If word seen for first time, create empty inverted
                        list for it. """
                        if word not in self.inverted_lists:
                            self.inverted_lists[word] = list()
                        self.inverted_lists[word].append(doc_id)

    def merge(self, l1, l2):
        """ Merges two given inverted lists """

        # Straightforward (dumb?) way
        # return sorted(l1 + l2)

        # Complicated (the right?) way

        # l1 = [1, 3, 3, 4, 6]
        # l2 = [2, 3, 5, 7, 7]
        # l1 = [13, 57, 57, 114, 987]
        # l2 = [5, 23, 23, 23, 57, 257]

        merged_list = list()
        last_items = False
        i = 0
        j = 0

        while i + j <= len(l1) + len(l2) - 2:
            if l1[i] < l2[j] or last_items:
                merged_list.append(l1[i])
                i += 1
            elif l1[i] == l2[j]:
                merged_list.extend([l1[i], l2[j]])
                i += 1
                j += 1
            else:
                merged_list.append(l2[j])
                if j + 1 != len(l2):
                    j += 1
                    i, j = j, i
                    l1, l2 = l2, l1
                else:
                    last_items = True

        return merged_list

    def process_query(self, query):
        """
        Computes the list of ids of all records containing at least one word
        from the given query.
        """
        lists = list()
        for word in re.split("\W+", query):
            word = word.lower()
            if any(word):
                if word in self.inverted_lists.keys():
                    lists.append(self.inverted_lists[word])

        print()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 inverted_index.py <file>")
        sys.exit()
    file_name = sys.argv[1]
    ii = InvertedIndex()
    ii.read_from_file(file_name)

    print(ii.inverted_lists)

    # ii.merge(ii.inverted_lists.items()[0][1], ii.inverted_lists.items()[2][1])

    ii.process_query('The third docum')

    # for word, inverted_list in ii.inverted_lists.items():
    #     print("%s %d" % (word, len(inverted_list)))
