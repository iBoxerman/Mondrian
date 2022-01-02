import numpy as np
import matplotlib.pyplot as plt
from mondrian import run


def avg_over_params(selected_k=10, selected_qis=None, n_rows=None, n_iter=10):
    results = []
    for i in range(n_iter):
        e_counter = 0
        while e_counter < 3:
            print(f'\n-> DEBUG[{i}]: k: {selected_k}, n_rows: {n_rows}')
            try:
                _, _, _, time_duration, total_ncp = run(selected_k=selected_k, selected_qis=selected_qis, n_rows=n_rows)
                results.append([total_ncp, time_duration])
                break
            except:
                print(f'Exception!!!!!!!!! e_counter: {e_counter}')
                e_counter += 1
    x= 3
    avg_ncp, avg_time = np.mean(results, axis=0)
    return avg_ncp, avg_time



def avg_error_over_k():
    results = []
    ks = [i for i in range(1, 21)]
    for k in ks:
        avg_ncp, avg_time = avg_over_params(k, selected_qis=None, n_rows=None, n_iter=10)
        results.append([avg_ncp, avg_time])

    results = np.asarray(results)
    plt.figure()
    plt.title("Avg. NCP over K")
    plt.xlabel("K")
    plt.ylabel("Avg. NCP")
    plt.plot(ks, results[:, 0],'--', marker='o', color='cornflowerblue')
    plt.show()

    plt.figure()
    plt.title("Avg. Time over K")
    plt.xlabel("K")
    plt.ylabel("Avg. Time")
    plt.plot(ks, results[:, 1], '--', marker='o', color='cornflowerblue')
    plt.show()

def avg_error_over_n():
    results = []
    ns = [i for i in range(1000, 32000,1500)]
    for n in ns:
        avg_ncp, avg_time = avg_over_params(10, selected_qis=None, n_rows=n, n_iter=10)
        results.append([avg_ncp, avg_time])

    results = np.asarray(results)
    plt.figure()
    plt.suptitle("Avg. NCP over n records")
    plt.title('K=10')

    plt.xlabel("n")
    plt.ylabel("Avg. NCP")
    plt.plot(ns, results[:, 0],'--', marker='o', color='cornflowerblue')
    plt.show()

    plt.figure()
    plt.suptitle("Avg. Time over n records")
    plt.title('K=10')
    plt.xlabel("n")
    plt.ylabel("Avg. Time")
    plt.plot(ns, results[:, 1],'--', marker='o', color='cornflowerblue')
    plt.show()

if __name__ == '__main__':
    pass
    # TODO: run graphs and send plots
    # TODO: run over different sizes of qis
    # avg_error_over_k()
    # avg_error_over_n()
