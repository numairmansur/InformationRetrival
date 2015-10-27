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
        self.records = dict()

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
                self.records[doc_id] = line.replace('\n', '')
                for word in re.split("\W+", line):
                    word = word.lower()
                    if len(word) > 0:
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
        l1.append('end')
        l2.append('end')
        i, j = 0, 0

        while l1[i] != 'end' or l2[j] != 'end':
            if l1[i] != 'end' and l2[j] != 'end' and l1[i] < l2[j]:
                merged_list.append(l1[i])
                i += 1

            elif l1[i] != 'end' and l2[j] != 'end' and l1[i] > l2[j]:
                merged_list.append(l2[j])
                j += 1

            elif l1[i] != 'end' and l2[j] != 'end' and l1[i] == l2[j]:
                merged_list.append(l1[i])
                merged_list.append(l2[j])
                i += 1
                j += 1

            elif l1[i] == 'end':
                merged_list.append(l2[j])
                j += 1

            elif l2[j] == 'end':
                merged_list.append(l1[i])
                i += 1

            else:
                print('Error while merging lists')

        return merged_list

    def process_query(self, query):
        """
        Computes the list of ids of all records containing at least one word
        from the given query.

        >>> ii = InvertedIndex()
        >>> file_name = ii.read_from_file('example.txt')
        >>> ii.process_query('third docum')
        [[3, 2], [1, 1], [2, 1]]
        """
        lists = list()
        merged_list = list()

        for word in re.split("\W+", query):
            word = word.lower()
            if any(word):
                if word in self.inverted_lists.keys():
                    lists.append(list(self.inverted_lists[word]))

        for i in range(len(lists)):
            merged_list = self.merge(merged_list, lists[i])

        list_of_pairs = [[record_id, merged_list.count(record_id)]
                         for record_id in sorted(set(merged_list))]

        list_of_pairs = sorted(list_of_pairs, key=lambda x: x[1], reverse=True)

        return list_of_pairs

    def print_output(self, hits):
        for hit in hits:
            record_title = self.records[hit[0]].split('\t')[0]
            print('%s (# of keywords occurrences: %s)' %
                  ('\033[92m' + record_title + '\033[0m', hit[1]))
        print('\n')

    def main(self):
        """ The main method """
        if len(sys.argv) != 2:
            print('Usage: python3 inverted_index.py <file>')
            sys.exit()

        file_name = sys.argv[1]
        self.read_from_file(file_name)

        while True:
            query = input('Enter the query (type "exit" for quitting): ')
            if query == 'exit':
                break

            hits = ii.process_query(query)
            if any(hits):
                self.print_output(hits[:3])
            else:
                print('No hits')


if __name__ == "__main__":
    ii = InvertedIndex()
    ii.main()
