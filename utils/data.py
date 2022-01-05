import numpy as np
import pandas as pd

attributes = ['age', 'work_class', 'final_weight', 'education',
              'education_num', 'marital_status', 'occupation', 'relationship',
              'race', 'sex', 'capital_gain', 'capital_loss', 'hours_per_week',
              'native_country', 'income']
str_attributes = {'work_class': [], 'education': [],
                  'marital_status': [], 'occupation': [], 'relationship': [],
                  'race': [], 'sex': [], 'native_country': [], 'income': []}
default_attributes = ['age', 'work_class',
                      'education_num', 'marital_status', 'occupation',
                      'race', 'sex', 'native_country', 'income']


qis = default_attributes

qis_info = {}


def get_qis():
    return qis_info


def set_dict(data, qis):
    global qis_info
    qis_info = {"size": len(qis),
                "names": qis,
                "n_unique": [data[qi].nunique() - 1 for qi in qis],
                "values_per_qi": {},
                "str_qis": {},
                "max_min":{}}
    for qi in qis:
        qis_info["values_per_qi"][qi] = {}
        for k, v in data[qi].value_counts().iteritems():
            qis_info["values_per_qi"][qi][k] = v


def get_data(selected_qis=None, n_rows=None, output_path=None,
             raw_data_filename='./resources/adult.data', selected_data_filename='mondrian_input.csv'):
    global qis
    if selected_qis:
        qis = selected_qis

    if not output_path:
        output_path = '.'
    output_path = output_path + '/' + selected_data_filename

    if 'income' in qis: qis.remove('income')
    qis.append('income')

    data = pd.read_csv(raw_data_filename, names=attributes, sep=',', skipinitialspace=True)

    data = data[qis]
    qis.remove('income')

    data = filter_data(data)

    if n_rows and n_rows<len(data.index):
        data = data.sample(n=n_rows)

    data.to_csv(output_path, sep=',', header=False, index=False)

    set_dict(data, qis)

    raw_data = data.copy()
    data = convert_to_number(data)
    return data, qis[:-1], len(data.index),raw_data


def convert_to_number(data):
    global qis_info
    for qi in qis_info["names"]:
        column_options = data[qi].unique()
        qis_info["str_qis"][qi] = {}
        qis_info["max_min"][qi] = {}
        for i, option in enumerate(column_options):
            if qi in str_attributes:
                str_attributes[qi].append(option)
                data[qi] = data[qi].replace(option, i)
                qis_info["str_qis"][qi][option] = i
            else:
                qis_info["str_qis"][qi][option] = option

        vals_list = [*qis_info["str_qis"][qi].values()]
        qis_info["max_min"][qi]["max"] = int(np.max(vals_list))
        qis_info["max_min"][qi]["min"] = int(np.min(vals_list))
    return data


def filter_data(data):
    filters = ['?', ' ?']
    for f in filters:
        data = data.replace(f, np.nan)
    data = data.dropna()
    return data