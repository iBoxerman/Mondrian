import numpy as np
import time
from utils.data import get_data, get_qis
from partition import Partition
import cProfile
import pstats

k = 10
results = []
qis_info = {}


def run(selected_k=10, selected_qis=None, n_rows=None):
    print(selected_qis)
    print(f'starting mondrian...')
    global k
    global qis_info
    k = selected_k

    results_folder_path = './resources'
    output_filename = 'mondrian_results.csv'
    raw_data_filename = './resources/adult.data'
    selected_data_filename = 'mondrian_input.csv'
    data, selected_qis, selected_rows = get_data(selected_qis=selected_qis, n_rows=n_rows,
                                  output_path=results_folder_path, raw_data_filename=raw_data_filename,
                                  selected_data_filename=selected_data_filename)
    qis_info = get_qis()
    whole = Partition(data)
    start_time = time.time()
    run_partition(whole)
    time_duration = time.time() - start_time
    global results
    output = data.astype(str)
    total_ncp = 0.0
    for partition in results:
        partition_ncp = reconstruct_result(partition, output)
        partition_ncp *= len(partition)
        total_ncp += partition_ncp
    total_ncp /= len(selected_qis)
    total_ncp /= selected_rows
    total_ncp *=100
    output.to_csv(results_folder_path + '/' + output_filename, sep=',', header=False, index=False)
    print(f'finished in {time_duration} s with ncp of {total_ncp:.3f}')
    return results_folder_path + '/', output_filename, selected_data_filename, time_duration, total_ncp


def reconstruct_result(partition, output, delimiter='~'):
    global qis_info
    row = {}
    partition_ncp = 0.0

    for qi in qis_info["names"]:
        partition_ncp += calc_norm(partition, qi)
        low = partition.restrictions[qi][0]
        high = partition.restrictions[qi][1]
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

    return partition_ncp


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
    max = qis_info["max_min"][qi]["max"]
    min = qis_info["max_min"][qi]["min"]
    width = partition.restrictions[qi][1] - partition.restrictions[qi][0]
    all_width = max - min
    if width == all_width:
        return 1
    return width * 1.0 / all_width


def frequency_set(partition, qi):
    freq_set = {}
    sum = 0
    # for idx , value_at in partition.data.iterrows():
    #     try:
    #         value_at=value_at[1]
    #         freq_set[value_at] += 1
    #         sum += freq_set[value_at]
    #     except KeyError:
    #         freq_set[value_at] = 1
    #         sum += freq_set[value_at]
    # return freq_set, sum

    for k, v in partition.data[qi].value_counts().iteritems():
        freq_set[k] = v
        sum += v
    return freq_set, sum


def find_mid(partition, qi):
    global k
    freq_set, total = frequency_set(partition, qi)
    split = ''
    next = ''
    values = sorted(freq_set.keys())
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
    cProfile.run('run(10, n_rows=None)', './profile_results')

    file = open('formatted_profile.txt', 'w')
    profile = pstats.Stats('./profile_results', stream=file)
    profile.sort_stats('cumulative')  # Sorts the result according to the supplied criteria
    profile.print_stats(15)  # Prints the first 15 lines of the sorted report
    file.close()
