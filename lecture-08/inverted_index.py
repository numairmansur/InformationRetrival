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
bm25k = 0.75
bm25b = 0.0
lmbda = 0.6


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

        print('Benchmark evaluation...')
        st = time()

        for query, relevant_ids in self.benchmark_ids.items():
            # BM25 (VSM)
            res_ids = [x[0] for x in self.ii.process_query_vsm(query)]

            # LSI
            # res_ids = [x[0]
            #            for x in self.ii.process_query_lsi(query,\
            # lmbda, True)]

            # BM25 + LSI
            # res_ids = [x[0] for x in self.ii.process_query_lsi(query, lmbda)]

            self.res_relevance = [[res_id, 1 if res_id in relevant_ids else 0]
                                  for res_id in res_ids]

            self.sum_pa3 += self.precision_at_k(None, None, 3)
            self.sum_par += self.precision_at_k(None, None, len(relevant_ids))
            self.sum_ap += self.average_precision(res_ids, relevant_ids)

        num = len(self.benchmark_ids)
        print('\nMP@3: %s, MP@R: %s, MAP: %s' %
              (round(self.sum_pa3 / num, 2),
               round(self.sum_par / num, 2),
               round(self.sum_ap / num, 2)))
        print('K = %s, B = %s' % (bm25k, bm25b))
        print('\nEvaluation time: %s s' % (round(time() - st, 2)))


class InvertedIndex:
    """ A simple inverted index as explained on the lecture. """

    def __init__(self):
        """ Creates an empty inverted index and additional dicts. """

        self.inverted_lists = dict()
        self.inv_lists_sorted = dict()
        self.records = dict()
        self.record_lengths = dict()

        self.terms = []
        self.num_terms = 0
        self.num_docs = 0

        self.A = None
        self.Uk = None
        self.Sk = None
        self.Vk = None

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
        [('beach', {4: 1, 5: 1, 6: 1}), ('internet', {1: 1, 2: 1, 4: 1}), \
('surfing', {1: 1, 2: 1, 3: 1, 4: 2, 5: 1}), ('web', {1: 1, 3: 1, 4: 1})]

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
                        # If a word is seen for the first time, create an empty
                        # inverted list for it
                        if term not in self.inverted_lists:
                            self.terms.append(term)
                            self.inverted_lists[term] = dict()

                        if doc_id in self.inverted_lists[term].keys():
                            self.inverted_lists[term][doc_id] += 1
                        else:
                            self.inverted_lists[term][doc_id] = 1
            self.num_docs = doc_id
            self.num_terms = len(self.inverted_lists)

    def bm25_score(self, tf, df, N, AVDL, DL):
        return tf * (bm25k + 1) / (bm25k * (1 - bm25b + bm25b * DL / AVDL) +
                                   tf) * log((N / df), 2)

    def preprocessing_vsm(self, k, m):
        """
        Computes the sparse term-document matrix using the (already built)
        inverted index. For LSI it also performs SVD using dimensionality k and
        only the most frequent terms m. Intermediate results are stored as
        members of this class.
        """
        self.inv_lists_sorted = OrderedDict(sorted(self.inverted_lists.items(),
                                                   key=lambda x: len(x[1]),
                                                   reverse=True)[:m])
        N = self.num_docs
        AVDL = sum(self.record_lengths.values()) / float(N)

        term_id = 0
        nz_vals, row_inds, col_inds = [], [], []

        for term, inv_list in self.inv_lists_sorted.items():
            for doc_id, tf in inv_list.items():
                df = len(self.inv_lists_sorted[term])
                DL = self.record_lengths[doc_id]
                self.inv_lists_sorted[term][doc_id] = \
                    self.bm25_score(tf, df, N, AVDL, DL)
            nz_vals += [v for v in self.inv_lists_sorted[term].values()
                        if v != 0]
            row_inds += [term_id] * len(self.inv_lists_sorted[term])
            col_inds += [id - 1 for id, v in
                         self.inv_lists_sorted[term].items() if v != 0]
            term_id += 1
        self.A = scipy.sparse.csr_matrix((nz_vals, (row_inds, col_inds)),
                                         dtype=float)
        # LSI
        self.Uk, Sk, self.Vk = scipy.sparse.linalg.svds(self.A, k)
        self.Sk = np.diag(Sk)

    def process_query_vsm(self, query):
        """
        Executes the query using the (full) term-document matrix in the vsm.
        """
        keywords = [word.lower() for word in re.split("\W+", query)]
        q = scipy.sparse.csr_matrix([1 if term in keywords else 0
                                     for term in self.inv_lists_sorted.keys()])

        scores = q.dot(self.A)
        return sorted(list(zip(scores.indices + 1, scores.data)),
                      key=lambda x: x[1], reverse=True)

    def process_query_lsi(self, query, lmbda, only_lsi=False):
        """
        Executes the query by mapping the query vector to latent space.
        """
        keywords = [word.lower() for word in re.split("\W+", query)]
        q = np.array([1 if term in keywords else 0
                      for term in self.inv_lists_sorted.keys()])
        qk = q.dot(self.Uk).dot(self.Sk)

        scores = qk.dot(self.Vk) if only_lsi \
            else lmbda * np.transpose(q) * self.A + (1 - lmbda) * \
            np.transpose(qk).dot(self.Vk)

        return sorted(list(zip([i + 1 for i in range(0, scores.size)],
                               scores)),
                      key=lambda x: x[1], reverse=True)

    def related_term_pairs(self):
        """
        Computes the term-term association matrix T.
        """

        T = self.Uk.dot(np.transpose(self.Uk))
        term_dict = {idx: term
                     for idx, term in enumerate(self.inv_lists_sorted.keys())}

        added = set()
        np.fill_diagonal(T, 0)
        max_values = sorted([((i, t.argmax()), t[t.argmax()])
                             for i, t in enumerate(T)],
                            key=lambda x: x[1], reverse=True)
        max_values = [item for item in max_values
                      if item[1] not in added and not added.add(item[1])]

        # for pair in max_values[:50]:
        #     print('{0:15} {1:15} {2:2f}'.format(term_dict[pair[0][0]],
        #                                      term_dict[pair[0][1]], pair[1]))

        with open('term_pairs.txt', 'w') as f:
            for pair in max_values[:50]:
                f.write('%s\t%s\t%f\n' % (term_dict[pair[0][0]],
                                          term_dict[pair[0][1]], pair[1]))

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
    if len(sys.argv) < 4 or \
            (len(sys.argv) == 5 and sys.argv[4] == '--benchmark') or \
            (len(sys.argv) == 6 and sys.argv[4] != '--benchmark'):
        msg = 'Usage: \n\tpython3 inverted_index.py <file> <k> <m>' + \
              '\n\tpython3 inverted_index.py <file> <k> <m> --benchmark ' + \
              '<benchmark_file>'
        print(msg)
        sys.exit()

    ii = InvertedIndex()
    file_name = sys.argv[1]
    k = int(sys.argv[2])
    m = int(sys.argv[3])
    print('Loading movies file...')
    ii.read_from_file(file_name)
    print('Preprocessing...\n')
    ii.preprocessing_vsm(k, m)

    # ii.related_term_pairs()

    if len(sys.argv) > 5 and sys.argv[4] == '--benchmark':
        eb = EvaluateBenchmark(ii)
        eb.evaluate_benchmark(sys.argv[5])
    else:
        while True:
            msg = PURPLE_CLR + \
                '> Enter the query (type "exit" for quitting): ' + END_CLR
            query = input(msg)
            if query == 'exit':
                break

            print('')

            hits = ii.process_query_vsm(query)
            # hits = ii.process_query_lsi(query, lmbda)
            # hits = ii.process_query_lsi(query, lmbda, only_lsi=True)
            if any(hits):
                ii.print_output(hits[:3], query)
            else:
                print('No hits')
