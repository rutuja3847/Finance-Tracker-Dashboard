import pandas as pd
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

FILE = "finance_data.csv"
FORMAT = "%d-%m-%Y"

# Initialize CSV
try:
    pd.read_csv(FILE)
except:
    pd.DataFrame(columns=["date","amount","category","description"]).to_csv(FILE,index=False)

# ---------- FUNCTIONS ----------

def add_entry():
    date = date_entry.get() or datetime.today().strftime(FORMAT)
    amount = amount_entry.get()
    category = category_var.get()
    desc = desc_entry.get()

    if not amount or not category:
        messagebox.showerror("Error","Please fill all required fields")
        return

    df = pd.read_csv(FILE)
    new = pd.DataFrame([[date,float(amount),category,desc]],columns=df.columns)
    df = pd.concat([df,new],ignore_index=True)
    df.to_csv(FILE,index=False)

    messagebox.showinfo("Success","Entry Added Successfully")
    clear_fields()


def view_data():
    df = pd.read_csv(FILE)
    if df.empty:
        messagebox.showinfo("Info","No data available")
        return

    top = tk.Toplevel(root)
    top.title("Transactions")
    top.geometry("650x400")
    top.configure(bg="#1e1e1e")

    tree = ttk.Treeview(top, columns=("Date","Amount","Category","Description"), show="headings")

    for col in ("Date","Amount","Category","Description"):
        tree.heading(col, text=col)
        tree.column(col, anchor="center")

    for _, row in df.iterrows():
        tree.insert("","end",values=list(row))

    tree.pack(fill="both", expand=True)


def show_embedded_chart():
    df = pd.read_csv(FILE)
    if df.empty:
        messagebox.showinfo("Info","No data available")
        return

    df["date"] = pd.to_datetime(df["date"], format=FORMAT)

    income = df[df["category"].str.startswith("Income")].groupby("date")["amount"].sum()
    expense = df[df["category"].str.startswith("Expense")].groupby("date")["amount"].sum()

    fig, ax = plt.subplots()
    ax.plot(income.index, income.values, label="Income")
    ax.plot(expense.index, expense.values, label="Expense")
    ax.set_title("Income vs Expense")
    ax.legend()

    for widget in chart_frame.winfo_children():
        widget.destroy()

    canvas = FigureCanvasTkAgg(fig, master=chart_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)


def show_pie_embedded():
    df = pd.read_csv(FILE)
    if df.empty:
        messagebox.showinfo("Info","No data available")
        return

    expense = df[df["category"].str.contains("Expense")]
    if expense.empty:
        messagebox.showinfo("Info","No expense data")
        return

    expense = expense.copy()
    expense["sub"] = expense["category"].apply(lambda x: x.split(" - ")[1] if " - " in x else x)
    data = expense.groupby("sub")["amount"].sum()

    fig, ax = plt.subplots()
    ax.pie(data, labels=data.index, autopct="%1.1f%%")
    ax.set_title("Expense Distribution")

    for widget in chart_frame.winfo_children():
        widget.destroy()

    canvas = FigureCanvasTkAgg(fig, master=chart_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)


def clear_fields():
    date_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)
    desc_entry.delete(0, tk.END)

# ---------- UI ----------
root = tk.Tk()
root.title("💰 Finance Tracker")
root.geometry("700x600")
root.configure(bg="#121212")

style = ttk.Style()
style.theme_use("default")

style.configure("TLabel", background="#121212", foreground="white")
style.configure("TEntry", fieldbackground="#1e1e1e", foreground="white")

# Header
tk.Label(root, text="Finance Tracker", font=("Arial", 18, "bold"), bg="#121212", fg="white").pack(pady=10)

frame = tk.Frame(root, bg="#1e1e1e")
frame.pack(padx=15, pady=10, fill="x")

# Inputs
tk.Label(frame, text="Date", bg="#1e1e1e", fg="white").grid(row=0, column=0)
date_entry = ttk.Entry(frame)
date_entry.grid(row=0, column=1)

tk.Label(frame, text="Amount", bg="#1e1e1e", fg="white").grid(row=1, column=0)
amount_entry = ttk.Entry(frame)
amount_entry.grid(row=1, column=1)

tk.Label(frame, text="Category", bg="#1e1e1e", fg="white").grid(row=2, column=0)
category_var = tk.StringVar()
category_menu = ttk.Combobox(frame, textvariable=category_var)
category_menu['values'] = (
    "Income - Salary","Income - Freelance",
    "Expense - Food","Expense - Rent","Expense - Travel"
)
category_menu.grid(row=2, column=1)

tk.Label(frame, text="Description", bg="#1e1e1e", fg="white").grid(row=3, column=0)
desc_entry = ttk.Entry(frame)
desc_entry.grid(row=3, column=1)

# Buttons
btn_frame = tk.Frame(root, bg="#121212")
btn_frame.pack(pady=10)

ttk.Button(btn_frame, text="Add", command=add_entry).grid(row=0, column=0, padx=5)
ttk.Button(btn_frame, text="View", command=view_data).grid(row=0, column=1, padx=5)
ttk.Button(btn_frame, text="Line Chart", command=show_embedded_chart).grid(row=0, column=2, padx=5)
ttk.Button(btn_frame, text="Pie Chart", command=show_pie_embedded).grid(row=0, column=3, padx=5)

# Chart Frame
chart_frame = tk.Frame(root, bg="#1e1e1e")
chart_frame.pack(fill="both", expand=True, padx=10, pady=10)

root.mainloop()
