import numpy as np
import pandas as pd

attributes = ['age', 'work_class', 'final_weight', 'education',
              'education_num', 'marital_status', 'occupation', 'relationship',
              'race', 'sex', 'capital_gain', 'capital_loss', 'hours_per_week',
              'native_country','income']
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
                "str_qis": {}}
    for qi in qis:
        qis_info["values_per_qi"][qi] = {}
        for k, v in data[qi].value_counts().iteritems():
            qis_info["values_per_qi"][qi][k] = v


def get_data(path=None, mod_qis=None, rows=None):
    global qis
    if mod_qis:
        qis = mod_qis
    if not path:
        path = './resources/adult.data'
    print(f'get data: {path}')
    if 'income' in qis: qis.remove('income')
    qis.append('income')
    data = pd.read_csv(path, names=attributes, sep=',', skipinitialspace=True)
    if rows:
        data = data.sample(n=rows)
    data = data[qis]
    qis.remove('income')
    data = filter_data(data)
    set_dict(data, qis)
    data = convert_to_number(data)
    return data, qis[:-1]


def convert_to_number(data):
    global qis_info
    for qi in qis_info["names"]:
        # if qi not in str_attributes:
        #     continue
        column_options = data[qi].unique()
        qis_info["str_qis"][qi]={}
        for i, option in enumerate(column_options):
            if qi in str_attributes:
                str_attributes[qi].append(option)
                data[qi] = data[qi].replace(option, i)
                qis_info["str_qis"][qi][option] = i
            else:
                qis_info["str_qis"][qi][option] = option
    return data


def filter_data(data):
    filters = ['?', ' ?']
    for f in filters:
        data = data.replace(f, np.nan)
    data = data.dropna()
    return data


def reconstruct_attribute(df):
    qis = df.columns
    for qi in qis:
        if qi not in str_attributes:
            continue
        for i, option in enumerate(str_attributes[qi]):
            df[qi] = df[qi].replace(i, option)
