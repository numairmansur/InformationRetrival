"""
Copyright 2015 University of Freiburg
Hannah Bast <bast@cs.uni-freiburg.de>
Evgeny Anatskiy <evgeny.anatskiy@jupiter.uni-freiburg.de>
Numair Mansur <numair.mansur@gmail.com>
"""

import re
import sys

from time import time


GREEN_CLR = '\033[32m'
PURPLE_CLR = '\033[35m'
END_CLR = '\033[0m'


class QgramIndex:
    """ A simple q-gram index as explained on the lecture. """

    def __init__(self, q):
        """ Create an empty q-gram index. """

        self.inverted_lists = dict()
        self.records = dict()
        self.q = q

    def read_from_file(self, file_name):
        """
        Construct index from the given file. The format is one record per line.

        >>> qi = QgramIndex(3)
        >>> qi.read_from_file('example.txt')
        >>> sorted(qi.inverted_lists.items())
        [('$$a', {2: 1}), ('$$b', {1: 1, 3: 1}), ('$an', {2: 1}), ('$ba', \
{1: 1, 3: 1}), ('ako', {3: 1}), ('ana', {1: 1, 2: 1, 3: 2}), ('ban', {1: 1, \
3: 1}), ('kon', {3: 1}), ('nak', {3: 1}), ('nan', {3: 1}), ('ong', {3: 1})]
        """

        with open(file_name, 'r', encoding='utf-8') as file:
            record_id = 0
            for record in file:
                record_id += 1
                normlzd = re.sub('\W+', '', record).lower()
                self.records[record_id] = (record.replace('\n', ''), normlzd)
                for qgram in self.qgrams(normlzd):
                    if len(qgram) > 0:
                        # If q-gram is seen for first time, create an empty
                        # inverted list for it. """
                        if qgram not in self.inverted_lists:
                            self.inverted_lists[qgram] = dict()

                        if record_id in self.inverted_lists[qgram].keys():
                            self.inverted_lists[qgram][record_id] += 1
                        else:
                            self.inverted_lists[qgram][record_id] = 1

    def qgrams(self, record):
        """ All q-grams of the given record.

        >>> qi = QgramIndex(3)
        >>> qi.qgrams("bana")
        ['$$b', '$ba', 'ban', 'ana']
        """

        record = "$" * (self.q - 1) + record
        return [record[i:i+self.q] for i in range(0, len(record) - self.q + 1)]

    @staticmethod
    def merge(lists):
        """ Merge the q-gram index lists and return a list of tuples (record_id,
        count).

        >>> QgramIndex.merge([[[1, 1], [2, 1], [3, 1]], [[2, 1], [3, 1], \
[4, 1]], [[3, 1], [4, 1], [5, 1]]])
        [[1, 1], [2, 2], [3, 3], [4, 2], [5, 1]]
        """

        merged_list = list()
        for l2 in lists:
            l1 = merged_list
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

    @staticmethod
    def compute_ped(p, s):
        """ Compute the prefix edit distance PED(p, s).

        >>> QgramIndex.compute_ped("shwartz", "schwarzenegger")
        2
        """

        n, m = len(p), len(s)
        bound = m + 1

        current_row = list(range(bound))
        for i in list(range(1, n + 1)):
            previous_row = current_row
            current_row = [i] + [0] * (bound - 1)
            for j in list(range(1, bound)):
                insert = previous_row[j] + 1
                delete = current_row[j - 1] + 1
                replace = previous_row[j - 1]
                if s[j - 1] != p[i - 1]:
                    replace += 1
                current_row[j] = min(insert, delete, replace)

        return min(current_row)

    def find_matches(self, prefix, delta, k=5, use_qindex=True):
        """ Find all matches for the given prefix with PED at most delta. Return
        the top-k matches.

        >>> qi = QgramIndex(3)
        >>> qi.read_from_file('example.txt')
        >>> qi.find_matches('ba', 0, use_qindex=True)
        #PEDs Q: 2
        [(1, 'bana.', 0), (3, 'banana Kong!', 0)]

        >>> qi.find_matches('ba', 0, use_qindex=False)
        [(1, 'bana.', 0), (3, 'banana Kong!', 0)]
        """

        result = list()

        if use_qindex:
            # Compute the PED only for candidate matches (default)

            all_qgrams = self.inverted_lists.keys()
            lists = [sorted(list(
                zip(self.inverted_lists[qgram].keys(),
                    self.inverted_lists[qgram].values())
            )) for qgram in self.qgrams(prefix) if qgram in all_qgrams]

            ped_count = 0
            for lst in self.merge(lists):
                if lst[1] >= len(prefix) - self.q * delta:
                    ped = self.compute_ped(prefix, self.records[lst[0]][1])
                    ped_count += 1
                    if ped <= delta:
                        result.append((lst[0], self.records[lst[0]][0], ped))
            print('#PEDs Q: %d' % ped_count)

        else:
            # Compute the PED for all records (baseline)
            for record_id, record in self.records.items():
                ped = self.compute_ped(prefix, record[1])
                if ped <= delta:
                    result.append((record_id, record[0], ped))

        return sorted(result, key=lambda x: x[2])[:k]


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python3 qgram_index.py <file>')
        sys.exit()

    file_name = sys.argv[1]
    qi = QgramIndex(3)
    qi.read_from_file(file_name)

    while True:
        msg = PURPLE_CLR + \
            '> Enter the query (type "exit" for quitting): ' + END_CLR
        query = input(msg)
        if query == 'exit':
            break

        idx = input(PURPLE_CLR + '> Use q-Gram Index? (y/n): ' + END_CLR)
        use_index = True if idx == 'y' else False

        normalized_query = re.sub('\W+', '', query).lower()
        delta = len(normalized_query) // 4

        st = time()
        hits = qi.find_matches(normalized_query, delta, use_qindex=use_index)
        if use_index:
            print('Time Q: %s s\n' % (time() - st))
        else:
            print('Time B: %s s\n' % (time() - st))

        if any(hits):
            for hit in hits:
                print(GREEN_CLR + '< ' + qi.records[hit[0]][0] + END_CLR)
        else:
            print('No hits')
        print()
