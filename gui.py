from utils.data import attributes, default_attributes
from mondrian import run
from tkinter import *
from tkinter import ttk
import pandas as pd
import platform

attributes_with_income = attributes.copy()


def attributes_without_income():
    temp = attributes_with_income.copy()
    temp.remove('income')
    return temp


b_height = 5
b_width = 10

root = Tk()
root.title("Mondrian")
root.columnconfigure([i for i in range(7)], minsize=5)
root.rowconfigure([i for i in range(20)], minsize=10)

config_model = Frame(root)
results_frame = Frame(root)


def main_window(init=False):
    switch_to_main()

    dict = {}
    r = 0
    c = 0
    Label(config_model, text="choose K").grid(row=r, column=2)
    k = Scale(config_model, from_=1, to=20, orient=HORIZONTAL, length=200)
    k.grid(row=r + 1, column=2)
    k.set(10)
    dict["k"] = k

    Label(config_model, text="choose number of record").grid(row=r, column=5)
    n = Scale(config_model, from_=1, to=32561, orient=HORIZONTAL, length=200)
    n.grid(row=r + 1, column=5)
    n.set(32561)
    dict["n"] = n

    r += 5

    Label(config_model, text="choose attributes:", font="bold 12").grid(row=r, column=0)
    r += 2
    for attribute in attributes_without_income():
        dict[attribute] = {}
        val = IntVar()
        dict[attribute]["var"] = val
        val.set(0)
        b = Checkbutton(config_model, text=attribute, variable=dict[attribute]["var"], onvalue=1, offvalue=0)
        b.grid(row=r, column=c)
        if attribute in default_attributes:
            val.set(1)
        dict[attribute]["button"] = b
        if c == 6:
            c = -1
            r += 1
        c += 1

    r += 2
    exit_button = create_button(parent=config_model, text="Exit", cmd=root.quit, bg='red')
    exit_button.grid(row=r + 1, column=1, sticky=W)

    def action():
        qis = []
        for attribute in attributes_without_income():
            b = dict[attribute]["var"]
            if b.get() == 1:
                qis.append(attribute)
        results_path, results_filename, input_data_filename, time_duration = run(k.get(), qis,
                                                                                 n_rows=n.get())
        results(results_path, results_filename, input_data_filename, qis, time_duration)
        switch_to_results()

    Button(config_model, text="Run", command=action, width=b_width, height=b_height, bg='green',
           fg='white').grid(row=r + 1, column=5, sticky=E)

    if init:
        mainloop()


def switch_to_results():
    global config_model
    config_model.grid_forget()
    results_frame.grid(row=0, column=0)


def switch_to_main():
    global results_frame
    results_frame.grid_forget()
    config_model.grid(row=0, column=0)


def results(results_path, results_filename, input_data_filename, qis, time_duration):
    input_tree = ttk.Treeview(results_frame)
    results_tree = ttk.Treeview(results_frame)

    input_df = pd.read_csv(results_path + input_data_filename)
    results_df = pd.read_csv(results_path + results_filename)

    clear_tree(input_tree)
    clear_tree(results_tree)
    r = 0

    Label(results_frame, text="input data").grid(row=r, column=0)
    r += 2
    build_tree(input_tree, input_df, qis, r=r, c=0)
    r += 4
    Label(results_frame, text="output data").grid(row=r, column=0)
    r += 2
    build_tree(results_tree, results_df, qis, r=r, c=0)
    r += 2

    exit_button = create_button(parent=results_frame, text="Exit", cmd=root.quit, bg='red')
    exit_button.grid(row=r+1, column=1, sticky=W)

    Button(results_frame, text="Run Again", command=main_window, width=b_width, height=b_height,
           highlightbackground='green',
           fg='white').grid(
        row=r, column=5, sticky=E)


def build_tree(tree, df, qis, r, c):
    tree["column"] = qis
    tree["show"] = "headings"
    for col in tree["column"]:
        tree.heading(col, text=col)
    df_rows = df.to_numpy().tolist()
    for row in df_rows:
        tree.insert("", "end", values=row)
    tree.grid(row=r, column=c)


def clear_tree(my_tree):
    my_tree.delete(*my_tree.get_children())


def create_button(parent=root, text="", cmd=None, width=b_width, height=b_height, bg='green', fg='white'):
    return Button(parent, text=text, command=cmd,
                  width=width, height=height)
                  # highlightbackground=bg, fg=fg, highlightthickness=0,
                  # activebackground=bg, activeforeground=fg)


if __name__ == '__main__':
    main_window(init=True)
