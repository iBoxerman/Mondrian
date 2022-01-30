from utils.data import attributes, default_attributes, str_attributes
from mondrian import run
from tkinter import *
from tkinter import ttk
import ttkthemes as theme
import pandas as pd

attributes_with_income = attributes.copy()


def attributes_without_income():
    temp = attributes_with_income.copy()
    temp.remove('income')
    return temp


root = Tk()
root.title("Mondrian - Itai & Igal")
root.attributes("-fullscreen", True)

pad_x = 20
pad_y = 20
font_family = "Thaoma"
font = (font_family, 18)
title_font = (font_family, 20, "bold")

curr_theme = 'default'  # equilux
style = theme.ThemedStyle(root)
style.theme_use(curr_theme)

style.configure('TLabel', font=font)
style.configure('exit.TButton', font=font)
style.configure('run.TButton', font=font)
style.map('exit.TButton', background=[('active', 'red')])
style.map('run.TButton', background=[('active', 'green')])
style.configure('Treeview.Heading', font=font)
style.configure('Treeview', font=font)
if theme == 'equilux':
    style.map('Treeview', background=[('selected', '#d69806'), ('disabled', '#2e2e2e')],
              foreground=[('selected', 'black')])

config_model = ttk.Frame(root)
results_frame = ttk.Frame(root)


def main_window(init=False):
    switch_to_main()
    scales_frame = ttk.Frame(config_model)

    k_frame = ttk.Frame(scales_frame)
    k_label = ttk.Label(k_frame, text="Choose K", font=title_font)
    k = ttk.LabeledScale(k_frame, from_=0, to=1000)
    k.value = 100
    k_label.pack(side=TOP, expand=YES)
    k.pack(side=BOTTOM, fill=X, expand=YES)

    n_frame = ttk.Frame(scales_frame)
    n_label = ttk.Label(n_frame, text="Choose Number of Records", font=title_font)
    n = ttk.LabeledScale(n_frame, from_=1, to=32561)
    # n.value = 32561//2
    n.value = 30000
    n_label.pack(side=TOP, expand=YES)
    n.pack(side=BOTTOM, fill=X, expand=YES)

    k_frame.pack(padx=pad_x, side=LEFT, anchor=W, fill=X, expand=YES)
    n_frame.pack(padx=pad_x, side=RIGHT, anchor=E, fill=X, expand=YES)

    list_frame = ttk.Frame(config_model)
    listbox = ttk.Treeview(list_frame, selectmode='extended', show="headings", columns=("name", "type"))
    listbox.column("# 1", anchor=CENTER)
    listbox.heading("# 1", text="Attribute")
    listbox.column("# 2", anchor=CENTER)
    listbox.heading("# 2", text="Type")
    for i, attribute in enumerate(attributes_without_income()):
        listbox.insert('', index=i, iid=i,
                       values=(attribute, "string" if attribute in str_attributes else "integer"),
                       tags=('entry'))
        if attribute in default_attributes:
            listbox.selection_toggle(i)
    listbox.tag_configure('entry', font=font)
    listbox.pack(padx=pad_x, fill=BOTH, expand=YES)

    def action():
        qis = []
        chosen_qis = listbox.selection()
        for i in chosen_qis:
            op = listbox.item(i)
            qis.append(op["values"][0])

        results_path, results_filename, input_data_filename, time_duration, ncp = run(k.value, qis,
                                                                                      n_rows=n.value + 1)
        results(results_path, results_filename, input_data_filename, qis, time_duration, ncp, k.value, n.value)
        switch_to_results()

    buttons_frame = create_buttons_frame(config_model, "Run", action)

    scales_frame.pack(side=TOP, fill=X, expand=YES)
    list_frame.pack(fill=BOTH, expand=YES)
    buttons_frame.pack(side=BOTTOM, fill=X, expand=YES)

    if init:
        mainloop()


def switch_to_results():
    global config_model
    clear_frame(config_model)
    results_frame.pack(fill=BOTH, expand=YES)


def switch_to_main():
    global results_frame
    clear_frame(results_frame)
    config_model.pack(fill=BOTH, expand=YES)


def results(results_path, results_filename, input_data_filename, qis, time_duration, ncp,k,n):
    switch_to_results()
    text_frame = ttk.Frame(results_frame)
    for sen in [f'Results for k={k}, n={n}',
                f'QIS={qis}\n',
                f'Information Loss: {ncp:.3f}%\n',
                f'Running time: {time_duration:.3f} seconds']:
        ttk.Label(text_frame, text=sen).pack(anchor=CENTER)

    tables_frame = ttk.Frame(results_frame)
    input_frame = ttk.Frame(tables_frame)
    input_label = ttk.Label(input_frame, text="input data", font=title_font)
    input_df = pd.read_csv(results_path + input_data_filename)
    input_tree = build_tree(input_frame, input_df, qis)
    input_label.pack(pady=pad_y)
    input_tree.pack(padx=pad_x, fill=BOTH, expand=YES)

    output_frame = ttk.Frame(tables_frame)
    output_label = ttk.Label(output_frame, text="output data", font=title_font)
    output_df = pd.read_csv(results_path + results_filename)
    output_tree = build_tree(output_frame, output_df, qis)
    output_label.pack(pady=pad_y)
    output_tree.pack(padx=pad_x, fill=BOTH, expand=YES)

    input_frame.pack(side=TOP, fill=BOTH, expand=YES)
    output_frame.pack(side=BOTTOM, fill=BOTH, expand=YES)

    buttons_frame = create_buttons_frame(results_frame, '', None)

    text_frame.pack(fill=X)
    tables_frame.pack(fill=BOTH, expand=YES)
    buttons_frame.pack(side=BOTTOM, fill=X)


def build_tree(frame, df, qis):
    container = ttk.Frame(frame)
    table_cols = ['index'] + qis
    tree = ttk.Treeview(container, selectmode='extended', show="headings", columns=table_cols)
    clear_tree(tree)
    for index, qi in enumerate(table_cols):
        tree.column(index, anchor=CENTER, width=50) if index == 0 else tree.column(index, anchor=CENTER)
        tree.heading(index, text=qi)

    scrollbar_yvertical = ttk.Scrollbar(container, orient='vertical', command=tree.yview)
    scrollbar_xvertical = ttk.Scrollbar(container, orient='horizontal', command=tree.xview)
    tree.configure(yscrollcommand=scrollbar_yvertical.set)
    tree.configure(xscrollcommand=scrollbar_xvertical.set)

    df_rows = df.to_numpy().tolist()
    for index, row in enumerate(df_rows):
        tree.insert("", END, values=(index + 1, *row))

    scrollbar_yvertical.pack(padx=3, side=RIGHT, anchor=CENTER, fill=Y)
    scrollbar_xvertical.pack(pady=0, side=BOTTOM, anchor=S, fill=X)

    tree.pack(fill=BOTH, expand=YES)
    return container


def clear_tree(my_tree):
    my_tree.delete(*my_tree.get_children())


def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()
    frame.pack_forget()


def create_buttons_frame(frame, run_text, run_cmd):
    buttons_frame = ttk.Frame(frame)
    if run_text != '' and run_cmd is not None:
        run_button = ttk.Button(buttons_frame, text=run_text, command=run_cmd, style="run.TButton")
        run_button.pack(padx=pad_x, pady=pad_y, side=RIGHT, fill=X, expand=YES)
    exit_button = ttk.Button(buttons_frame, text="Exit", command=root.quit, style="exit.TButton")
    exit_button.pack(padx=pad_x, pady=pad_y, side=LEFT, fill=X, expand=YES)
    return buttons_frame


if __name__ == '__main__':
    main_window(init=True)
