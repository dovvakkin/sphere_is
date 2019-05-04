# -*- coding: utf-8 -*-
import sys
import numpy as np
reload(sys)
sys.setdefaultencoding('utf8')
import json

EMPTY_LEX = "~"


class ErrorModel:
    def __init__(self):
        self.un_statistics = dict()  # {"origin" : {"fix" : number}}
        self._un_statistics_size = 0
        self.bin_statistics = dict()  # {"o1" : {"o2" : {"f1" : {"f2" : number}}}}
        self._bin_statistics_size = 0

    def load_json(self, json_path):
        (size, stat) = json.loads(open(json_path, "r").read())
        self._un_statistics_size, self.un_statistics = size, stat

    def store_json(self, json_path):
        file = open(json_path, "w")
        file.write(json.dumps((self._un_statistics_size, self.un_statistics)))
        file.close()

    def fit(self, a, b):
        levenshtein_matrix = self._get_levenshtein_matrix(a, b)
        self._fill_statistics(a, b, levenshtein_matrix)

    def fit_all(self, file_name):
        def split_line(line):
            line = line.lower()
            #TODO line = "".join(str(c) for c in line if ('a' <= c <= 'z') or ('а' <= c <= 'я') or c == ' ')
            words = line.split(" ")
            return words

        with open(file_name) as f:
            for line in f:
                tab_ind = line.find('\t')
                if tab_ind != -1:
                    orig = line[:tab_ind]
                    fix = line[tab_ind+1:]

                    split_orig = split_line(orig)
                    split_fix = split_line(fix)
                    if len(split_orig) == len(split_fix):
                        for i in range(len(split_orig)):
                            self.fit(split_orig[i], split_fix[i])
        self._prichesat_statistiku()

    def _prichesat_statistiku(self):
        for orig in self.un_statistics.keys():
            for fix in self.un_statistics[orig].keys():
                self.un_statistics[orig][fix] /= self._un_statistics_size

        for o_f in self.bin_statistics.keys():
            for o_s in self.bin_statistics.keys():
                for f_f in self.bin_statistics.keys():
                    for f_s in self.bin_statistics.keys():
                        self.bin_statistics[o_f][o_s][f_f][f_s] /= self._bin_statistics_size

    # TODO count with 2gram
    def get_weighted_distance(self, a, b):
        n, m = len(a), len(b)
        if n > m:
            # Make sure n <= m, to use O(min(n,m)) space
            a, b = b, a
            n, m = m, n

        current_row = list(range(n + 1))  # Keep current and previous row, not entire matrix
        # matrix = np.array([current_row])
        for i in range(1, m + 1):
            previous_row, current_row = current_row, [i] + [0] * n
            for j in range(1, n + 1):
                add, delete, change = (previous_row[j] + 1) / self._get_un_statistics(EMPTY_LEX, b[i - 1]), \
                                      (current_row[j - 1] + 1) / self._get_un_statistics(a[j - 1], EMPTY_LEX), \
                                      (previous_row[j - 1] + int(a[j - 1] != b[i - 1])) / self._get_un_statistics(a[j - 1],
                                                                                                                  b[i - 1])
                current_row[j] = min(add, delete, change)
            # matrix = np.vstack((matrix, [current_row]))
        return current_row[n]

    def _get_un_statistics(self, orig, fit):
        if orig in self.un_statistics and fit in self.un_statistics[orig]:
            return self.un_statistics[orig][fit]
        return 0.5 / self._un_statistics_size  # newer sow this case

    def _get_bin_statistics(self, o_f, o_s, f_f, f_s):
        if o_f in self.bin_statistics:
            if o_s in self.bin_statistics[o_f]:
                if f_f in self.bin_statistics[o_s]:
                    if f_s in self.bin_statistics[f_f]:
                        return self.bin_statistics[o_f][o_s][f_f][f_s]
        return 0.5 / self._bin_statistics_size

    def _add_un_statistics(self, orig, fix):
        self.un_statistics.setdefault(orig, dict())
        self.un_statistics[orig].setdefault(fix, 0)
        self.un_statistics[orig][fix] += 1
        self._un_statistics_size += 1

    def _add_bin_statistics(self, orig_first, orig_second, fix_first, fix_second):
        print "{}{} -> {}{}".format(orig_first, orig_second, fix_first, fix_second)
        self.bin_statistics.setdefault(orig_first, dict())
        self.bin_statistics[orig_first].setdefault(orig_second, dict())
        self.bin_statistics[orig_first][orig_second].setdefault(fix_first, dict())
        self.bin_statistics[orig_first][orig_second][fix_first].setdefault(fix_second, 0)
        self.bin_statistics[orig_first][orig_second][fix_first][fix_second] += 1
        self._bin_statistics_size += 1


    def _fill_statistics(self, a, b, matrix):
        n, m = len(a), len(b)

        a_prev = ""
        b_prev = ""
        position = [n, m, matrix[m, n]]  # [x, y, distance]
        while position[2] != 0:  # пока position не придет в правый нижний угол
            x, y = position[0], position[1]

            possible_actions = [matrix[y - 1][x - 1],  # change
                                matrix[y - 1][x],  # add
                                matrix[y][x - 1]]  # delete
            action = np.argmin(possible_actions)

            if action == 0:  # change
                if position[2] != possible_actions[action.item()]:
                    position[2] -= 1

                    if not a_prev:
                        a_prev = a[x - 1]
                        b_prev = b[y - 1]
                    else:
                        self._add_bin_statistics(a_prev, a[x - 1], b_prev, b[x - 1])
                        a_prev = a[x - 1]
                        b_prev = b[y - 1]

                    self._add_un_statistics(a[x - 1], b[y - 1])
                    # print(a[x - 1] + " -> " + b[y - 1])
                position[0] -= 1
                position[1] -= 1
            elif action == 1:  # add
                if position[2] != possible_actions[action.item()]:
                    position[2] -= 1

                    if not a_prev:
                        a_prev = a[x - 1]
                        b_prev = b[y - 1]
                    else:
                        self._add_bin_statistics(a_prev, EMPTY_LEX, b_prev, b[x - 1])
                        a_prev = a[x - 1]
                        b_prev = b[y - 1]

                    self._add_un_statistics(EMPTY_LEX, b[y - 1])
                    # print("~ -> " + b[y - 1])
                position[1] -= 1
            else:  # delete
                if position[2] != possible_actions[action.item()]:
                    position[2] -= 1

                    if not a_prev:
                        a_prev = a[x - 1]
                        b_prev = b[y - 1]
                    else:
                        self._add_bin_statistics(a_prev, a[x - 1], b_prev, EMPTY_LEX)
                        a_prev = a[x - 1]
                        b_prev = b[y - 1]

                    self._add_un_statistics(a[x - 1], EMPTY_LEX)
                    # print(a[x - 1] + " -> ~")
                position[0] -= 1

    @staticmethod
    def _get_levenshtein_matrix(a, b):
        n, m = len(a), len(b)
        inverse = False
        if n > m:
            # Make sure n <= m, to use O(min(n,m)) space
            a, b = b, a
            n, m = m, n
            inverse = True

        current_row = list(range(n + 1))  # Keep current and previous row, not entire matrix
        matrix = np.array([current_row])
        for i in range(1, m + 1):
            previous_row, current_row = current_row, [i] + [0] * n
            for j in range(1, n + 1):
                add, delete, change = previous_row[j] + 1, \
                                      current_row[j - 1] + 1, \
                                      previous_row[j - 1] + int(a[j - 1] != b[i - 1])
                current_row[j] = min(add, delete, change)
            matrix = np.vstack((matrix, [current_row]))
        return matrix if not inverse else matrix.T

#
# # represent word as bigrams
# def bi_symbols(string):
#     if not string:
#         return ["^_"]
#     new_string = ["^" + string[0]]
#     for i in range(len(string) - 1):
#         new_string += [string[i:i + 2]]
#     new_string += [string[-1:] + "_"]
#     return new_string

em = ErrorModel()

f = open("test.txt", "w")
f.write("кшка сабака\tкошка собака")
f.close()

em.fit_all("test.txt")