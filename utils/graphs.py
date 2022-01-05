import random

import numpy as np
import matplotlib.pyplot as plt
from mondrian import run



def_qis = ['age', 'work_class','education_num', 'marital_status',
           'occupation', 'race', 'sex', 'native_country']

def avg_over_params(selected_k=10, selected_qis=None, n_rows=None, n_iter=10):
    results = []
    for i in range(n_iter):
        e_counter = 0
        while e_counter < 100:
            print(f'\n-> DEBUG[{i}]: k: {selected_k}, n_rows: {n_rows}')
            try:
                _, _, _, time_duration, total_ncp = run(selected_k=selected_k, selected_qis=selected_qis, n_rows=n_rows)
                if total_ncp<=100:
                    results.append([total_ncp, time_duration])
                break
            except:
                print(f'Exception!!!!!!!!! e_counter: {e_counter}')
                e_counter += 1

    avg_ncp, avg_time = np.mean(results, axis=0)
    return avg_ncp, avg_time


def avg_error_over_k():
    results = []
    ks = [i for i in range(10, 1011, 100)]
    n_rows = 30000
    for k in ks:
        avg_ncp, avg_time = avg_over_params(k, selected_qis=def_qis, n_rows=n_rows, n_iter=10)
        results.append([avg_ncp, avg_time])

    make_graphs(results, ks, over="K", param=f'n={n_rows}, number of qis={len(def_qis)}', x_label="K")


def avg_error_over_n():
    results = []
    ns = [i for i in range(1000, 32000, 1000)]
    k = 10
    for n in ns:
        avg_ncp, avg_time = avg_over_params(k, selected_qis=def_qis, n_rows=n, n_iter=10)
        results.append([avg_ncp, avg_time])

    make_graphs(results, ns, over="n records", param=f'K={k}, number of qis={len(def_qis)}', x_label="n")


def avg_error_over_n_qis():
    qis = ['age', 'work_class', 'final_weight', 'education',
           'education_num', 'marital_status', 'occupation', 'relationship',
           'race', 'sex', 'capital_gain', 'capital_loss', 'hours_per_week',
           'native_country']
    results = []
    n_qis = [i for i in range(2, 13)]
    k = 10
    n_rows = 30000
    n_iter = 10

    pre_qis = random.sample(qis, n_qis[0])
    for n in n_qis:
        sub_res = []
        for i in range(n_iter):
            selected_qis = random.sample(qis, n)
            while selected_qis == pre_qis:
                print('\n\nreshuffle\n')
                selected_qis = random.sample(qis, n)
            avg_ncp, avg_time = avg_over_params(k, selected_qis=selected_qis, n_rows=n_rows, n_iter=1)
            pre_qis = selected_qis
            sub_res.append([avg_ncp, avg_time])
        avg_ncp, avg_time = np.mean(sub_res, axis=0)
        results.append([avg_ncp, avg_time])

    make_graphs(results, n_qis,
                over="number of Quasi Identifiers", param=f'K={k}, number of records={n_rows}', x_label="number of quasi identifiers")


def qis_by_type():
    str_qis = ['work_class', 'education', 'marital_status',
               'occupation', 'relationship','race',
               'sex', 'native_country']
    int_qis = ['age', 'final_weight', 'education_num',
               'capital_gain', 'capital_loss', 'hours_per_week' ]

    n_qis = [i for i in range(2, min(len(str_qis), len(int_qis)))]
    k = 10
    n_rows = 30000
    n_iter = 10

    results = []
    qis = str_qis
    pre_qis = random.sample(qis, n_qis[0])
    for n in n_qis:
        sub_res = []
        for i in range(n_iter):
            selected_qis = random.sample(qis, n)
            while selected_qis == pre_qis:
                print('\n\nreshuffle\n')
                selected_qis = random.sample(qis, n)
            avg_ncp, avg_time = avg_over_params(k, selected_qis=selected_qis, n_rows=n_rows, n_iter=1)
            pre_qis = selected_qis
            sub_res.append([avg_ncp, avg_time])
        avg_ncp, avg_time = np.mean(sub_res, axis=0)
        results.append([avg_ncp, avg_time])
    str_res = np.array(results.copy())

    results = []
    qis = int_qis
    pre_qis = random.sample(qis, n_qis[0])
    for n in n_qis:
        sub_res = []
        for i in range(n_iter):
            selected_qis = random.sample(qis, n)
            while selected_qis == pre_qis:
                print('\n\nreshuffle\n')
                selected_qis = random.sample(qis, n)
            avg_ncp, avg_time = avg_over_params(k, selected_qis=selected_qis, n_rows=n_rows, n_iter=1)
            pre_qis = selected_qis
            sub_res.append([avg_ncp, avg_time])
        avg_ncp, avg_time = np.mean(sub_res, axis=0)
        results.append([avg_ncp, avg_time])

    int_res = np.asarray(results.copy())

    plt.figure()
    plt.suptitle(f"Avg. NCP over QIS by type")
    plt.title(f'K={k}, number of records={n_rows}', fontsize=9)
    plt.xlabel("number of quasi identifiers")
    plt.ylabel("Avg. NCP")
    plt.plot(n_qis, str_res[:, 0], '--', marker='o', color='cornflowerblue')
    plt.plot(n_qis, int_res[:, 0], '--', marker='o', color='tomato')
    plt.legend(['String', 'Integer'])

    plt.show()

    plt.figure()
    plt.suptitle(f"Avg. Time over QIS by type")
    plt.title(f'K={k}, number of records={n_rows}', fontsize=9)
    plt.xlabel("number of quasi identifiers")
    plt.ylabel("Avg. Time")
    plt.plot(n_qis, str_res[:, 1], '--', marker='o', color='cornflowerblue')
    plt.plot(n_qis, int_res[:, 1], '--', marker='o', color='tomato')
    plt.legend(['String', 'Integer'])
    plt.show()


def compare():
    qis = ['marital_status', 'relationship', 'race', 'sex']
    results = []
    ks = [i for i in range(10, 1011, 100)]
    n_rows = 30000
    for k in ks:
        avg_ncp, avg_time = avg_over_params(k, selected_qis=qis, n_rows=n_rows, n_iter=10)
        results.append([avg_ncp, avg_time])

    make_graphs(results, ks, over="K", param=f'number of records={n_rows}, number of qis={len(qis)}', x_label="K")





def make_graphs(results, x, over='', param='', x_label=''):
    results = np.asarray(results)
    plt.figure()
    plt.suptitle(f"Avg. NCP over {over}")
    plt.title(param,fontsize=9)

    plt.xlabel(x_label)
    plt.ylabel("Avg. NCP (%)")
    plt.plot(x, results[:, 0], '--', marker='o', color='cornflowerblue')
    plt.show()

    plt.figure()
    plt.suptitle(f"Avg. Time over {over}")
    plt.title(param,fontsize=9)
    plt.xlabel(x_label)
    plt.ylabel("Avg. Time (seconds)")
    plt.plot(x, results[:, 1], '--', marker='o', color='cornflowerblue')
    plt.show()


if __name__ == '__main__':
    avg_error_over_k()
    avg_error_over_n()
    avg_error_over_n_qis()
    qis_by_type()
    compare()