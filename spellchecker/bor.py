# -*- coding: utf-8 -*-
import json
import pickle
import sys
import numpy as np
import copy
import time

MAX_DELETE = 2

MAX_INSERT = 2


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print('\n%r  %2.2f ms' % \
                  (method.__name__, (te - ts) * 1000))
        return result

    return timed


class TreeItself:
    def __init__(self):
        self.lit = "~"  # literal of current node
        self.is_word_end = False  # is there words ends in this node
        self.children = {}


class BORtree:
    def __init__(self, bin_stats, default_prob):
        self.root = TreeItself()
        self.root.lit = "^"
        self.bin_stats = bin_stats  # {2gram : {f_f : {f_s : prob}}}
        self.default_prob = default_prob

    def store_tree(self):
        with open("tree_root.pickle", "wb") as f:
            pickle.dump(self.root, f)
        with open("tree.json", "w") as f:
            f.write(json.dumps((self.bin_stats, self.default_prob)))

    def load_tree(self):
        with open("tree_root.pickle", "rb") as f:
            self.root = pickle.load(f)
        with open("tree.json", "r") as f:
            self.bin_stats, self.default_prob = json.loads(f.read())

    def fill_BORtree(self, set_of_words):
        def add_word_to_bor(literals, bor):
            lt = literals.pop(0)
            if lt not in bor.children:
                bor.children[lt] = TreeItself()

            bor.children[lt].is_word_end = (not literals) or bor.children[lt].is_word_end
            bor.children[lt].lit = lt

            if literals:
                add_word_to_bor(copy.deepcopy(literals), bor.children[lt])

        for word in set_of_words:
            literals = list(word)
            if literals:
                add_word_to_bor(copy.deepcopy(literals), self.root)

    def print_tree(self):
        def go_down(node, res):
            if node.is_word_end:
                result[res + node.lit] = 1
            for child in node.children:
                go_down(node.children[child], res + child)

        result = {}
        go_down(self.root, "")
        for word in result:
            print(word)

    def is_in_tree(self, word):
        def go_down(node, word_as_list):
            if word_as_list:
                c = word_as_list.pop(0)
                if c in node.children:
                    return go_down(node.children[c], word_as_list)
                else:
                    return False
            else:
                return node.is_word_end

        return go_down(self.root, list(word))

    # sorted(a.items(), key=lambda kv: (kv[1], kv[0]))
    @timeit
    # TODO dynamic threshold
    def indistrinct_search(self, word, threshold=1500):
        def go_down(node, word_as_list, res, err, deleted, inserted):
            if word_as_list:
                c = word_as_list.pop(0)
                if err < threshold:
                    bigram = node.lit + c
                    # insert
                    if inserted < MAX_INSERT:
                        if node.lit + "~" in self.bin_stats:
                            for child in node.children:
                                if node.lit + child in self.bin_stats[node.lit + "~"]:
                                    word_as_list.insert(0, c)
                                    appended = copy.deepcopy(word_as_list)
                                    word_as_list.pop(0)
                                    go_down(node.children[child],
                                            appended,
                                            res + child,
                                            err + 1 / self.bin_stats[node.lit + "~"][node.lit + child],
                                            deleted,
                                            inserted + 1)
                    # no changes
                    if c in node.children:
                        go_down(node.children[c],
                                copy.deepcopy(word_as_list),
                                res + c,
                                err,
                                deleted,
                                inserted)

                    if bigram in self.bin_stats:
                        for child in node.children:
                            # swap
                            if node.lit + child in self.bin_stats[bigram]:
                                go_down(node.children[child],
                                        copy.deepcopy(word_as_list),
                                        (res + child),
                                        err + 1 / self.bin_stats[bigram][node.lit + child],
                                        deleted,
                                        inserted)
                        # delete
                        if deleted < MAX_DELETE:
                            if node.lit + '~' in self.bin_stats[bigram]:
                                go_down(node,
                                        copy.deepcopy(word_as_list),
                                        res,
                                        err + 1 / self.bin_stats[bigram][node.lit + '~'],
                                        deleted + 1,
                                        inserted)
            else:
                if node.is_word_end:
                    result[res] = err
                    return

        result = {}
        go_down(self.root, list(word), "", 0, 0, 0)
        print(sorted(result.items(), key=lambda kv: (kv[1], kv[0])))
