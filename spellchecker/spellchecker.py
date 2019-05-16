# -*- coding: utf-8 -*-
import sys
reload(sys)
import pickle

sys.setdefaultencoding('UTF8')
from error_model import ErrorModel
from language_model import LanguageModel
from bor import BORtree
from layout_switcher import LayoutSwitcher
from wordchain import WordChain

if __name__ == "__main__":
    sys.setrecursionlimit(100000)
    error = ErrorModel()
    # error.make_bin_stats("queries_all.txt")
    # error.store_json()
    error.load_json()
    print "em created"

    lm = LanguageModel()
    # lm.create_model("queries_all.txt")
    # with open("pretrained_models/lm.pickle", "wb") as f:
    #     pickle.dump(lm, f)
    #     print "lm created"

    with open("pretrained_models/lm.pickle", "rb") as f:
        lm = pickle.load(f)
        print "lm loaded"

    tree = BORtree(error.bin_stats, 1.0 / error.bin_size)
    # tree.fill_BORtree(lm.get_all_words())
    # tree.store_tree()
    tree.load_tree()
    print "tree loaded"
    # tree.print_tree()
    print tree.is_in_tree("сматре")

    wc = WordChain(lm, tree)
    wc.fix_query("смтреть прно анлайн")

