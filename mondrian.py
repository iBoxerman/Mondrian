import numpy as np
import time
from utils.data import get_data, get_qis
from partition import Partition

k = 10
results = []
qis_info = {}


def run(arg_k=10, qis=None, path=None, rows=None):
    global k
    global qis_info
    if arg_k:
        k = arg_k
    output_path = './mondrian_results.csv'
    if path:
        path = path + './resources/adult.data'
        output_path = '.' + output_path
    data, qis = init(path=path, rows=rows, qis=qis)
    qis_info = get_qis()
    whole = Partition(data)
    start_time = time.time()
    run_partition(whole)
    print(f'time: {time.time()-start_time}')
    global results
    output = data.copy().astype(str)
    for partition in results:
        reconstruct_result(partition, output)
    output.to_csv(output_path, sep=',', header=False, index=False)


def reconstruct_result(partition, output, delimiter='~'):
    global qis_info
    row = {}
    for qi in qis_info["names"]:
        low = partition.resrections[qi]["low"]
        high = partition.resrections[qi]["high"]
        dt = 'U50'
        keys = np.fromiter(qis_info["str_qis"][qi].keys(), dtype=dt)
        vals = np.fromiter(qis_info["str_qis"][qi].values(), dtype=int)
        pos = np.where(vals == low)
        res = keys[pos][0]
        if low != high:
            if np.array_equal(keys, vals.astype(dt)):
                res = res + delimiter + str(high)
            else:
                for idx in vals:
                    if idx < low:
                        continue
                    elif low < idx <= high:
                        res += delimiter + keys[idx]
                    elif idx > high:
                        break
        row[qi] = res
    for index, record in partition.data.iterrows():
        for qi in row:
            output.at[index, qi] = row[qi]


def init(arg_k=10, qis=None, path=None, rows=None):
    global k
    k = arg_k
    data, qis = get_data(path=path, mod_qis=qis, rows=rows)
    return data, qis


def run_partition(partition):
    global results
    if not all(partition.finished_qis):
        results.append(partition)
        return
    for idx in range(len(partition.finished_qis)):
        dim, qi = choose_dim(partition)
        if dim < 0:
            raise Exception("dim < 0")
        split, next = find_mid(partition, qi)
        if split == next:
            partition.finished_qis[qi] = True
            continue
        df = partition.data
        lhs = Partition(df[df[qi] <= split])
        rhs = Partition(df[df[qi] > split])
        if len(lhs) < k or len(rhs) < k:
            partition.finished_qis[qi] = True
            continue
        run_partition(lhs)
        run_partition(rhs)
        return
    results.append(partition)


def choose_dim(partition):
    m_w = -1
    m_d = -1
    m_qi = ""
    for dim, name in enumerate(qis_info["names"]):
        if partition.finished_qis[name]:
            continue
        norm = calc_norm(partition, name)
        if norm > m_w:
            m_w = norm
            m_d = dim
            m_qi = name
    if m_w > 1:
        raise Exception("norm > 1")
    return m_d, m_qi


def calc_norm(partition, qi):
    keys = partition.data[qi].unique()
    all_keys = list(qis_info["str_qis"][qi].values())
    diff = lambda arr: float(np.max(arr)) - float(np.min(arr))
    width = diff(keys)
    all_width = diff(all_keys)
    if width == all_width:
        return 1
    return width * 1.0 / all_width


def frequency_set(partition, qi):
    freq_set = {}
    for k, v in partition.data[qi].value_counts().iteritems():
        freq_set[k] = v
    return freq_set


def find_mid(partition, qi):
    global k
    freq_set = frequency_set(partition, qi)
    split = ''
    next = ''
    values = sorted(freq_set.keys())
    total = sum(freq_set.values())
    middle = total // 2
    if middle < k or len(values) <= 1:
        return '', ''
    curr_index = 0
    split_index = 0
    for idx, val in enumerate(values):
        curr_index += freq_set[val]
        if curr_index >= middle:
            split = val
            split_index = idx
            break
    next = values[split_index + 1] if split_index + 1 < len(values) else split
    return split, next


if __name__ == '__main__':
    run()
