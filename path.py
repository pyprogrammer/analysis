import collections
import pickle

HistoryElement = collections.namedtuple("HistoryElement", ["branch", "type", "done"])

def read_path(filename):
    try:
        with open(filename, "r") as f:
            return pickle.load(f)
    except IOError:
        return []

def write_path(filename, path):
    # format = (id [int], then/else [str], done [bool])
    with open(filename, "w") as f:
        pickle.dump(path, f)

def cmp_n_set_branch_hist(hist, branch_id, branch_type, i):
    if i < len(hist):
        if hist[i].type != branch_type:
            raise ValueError("Prediction Failed, {}, {} != {}, {}".format(hist[i].branch, hist[i].type, branch_id, branch_type))
        elif i == len(hist) - 1:
            hist[i] = HistoryElement(hist[i].branch, hist[i].type, True)
    else:
        hist.append(HistoryElement(branch_id, branch_type, False))