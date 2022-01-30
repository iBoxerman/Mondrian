import numpy as np


class Partition(object):
    def __init__(self, data):
        self.data = data
        self.finished_qis = {}
        self.restrictions = {}

        qis = data.columns.tolist()
        qis.remove('income')

        for qi in qis:
            self.finished_qis[qi] = False
            self.restrictions[qi] = []
            self.restrictions[qi].append(np.min(data[qi]))
            self.restrictions[qi].append(np.max(data[qi]))

    def __len__(self):
        return len(self.data)
