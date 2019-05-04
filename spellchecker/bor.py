# -*- coding: utf-8 -*-
import sys
import numpy as np
reload(sys)
sys.setdefaultencoding('utf8')


class BORtree:
    class TreeItself:
        def __init__(self):
            self.lit = "~"  # literal of current node
            self.is_word_end = False  # is there words ends in this node
            self.children = {}

    def __init__(self):
        self.root = self.TreeItself()

    def fill_BORtree(self, set_of_words):
        def add_word_to_bor(literals, bor):
            lt = literals.pop(0)
            if lt not in bor.children:
                bor.children[lt] = self.TreeItself()

            bor.children[lt].is_word_end = not literals or bor.children[lt].is_word_end
            bor.children[lt].lit = lt

            if literals:
                add_word_to_bor(literals, bor.children[lt])

        for word in set_of_words:
            literals = list(word)
            add_word_to_bor(literals, self.root)