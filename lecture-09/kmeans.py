"""
Copyright 2015 University of Freiburg
Hannah Bast <bast@cs.uni-freiburg.de>
Evgeny Anatskiy <evgeny.anatskiy@jupiter.uni-freiburg.de>
Numair Mansur <numair.mansur@gmail.com>
"""

import re
import sys
import random
import logging
from math import log
from time import time

import numpy as np
from scipy.sparse import csr_matrix

logging.basicConfig(format='%(asctime)s : %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


class Kmeans:
    """ Class for a simple inverted index. """

    def __init__(self):
        self.inverted_lists = dict()
        self.record_lengths = dict()
        self.terms = []
        self.n = 0      # Total number of records (documents) [Lines]
        self.m = 0      # Total number of terms
        self.A = None   # Term-document matrix

    def build_inverted_index(self, file_name):
        """
        Builds the inverted index from the given file.
        The format: one record per line.
        >>> ii = Kmeans()
        >>> ii.build_inverted_index('example.txt')
        >>> ii.terms
        ['internet', 'web', 'surfing', 'beach']
        >>> sorted(ii.inverted_lists.items())
        [('beach', {4: 1.0, 5: 1.0, 6: 1.0}), ('internet', {1: 1.0, 2: 1.0, \
4: 1.0}), ('surfing', {1: 0.2630344058337938, 2: 0.2630344058337938, \
3: 0.2630344058337938, 4: 0.334771061970283, 5: 0.2630344058337938}), \
('web', {1: 1.0, 3: 1.0, 4: 1.0})]
        """

        with open(file_name, 'r', encoding='utf-8') as file:
            doc_id = 0
            for line in file:
                doc_id += 1
                words = re.split('\W+', line)
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

            self.n = len(self.record_lengths)
            AVDL = sum(self.record_lengths.values()) / float(self.n)

            for term, inv_list in self.inverted_lists.items():
                for doc_id, tf in inv_list.items():
                    df = len(self.inverted_lists[term])
                    DL = self.record_lengths[doc_id]
                    self.inverted_lists[term][doc_id] = \
                        self.bm25_score(tf, df, self.n, AVDL, DL)

    def bm25_score(self, tf, df, N, AVDL, DL, bm25k=0.75, bm25b=0.0):
        return tf * (bm25k + 1) / (bm25k * (1 - bm25b + bm25b * DL / AVDL) +
                                   tf) * log((N / df), 2)

    def build_td_matrix(self, m=10000):
        """
        Computes the sparse term-document matrix using the (already built)
        inverted index.
        """
        terms = sorted(self.terms,
                       key=lambda t: len(self.inverted_lists[t]),
                       reverse=True)[:m]
        self.lsi_vocab = {t: i for i, t in enumerate(terms)}
        self.lsi_terms = terms
        row = []
        col = []
        values = []
        for i, t in enumerate(terms):
            for doc, score in self.inverted_lists[t]:
                row.append(i)
                col.append(doc - 1)
                values.append(score)
        self.A = csr_matrix((values, (row, col)), dtype=float)
        U, S, VT = svds(self.A, k)
        S = scipy.sparse.diags(S, 0)
        self.lsi_VT = VT
        self.lsi_U = U
        self.lsi_US = U * S
        self.lsi_m = m


    def initialize_centriods(self, k):
        '''
        Compute an m (# of terms) x k (# of clusters) matrix with the initial (random) centroids. Make sure that
        no two centroids are the same.
        '''
        # Randomly selects any K documents from the document vectors.
        rows = sorted(random.sample(range(self.n), k))
        cols = [i for i in range(k)]
        vals = [1 for _ in range(k)]
        return self.A * csr_matrix((vals, (rows, cols)), shape=(self.n, k))

    def compute_distances(self, centroids):
        '''
        Compute a k x n matrix such that the entry at i, j contains the distance
        between the i-th centroid and the j-th document. If the centroids and the
        documents are L2-normalized to 1, this can (and should) be done with a
        single matrix operation.
        '''
        return 2 * (1 - centroids.T * self.A)




    @staticmethod
    def norm_sp_row_l2(matrix):
        """ L2 normalize rows of a sparse csr_matrix.
        >>> m = np.matrix([[0, 1, 2], [0, 2, 3]], dtype=float)
        >>> m = csr_matrix(m)
        >>> Kmeans.norm_sp_row_l2(m)
        >>> m[0, 0]
        0.0
        >>> m[0, 1]
        0.44721359549995793
        >>> m[0, 2]
        0.89442719099991586
        >>> m[1, 0]
        0.0
        >>> m[1, 1]
        0.55470019622522915
        >>> m[1, 2]
        0.83205029433784372
        """
        sq = matrix.multiply(matrix)
        print(sq)
        row_sums = np.array(sq.sum(axis=1))[:, 0]
        print(row_sums)
        row_sums = np.sqrt(row_sums)
        print(row_sums)
        row_indices, col_indices = matrix.nonzero()
        print(row_indices)
        print(col_indices)
        print(matrix.data)
        print(row_sums[row_indices])
        matrix.data = matrix.data / row_sums[row_indices]




if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Usage: python3 kmeans.py <records_file>')
        sys.exit()

    k = Kmeans()
    file_name = sys.argv[1]
    logger.info('Building inverted index "%s"...' % file_name)
    k.build_inverted_index(file_name)
    logger.info('Computing term-document matrix A...')
    k.build_td_matrix()
    initial_centriods = k.initialize_centriods(3) # initialize centriods
    print("************************************************************")
    print("Term Document Matrix : ")
    print(k.A.todense())
    print()
    print("Randomly initialized centriods : ")
    print(initial_centriods.todense())
    print("L2 normalized sparse Term Document Matrix")
    k.norm_sp_row_l2(k.A)


    