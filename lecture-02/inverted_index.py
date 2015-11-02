"""
Copyright 2015 University of Freiburg
Hannah Bast <bast@cs.uni-freiburg.de>
"""

import re
import sys
from math import log

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
        self.record_lengths = dict()

    def read_from_file(self, file_name):
        """
        Construct inverted index from given file. The format is one record per
        line.

        >>> ii = InvertedIndex()
        >>> ii.read_from_file("example.txt")
        >>> sorted(ii.inverted_lists.items())
        [('doc', {1: 1, 2: 1, 3: 1}), ('first', {1: 1}), ('second', {2: 1})]
        """

        with open(file_name, 'r', encoding='utf-8') as file:
            doc_id = 0
            for line in file:
                doc_id += 1
                words = re.split("\W+", line)
                self.records[doc_id] = line.replace('\n', '')
                self.record_lengths[doc_id] = len(words)
                for word in words:
                    word = word.lower()
                    if any(word):
                        """ If a word is seen for first time, create an empty
                        inverted list for it. """
                        if word not in self.inverted_lists:
                            self.inverted_lists[word] = dict()

                        if doc_id in self.inverted_lists[word].keys():
                            self.inverted_lists[word][doc_id] += 1
                        else:
                            self.inverted_lists[word][doc_id] = 1

    def merge(self, l1, l2):
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
            merged_list.extend(l1[i:])
        if j < len(l2):
            merged_list.extend(l2[j:])

        return merged_list

    def bm25_score(self, tf, df, N, AVDL, DL):
        k = 1.75
        b = 0.75
        return tf * (k + 1) / (k * (1 - b + b * DL / AVDL) + tf) * \
            log((N / df), 2)

    def process_query(self, query):
        """
        Computes the list of ids of all records containing at least one word
        from the given query.

        >>> ii = InvertedIndex()
        >>> file_name = ii.read_from_file('example.txt')
        >>> ii.process_query('first')
        [[1, 1.4957286870076327]]
        """
        lists = list()
        merged_list = list()

        N = len(self.record_lengths)
        AVDL = sum(self.record_lengths.values()) / float(N)

        for word in re.split("\W+", query):
            word = word.lower()
            if any(word):
                if word in self.inverted_lists.keys():
                    for record_id, tf in self.inverted_lists[word].items():
                        df = len(self.inverted_lists[word])
                        DL = self.record_lengths[record_id]
                        self.inverted_lists[word][record_id] = \
                            self.bm25_score(tf, df, N, AVDL, DL)

                    inv_list = [[x, self.inverted_lists[word][x]]
                                for x in self.inverted_lists[word]]
                    lists.append(sorted(inv_list, key=lambda x: x[0]))

        for i in range(len(lists)):
            merged_list = self.merge(merged_list, lists[i])

        return sorted(merged_list, key=lambda x: x[1], reverse=True)

    def print_output(self, hits, query):
        for hit in hits:
            record = self.records[hit[0]].split('\t')
            title = record[0]

            print(GREEN_CLR + title + END_CLR)

            keywords = [word.lower() for word in re.split("\W+", query)]
            description = record[0] if len(record) == 1 \
                else record[1]

            # Keywords highlighting
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
        print('Loading...\n')
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
