"""
Copyright 2015 University of Freiburg
Hannah Bast <bast@cs.uni-freiburg.de>
"""

import re
import sys

from collections import Counter

GREEN_CLR = '\033[32m'
YELLOW_CLR = '\033[33m'
PURPLE_CLR = '\033[35m'
END_CLR = '\033[0m'


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

        print('Loading...\n')

        with open(file_name, 'r', encoding='utf-8') as file:
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

        merged_list = list()
        i, j = 0, 0

        while i < len(l1) and j < len(l2):
            if l1[i] < l2[j]:
                merged_list.append(l1[i])
                i += 1
            else:
                merged_list.append(l2[j])
                j += 1

        if i < len(l1):
            merged_list.extend(l1[i:])
        if j < len(l2):
            merged_list.extend(l2[j:])

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

        list_of_pairs = Counter(merged_list).most_common()

        return list_of_pairs

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
        """ The main method """
        if len(sys.argv) != 2:
            print('Usage: python3 inverted_index.py <file>')
            sys.exit()

        file_name = sys.argv[1]
        self.read_from_file(file_name)

        while True:
            msg = PURPLE_CLR + \
                '> Enter the query (type "exit" for quitting): ' + END_CLR
            query = input(msg)
            if query == 'exit':
                break

            print('')

            hits = ii.process_query(query)
            if any(hits):
                self.print_output(hits[:3], query)
            else:
                print('No hits')


if __name__ == "__main__":
    ii = InvertedIndex()
    ii.main()
