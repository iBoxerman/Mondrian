from utils.data import attributes, default_attributes
from mondrian import run
from tkinter import *


def start_gui():
    just_attributes = attributes.copy()
    just_attributes.remove('income')

    root = Tk()
    root.title("Mondrian")
    root.columnconfigure([i for i in range(7)], minsize=5)
    root.rowconfigure([i for i in range(20)], minsize=10)

    b_height = 5
    b_width = 10

    dict = {}
    r = 0
    c = 0
    Label(root, text="choose K").grid(row=r, column=2)
    k = Scale(root, from_=1, to=20, orient=HORIZONTAL, length=200)
    k.grid(row=r + 1, column=2)
    k.set(10)
    dict["k"] = k

    Label(root, text="choose number of record").grid(row=r, column=5)
    n = Scale(root, from_=1, to=32561, orient=HORIZONTAL, length=200)
    n.grid(row=r + 1, column=5)
    n.set(32561)
    dict["n"] = n

    r += 5

    Label(root, text="choose attributes:", font="bold 12").grid(row=r, column=0)
    r += 2
    for attribute in just_attributes:
        dict[attribute] = {}
        val = IntVar()
        dict[attribute]["var"] = val
        val.set(0)
        b = Checkbutton(root, text=attribute, variable=dict[attribute]["var"], onvalue=1, offvalue=0)
        b.grid(row=r, column=c)
        if attribute in default_attributes:
            val.set(1)
        dict[attribute]["button"] = b
        if c == 6:
            c = -1
            r += 1
        c += 1

    r += 2
    Button(root, text="Exit", command=root.quit, width=b_width, height=b_height).grid(row=r + 1, column=1, sticky=W)

    def results():
        new_win =2

    def action():
        qis = []
        for attribute in just_attributes:
            b = dict[attribute]["var"]
            if b.get() == 1:
                qis.append(attribute)
        run(k.get(), qis, path='.', rows=n.get())
        results()

    Button(root, text="Run", command=action, width=b_width, height=b_height).grid(row=r + 1, column=5, sticky=E)

    mainloop()



if __name__ == '__main__':
    start_gui()
