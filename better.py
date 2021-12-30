from utils.data import attributes, default_attributes
from mondrian import run
from tkinter import *
from tkinter import ttk
from ttkthemes import themed_style
import pandas as pd

attributes_with_income = attributes.copy()


def attributes_without_income():
    temp = attributes_with_income.copy()
    temp.remove('income')
    return temp


root = Tk()
root.title("Mondrian")
root.geometry('700x500')

button_height = 3
button_width = 4
button_border = 4

scale_width = 250
pad_x = 20
pad_y = 20
# title_font = ("Times", 18)
title_font = None
button_font = None


style = ttk.Style()

style.theme_use('alt')


style.configure('exit.TButton', background='red', foreground='white', width=4, borderwidth=0)
style.configure('run.TButton', background='green', foreground='white', width=4, borderwidth=0)
style.map('exit.TButton', background=[('active','red')])
style.map('run.TButton', background=[('active','green')])


config_model = ttk.Frame(root)
results_frame = ttk.Frame(root)


def main_window(init=False):
    switch_to_main()
    scales_frame = ttk.Frame(config_model)

    k_frame = ttk.Frame(scales_frame)
    k_label = ttk.Label(k_frame, text="Choose K")
    k = ttk.LabeledScale(k_frame, from_=1, to=20)
    # k.set(10)
    k_label.pack(side=TOP)
    k.pack(side=BOTTOM, fill=X, expand=YES)

    n_frame = ttk.Frame(scales_frame)
    n_label = ttk.Label(n_frame, text="Choose Number of Records", font=title_font)
    n = ttk.LabeledScale(n_frame, from_=1, to=32561)
    # n.set(32561)
    n_label.pack(side=TOP)
    n.pack(side=BOTTOM, fill=X, expand=YES)

    k_frame.pack(padx=pad_x, side=LEFT, anchor=W, fill=X, expand=YES)
    n_frame.pack(padx=pad_x, side=RIGHT, anchor=E, fill=X, expand=YES)

    list_frame = ttk.Frame(config_model)
    list_label = ttk.Label(list_frame, text="choose attributes:", font="bold 12")
    listbox = Listbox(list_frame, selectmode="multiple")

    list_label.pack(side=TOP)
    listbox.pack(padx=pad_x, pady=pad_y, fill=X, expand=YES)

    for i, attribute in enumerate(attributes_without_income()):
        listbox.insert(END, attribute.replace('_', ' '))
        listbox.itemconfig(i)
        if attribute in default_attributes:
            listbox.select_set(i)
            print(attribute)

    def action():
        qis = []
        chosen_qis = listbox.curselection()
        for i in chosen_qis:
            op = listbox.get(i)
            qis.append(op.replace(' ', '_'))

        results_path, results_filename, input_data_filename, time_duration = run(k.get(), qis,
                                                                                 n_rows=n.get())
        results(results_path, results_filename, input_data_filename, qis, time_duration)
        switch_to_results()

    buttons_frame = ttk.Frame(config_model)
    exit_button = ttk.Button(buttons_frame, text="Exit", command=root.quit, style="exit.TButton")
    run_button = ttk.Button(buttons_frame, text="Run", command=action, style="run.TButton")

    exit_button.pack(padx=pad_x, pady=pad_y, side=LEFT, fill=X, expand=YES)
    run_button.pack(padx=pad_x, pady=pad_y, side=RIGHT, fill=X, expand=YES)

    scales_frame.pack(side=TOP, fill=X, expand=YES)
    list_frame.pack(fill=X, expand=TRUE)
    buttons_frame.pack(side=BOTTOM, anchor=S, fill=X, expand=YES)

    if init:
        mainloop()


def switch_to_results():
    global config_model
    config_model.pack_forget()
    results_frame.pack(fill=BOTH, expand=TRUE)


def switch_to_main():
    global results_frame
    results_frame.pack_forget()
    config_model.pack(fill=BOTH, expand=TRUE)


def results(results_path, results_filename, input_data_filename, qis, time_duration):
    input_tree = ttk.Treeview(results_frame)
    results_tree = ttk.Treeview(results_frame)

    input_df = pd.read_csv(results_path + input_data_filename)
    results_df = pd.read_csv(results_path + results_filename)

    clear_tree(input_tree)
    clear_tree(results_tree)
    r = 0

    Label(results_frame, text="input data").pack()
    r += 2
    build_tree(input_tree, input_df, qis)
    r += 4
    Label(results_frame, text="output data").pack()
    r += 2
    build_tree(results_tree, results_df, qis)
    r += 2

    exit_button = create_button(parent=results_frame, text="Exit", cmd=root.quit, bg='red')
    exit_button.pack()

    Button(results_frame, text="Run Again", command=main_window, width=button_width, height=button_height,
           highlightbackground='green',
           fg='white')


def build_tree(tree, df, qis):
    tree["column"] = qis
    tree["show"] = "headings"
    for col in tree["column"]:
        tree.heading(col, text=col)
    df_rows = df.to_numpy().tolist()
    for row in df_rows:
        tree.insert("", "end", values=row)
    tree.pack()


def clear_tree(my_tree):
    my_tree.delete(*my_tree.get_children())


if __name__ == '__main__':
    main_window(init=True)
