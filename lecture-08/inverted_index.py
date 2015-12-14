"""
Copyright 2015 University of Freiburg
Hannah Bast <bast@cs.uni-freiburg.de>
Evgeny Anatskiy <evgeny.anatskiy@jupiter.uni-freiburg.de>
Numair Mansur <numair.mansur@gmail.com>
"""

import re
import sys
from math import log
from time import time
import numpy as np
import scipy.sparse
import scipy.sparse.linalg

from collections import OrderedDict


GREEN_CLR = '\033[32m'
YELLOW_CLR = '\033[33m'
PURPLE_CLR = '\033[35m'
END_CLR = '\033[0m'

# BM25 parameters
K = 0.75
B = 0.0


class EvaluateBenchmark:
    """ Class for evaluating a given benchmark. """

    def __init__(self, inv_lists):
        """
        Creates an empty dictionary of queries and their relevant movies ids,
        a list of pair with a movies id and its relevance according to the
        benchmark file and total sums for P@3, P@R and AP.
        """

        self.benchmark_ids = dict()
        self.res_relevance = list()
        self.ii = inv_lists
        self.sum_pa3 = 0
        self.sum_par = 0
        self.sum_ap = 0

    def precision_at_k(self, results_ids, relevant_ids, k):
        """
        Computes the P@k for the given result list and the given set of
        relevant docs.

        (Note: with our approach results_ids and relevant_ids are not needed as
        they were used before to generate the results_relevance list.)
        """
        return len([x for x in self.res_relevance[:k] if x[1] == 1]) / k

    def average_precision(self, results_ids, relevant_ids):
        """
        Computes the AP (average precision) of the given result list and the
        given set of relevant docs.
        """
        sum_p = 0

        r_list = [results_ids.index(x[0]) + 1
                  for x in self.res_relevance if x[1] == 1]

        # Taking into the consideration the note below on the Slide 22
        # (Lecture 2): "for docs not in the result list take P@Ri = 0"
        r_list_length = len(r_list)
        r_list_length += len(relevant_ids) - r_list_length

        for r in r_list:
            sum_p += self.precision_at_k(None, None, r)

        return sum_p / r_list_length

    def evaluate_benchmark(self, file_name):
        """ Evaluates the given benchmark. """

        with open(file_name, 'r', encoding='utf-8') as file:
            for line in file:
                splitted_line = line.replace('\n', '').split('\t')
                self.benchmark_ids[splitted_line[0]] = \
                    [int(x) for x in splitted_line[1].split(' ')]

        print('Calculating...')
        st = time()

        for query, relevant_ids in self.benchmark_ids.items():
            results_ids = [x[0] for x in self.ii.process_query(query)]

            self.res_relevance = [[res_id, 1 if res_id in relevant_ids else 0]
                                  for res_id in results_ids]

            self.sum_pa3 += self.precision_at_k(None, None, 3)
            self.sum_par += self.precision_at_k(None, None, len(relevant_ids))
            self.sum_ap += self.average_precision(results_ids, relevant_ids)

        num = len(self.benchmark_ids)
        print('\nMP@3: %s, MP@R: %s, MAP: %s' %
              (round(self.sum_pa3 / num, 2),
               round(self.sum_par / num, 2),
               round(self.sum_ap / num, 2)))
        print('K = %s, B = %s' % (K, B))
        print('\nCalculation time: %s s' % (round(time() - st, 2)))


class InvertedIndex:
    """ A simple inverted index as explained on the lecture. """

    def __init__(self):
        """ Creates an empty inverted index and additional dicts. """

        self.inverted_lists = dict()
        self.records = dict()
        self.record_lengths = dict()

        self.terms = []
        self.num_terms = 0
        self.num_docs = 0

        self.A = None

    def read_from_file(self, file_name):
        """
        Constructs the inverted index from the given file. The format is: one
        record per line.

        >>> ii = InvertedIndex()
        >>> ii.read_from_file('example.txt')
        >>> ii.num_terms, ii.num_docs
        (4, 6)
        >>> ii.terms
        ['internet', 'web', 'surfing', 'beach']
        >>> sorted(ii.inverted_lists.items())
        [('beach', [4, 5, 6]), ('internet', [1, 2, 4]), ('surfing', \
[1, 2, 3, 4, 4, 5, 6]), ('web', [1, 3, 4])]
        """

        with open(file_name, 'r', encoding='utf-8') as file:
            doc_id = 0
            for line in file:
                doc_id += 1
                words = re.split("\W+", line)
                self.records[doc_id] = line.replace('\n', '')
                self.record_lengths[doc_id] = len(words)
                for term in words:
                    term = term.lower()
                    if any(term):
                        """ If a word is seen for first time, create an empty
                        inverted list for it. """
                        if term not in self.inverted_lists:
                            self.terms.append(term)
                            self.inverted_lists[term] = dict()

                        if doc_id in self.inverted_lists[term].keys():
                            self.inverted_lists[term][doc_id] += 1
                        else:
                            self.inverted_lists[term][doc_id] = 1
            self.num_docs = doc_id
            self.num_terms = len(self.inverted_lists)

            st = time()
            N = self.num_docs
            AVDL = sum(self.record_lengths.values()) / float(N)
            for term, inv_lists in self.inverted_lists.items():
                for doc_id, tf in inv_lists.items():
                    df = len(self.inverted_lists[term])
                    DL = self.record_lengths[doc_id]
                    self.inverted_lists[term][doc_id] = \
                        self.bm25_score(tf, df, N, AVDL, DL)
            print('Calculating BM25 scores: {0:.2f} s\n'.format(time() - st))

            self.preprocessing_vsm(2, 3)
            result = self.process_query_vsm('web surfing')

            print('!')

    def bm25_score(self, tf, df, N, AVDL, DL):
        return tf * (K + 1) / (K * (1 - B + B * DL / AVDL) + tf) * \
            log((N / df), 2)

    def preprocessing_vsm(self, k, m):
        """
        Computes the sparse term-document matrix using the (already built)
        inverted index. For LSI it also performs SVD using dimensionality k and
        only the most frequent terms m. Intermediate results are stored as
        members of this class.
        """
        # inv_lists_sorted = OrderedDict(sorted(self.inverted_lists.items(),
        #                                       key=lambda x: len(x[1]),
        #                                       reverse=True)[:m])
        term_id = 0
        nz_vals, row_inds, col_inds = [], [], []
        # for term, inv_list in inv_lists_sorted.items():
        for term, inv_list in self.inverted_lists.items():
            for doc_id, value in inv_list.items():
                if value != 0.0:
                    nz_vals.append(value)
                    row_inds.append(term_id)
                    col_inds.append(doc_id - 1)
            term_id += 1
        self.A = scipy.sparse.csr_matrix((nz_vals, (row_inds, col_inds)),
                                         dtype=float)

        inv_lists_sorted = OrderedDict(sorted(self.inverted_lists.items(),
                                              key=lambda x: len(x[1]),
                                              reverse=True)[:m])
        term_id = 0
        nz_vals, row_inds, col_inds = [], [], []
        for term, inv_list in inv_lists_sorted.items():

        U, S, V = scipy.sparse.linalg.svds(self.A, k)
        S = np.diag(S)
        Uk = U[:, 0:k]
        Sk = S[0:k, 0:k]
        Vk = V[0:k, :]
        Ak = Uk.dot(Sk).dot(Vk)
        print('!')


    def process_query_vsm(self, query):
        """
        Executes the query using the (full) term-document matrix in the vsm.
        """
        keywords = [word.lower() for word in re.split("\W+", query)]
        q = scipy.sparse.csr_matrix([1 if term in keywords else 0
                                  for term in self.inverted_lists.keys()])

        result = q.dot(self.A)
        return sorted(list(zip(result.indices + 1, result.data)),
                      key=lambda x: x[1], reverse=True)

    def process_query_lsi(self, query, lmbda):
        """
        Executes the query by mapping the query vector to latent space.
        """
        pass

    def related_term_pairs(self):
        """
        Computes the term-term association matrix T.
        """
        pass

    def merge(self, l1, l2):
        """
        Merges two given inverted lists

        >>> ii = InvertedIndex()
        >>> l1 = [[1, 1], [3, 2], [4, 1], [6, 1]]
        >>> l2 = [[2, 1], [3, 1], [5, 1], [7, 2]]
        >>> ii.merge(l1, l2)
        [[1, 1], [2, 1], [3, 3], [4, 1], [5, 1], [6, 1], [7, 2]]
        """
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

    def process_query(self, query):
        """
        Computes the list of ids of all records containing at least one word
        from the given query.

        >>> ii = InvertedIndex()
        >>> file_name = ii.read_from_file('example.txt')
        >>> ii.process_query('internet')
        [[1, 1.0], [2, 1.0], [4, 1.0]]
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

if __name__ == "__main__":
    if len(sys.argv) < 2 or \
            (len(sys.argv) == 3 and sys.argv[2] == '--benchmark') or \
            (len(sys.argv) == 4 and sys.argv[2] != '--benchmark'):
        msg = 'Usage: \n\tpython3 inverted_index.py <file>' + \
          '\n\tpython3 inverted_index.py <file> --benchmark ' + \
          '<benchmark_file>'
        print(msg)
        sys.exit()

    ii = InvertedIndex()
    file_name = sys.argv[1]
    print('Loading...\n')
    ii.read_from_file(file_name)

    if len(sys.argv) > 3 and sys.argv[2] == '--benchmark':
        eb = EvaluateBenchmark(ii)
        eb.evaluate_benchmark(sys.argv[3])
    else:
        while True:
            msg = PURPLE_CLR + \
                '> Enter the query (type "exit" for quitting): ' + END_CLR
            query = input(msg)
            if query == 'exit':
                break

            print('')

            hits = ii.process_query(query)
            if any(hits):
                ii.print_output(hits[:3], query)
            else:
                print('No hits')
