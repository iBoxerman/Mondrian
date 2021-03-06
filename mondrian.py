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
    global k
    global qis_info
    global results

    k = selected_k
    print(f'starting mondrian... \nk={k}\nselected qis:{selected_qis}')

    results_folder_path = './resources'
    output_filename = 'mondrian_results.csv'
    raw_data_filename = './resources/adult.data'
    selected_data_filename = 'mondrian_input.csv'
    data, selected_qis, n_selected_rows, raw_data = get_data(selected_qis=selected_qis, n_rows=n_rows,
                                                             output_path=results_folder_path,
                                                             raw_data_filename=raw_data_filename,
                                                             selected_data_filename=selected_data_filename)
    qis_info = get_qis()
    whole = Partition(data)
    start_time = time.time()
    if k > 1:
        run_partition(whole)
    else:
        data = raw_data
    time_duration = time.time() - start_time
    output = data.astype(str)
    total_ncp = 0.0
    for partition in results:
        partition_ncp = reconstruct_result(partition, output)
        partition_ncp *= len(partition)
        total_ncp += partition_ncp
    total_ncp /= len(selected_qis)
    total_ncp /= n_selected_rows
    total_ncp *= 100
    output.to_csv(results_folder_path + '/' + output_filename, sep=',', header=False, index=False)
    print(f'finished in {time_duration:.3f} s with ncp of {total_ncp:.3f}%')

    # reset
    results = []
    return results_folder_path + '/', output_filename, selected_data_filename, time_duration, total_ncp


def reconstruct_result(partition, output, delimiter='~'):
    global qis_info
    row = {}
    partition_ncp = 0.0

    for qi in qis_info["names"]:
        partition_ncp += calc_norm(partition, qi)
        low = partition.restrictions[qi][0]
        high = partition.restrictions[qi][1]

        # changing integers back to string (country, gender etc.)
        dt = 'U50'
        keys = np.fromiter(qis_info["str_qis"][qi].keys(), dtype=dt)
        vals = np.fromiter(qis_info["str_qis"][qi].values(), dtype=int)
        pos = np.where(vals == low)
        res = keys[pos][0]

        # unionizing and merging the qi (1,2,3,4,5 -> 1~5)
        if low != high:
            if np.array_equal(keys, vals.astype(dt)):  # qi is an instance of numbers
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
    # setting the anonymize values in output file
    for index, record in partition.data.iterrows():
        for qi in row:
            output.at[index, qi] = row[qi]

    return partition_ncp


def run_partition(partition):
    global results
    if not all(partition.finished_qis):
        results.append(partition)
        return
    n_qis = len(partition.finished_qis)
    for idx in range(n_qis):
        dim, qi = choose_dim(partition)
        if dim < 0:
            raise Exception("dim < 0")
        split_val, next_val = find_mid(partition, qi)
        if split_val == next_val:
            partition.finished_qis[qi] = True
            continue
        df = partition.data
        lhs = Partition(df[df[qi] <= split_val])
        rhs = Partition(df[df[qi] > split_val])
        if len(lhs) < k or len(rhs) < k:
            partition.finished_qis[qi] = True
            continue
        run_partition(lhs)
        run_partition(rhs)
        return
    results.append(partition)


def choose_dim(partition):
    max_width = -1
    max_dim = -1
    max_qi_name = ""
    for dim, name in enumerate(qis_info["names"]):
        if partition.finished_qis[name]:
            continue
        norm = calc_norm(partition, name)
        if norm > max_width:
            max_width = norm
            max_dim = dim
            max_qi_name = name
    if max_width > 1:
        raise Exception("norm > 1")
    return max_dim, max_qi_name


def calc_norm(partition, qi):
    global_max = qis_info["max_min"][qi]["max"]
    global_min = qis_info["max_min"][qi]["min"]
    partition_width = partition.restrictions[qi][1] - partition.restrictions[qi][0]
    global_width = global_max - global_min
    if partition_width == global_width:
        return 1
    return partition_width * 1.0 / global_width


def frequency_set(partition, qi):
    freq_set = {}
    total_sum = 0
    for key, val in partition.data[qi].value_counts().iteritems():
        freq_set[key] = val
        total_sum += val
    return freq_set, total_sum


def find_mid(partition, qi):
    global k
    freq_set, total_sum = frequency_set(partition, qi)
    split_val = ''
    values = sorted(freq_set.keys())
    middle = total_sum // 2
    if middle < k or len(values) <= 1:
        return '', ''
    curr_sum = 0
    split_index = 0
    for idx, val in enumerate(values):
        curr_sum += freq_set[val]
        if curr_sum >= middle:
            split_val = val
            split_index = idx
            break
    next_val = values[split_index + 1] if split_index + 1 < len(values) else split_val
    return split_val, next_val


if __name__ == '__main__':
    cProfile.run('run(2, n_rows=8)', './profile_results')

    file = open('formatted_profile.txt', 'w')
    profile = pstats.Stats('./profile_results', stream=file)
    profile.sort_stats('cumulative')  # Sorts the result according to the supplied criteria
    profile.print_stats(15)  # Prints the first 15 lines of the sorted report
    file.close()
