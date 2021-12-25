import numpy as np
from utils.data import get_qis


class Partition(object):
    def __init__(self, data):
        self.data = data
        self.finished_qis = {}
        self.resrections = {}
        for qi in get_qis()["names"]:
            self.finished_qis[qi] = False
            self.resrections[qi] = {}
            self.resrections[qi]["high"] = np.max(data[qi])
            self.resrections[qi]["low"] = np.min(data[qi])

    # def add_record(self, record, dim):
    #     self.member.append(record)

    # def add_multiple_record(self, records, dim):
    #     for record in records:
    #         self.add_record(record, dim)

    def __len__(self):
        return len(self.data)
