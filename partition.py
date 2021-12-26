import numpy as np
from utils.data import get_qis


class Partition(object):
    def __init__(self, data):
        self.data = data
        self.finished_qis = {}
        self.resrections = {}
        qis = list(data.columns)
        qis.remove('income')
        for qi in qis:
            self.finished_qis[qi] = False
            self.resrections[qi] = {}
            self.resrections[qi]["high"] = np.max(data[qi])
            self.resrections[qi]["low"] = np.min(data[qi])


    def __len__(self):
        return len(self.data)
