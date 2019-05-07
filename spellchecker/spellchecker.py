from error_model import ErrorModel
from language_model import LanguageModel
from bor import BORtree
import sys
import pickle

if __name__ == "__main__":
    sys.setrecursionlimit(100000)
    error = ErrorModel()
    error.load_json("bin_stats.json")

    # lm = LanguageModel()
    # lm.create_model("queries_all.txt")
    # with open("lm.pickle", "wb") as f:
    #     pickle.dump(lm, f)

    with open("lm.pickle", "rb") as f:
        lm = pickle.load(f)

    tree = BORtree(error.bin_stats, 1 / error.bin_size)
    tree.load_tree()
    tree.indistrinct_search("кожка")
