import tkinter as tk
from tkinter import ttk, messagebox
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
from mydb import Database

# Create an instance of the Database class
data = Database('test.db')

# Initialize selected_rowid globally
selected_rowid = 0

# Functions for GUI operations
def save_record():
    data.insertRecord(item_name.get(), item_amt.get(), transaction_date.get())
    clear_entries()
    refresh_data()

def set_date():
    date = dt.datetime.now()
    dopvar.set(f'{date:%d %B %Y}')

def clear_entries():
    item_amt.delete(0, tk.END)
    item_name.delete(0, tk.END)
    transaction_date.delete(0, tk.END)

def fetch_records():
    for item in tv.get_children():
        tv.delete(item)

    for rec in data.fetchRecord('SELECT rowid, * FROM expense_record'):
        tv.insert(parent='', index='end', iid=rec[0], values=(rec[0], rec[1], rec[2], rec[3]))

def select_record(event):
    global selected_rowid
    selected = tv.focus()
    val = tv.item(selected, 'values')

    try:
        selected_rowid = val[0]
        namevar.set(val[1])
        amtvar.set(val[2])
        dopvar.set(val[3])
    except Exception as ep:
        pass

def update_record():
    global selected_rowid

    selected = tv.focus()
    try:
        data.updateRecord(namevar.get(), amtvar.get(), dopvar.get(), selected_rowid)
        tv.item(selected, text="", values=(namevar.get(), amtvar.get(), dopvar.get()))
    except Exception as ep:
        messagebox.showerror('Error', ep)

    clear_entries()
    refresh_data()

def total_balance():
    total_spent = data.fetchRecord(query="SELECT SUM(item_price) FROM expense_record")[0][0]
    remaining_balance = limit_var.get() - total_spent
    messagebox.showinfo('Current Balance', f"Total Expense: {total_spent}\nBalance Remaining: {remaining_balance}")

def refresh_data():
    fetch_records()

def delete_row():
    global selected_rowid
    if messagebox.askyesno("Confirmation", "Are you sure you want to delete this record?"):
        data.removeRecord(selected_rowid)
        refresh_data()

def generate_report():
    timestamp = dt.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"expenses_report_{timestamp}.pdf"
    data.generate_pdf_report(filename)
    messagebox.showinfo("Success", f"Expense report generated successfully!\nFilename: {filename}")

# Function to generate Excel report
def generate_excel_report():
    try:
        filename = f"expenses_report_{dt.datetime.now():%Y%m%d%H%M%S}.xlsx"
        expense_data = data.fetchRecord(query="SELECT rowid, item_name, item_price, purchase_date FROM expense_record")
        df = pd.DataFrame(expense_data, columns=['Serial no', 'Item Name', 'Item Price', 'Purchase Date'])
        df.to_excel(filename, index=False)
        messagebox.showinfo("Success", f"Expense report generated successfully!\nFilename: {filename}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to generate Excel report: {e}")

# Function to show pie chart of expenses
def show_expense_pie_chart():
    # Fetching expense data
    expense_data = data.fetchRecord(query="SELECT item_name, item_price FROM expense_record")

    # Extracting item names and prices
    items = [record[0] for record in expense_data]
    prices = [record[1] for record in expense_data]

    # Creating a pie chart
    plt.figure(figsize=(8, 6))
    plt.pie(prices, labels=items, autopct='%1.1f%%', startangle=140)
    plt.title('Expense Distribution')
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    # Displaying the pie chart
    plt.show()

# Create the main window
ws = tk.Tk()
ws.title('Daily Expenses')

# Set ttk theme
ttk.Style().theme_use('clam')

# Variables
f = ('Times new roman', 14)
namevar = tk.StringVar()
amtvar = tk.IntVar(value=0)
dopvar = tk.StringVar()
limit_var = tk.IntVar(value=5000)  # Default limit set to 5000

# Frame widget
f2 = tk.Frame(ws)
f2.pack()

f1 = tk.Frame(
    ws,
    padx=10,
    pady=10,
)
f1.pack(expand=True, fill=tk.BOTH)

# Label widget
tk.Label(f1, text='Item Name:', font=f).grid(row=0, column=0, sticky=tk.E)
tk.Label(f1, text='Item Price:', font=f).grid(row=1, column=0, sticky=tk.E)
tk.Label(f1, text='Purchase Date:', font=f).grid(row=2, column=0, sticky=tk.E)
tk.Label(f1, text='Expense Limit:', font=f).grid(row=3, column=0, sticky=tk.E)

# Entry widgets
item_name = tk.Entry(f1, font=f, textvariable=namevar)
item_amt = tk.Entry(f1, font=f, textvariable=amtvar)
transaction_date = tk.Entry(f1, font=f, textvariable=dopvar)
limit_entry = tk.Entry(f1, font=f, textvariable=limit_var)

# Entry grid placement
item_name.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
item_amt.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
transaction_date.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=5)
limit_entry.grid(row=3, column=1, sticky=tk.W, padx=(10, 0), pady=5)

# Action buttons
buttons_frame = tk.Frame(f1)
buttons_frame.grid(row=4, columnspan=2, pady=10)

bg_color_primary = '#04C4D9'  # Light blue
bg_color_secondary = '#D9B036'  # Yellow
bg_color_chart = '#486966'  # Dark green

action_buttons = [
    ('Current Date', set_date),
    ('Save Record', save_record),
    ('Clear Entry', clear_entries),
    ('Exit', ws.destroy),
    ('Total Balance', total_balance),
    ('Update', update_record),
    ('Delete', delete_row),
    ('Generate PDF Report', generate_report),
    ('Generate Excel Report', generate_excel_report)
]

for i, (text, command) in enumerate(action_buttons):
    btn = tk.Button(
        buttons_frame,
        text=text,
        font=f,
        command=command,
        width=20 if 'Generate' in text else 15 if i != 0 else 0,
        bg=bg_color_primary if i == 0 else (bg_color_secondary if i in (1, 7, 8) else bg_color_primary),
        fg='white'
    )
    btn.grid(row=i//2, column=i%2, sticky=tk.EW, padx=(10, 0), pady=5)

# Add button to show pie chart
show_chart_btn = tk.Button(
    f1,
    text='Show Expense Pie Chart',
    font=f,
    bg=bg_color_chart,
    command=show_expense_pie_chart
)
show_chart_btn.grid(row=5, columnspan=2, sticky=tk.EW, padx=(10, 0), pady=5)

# Treeview widget
tv = ttk.Treeview(f2, columns=(1, 2, 3, 4), show='headings', height=8)
tv.pack(side="left")

# add heading to treeview
tv.column(1, anchor=tk.CENTER, stretch=tk.NO, width=70)
tv.column(2, anchor=tk.CENTER)
tv.column(3, anchor=tk.CENTER)
tv.column(4, anchor=tk.CENTER)
tv.heading(1, text="Serial no", )
tv.heading(2, text="Item Name", )
tv.heading(3, text="Item Price", )
tv.heading(4, text="Purchase Date", )

# binding treeview
tv.bind("<ButtonRelease-1>", select_record)
ws.bind("<Up>", lambda event: tv.selection_set(tv.prev(selected_rowid)))
ws.bind("<Down>", lambda event: tv.selection_set(tv.next(selected_rowid)))

# Vertical scrollbar
scrollbar = ttk.Scrollbar(f2, orient='vertical', command=tv.yview)
scrollbar.pack(side="right", fill="y")
tv.configure(yscrollcommand=scrollbar.set)

# calling function
fetch_records()

# Start the Tkinter event loop
ws.mainloop()


'''import tkinter as tk
from tkinter import ttk, messagebox
import datetime as dt
import mydb

# Importing Database class from mydb.py
from mydb import Database

# Create an instance of the Database class
data = Database('test.db')

# Initialize selected_rowid globally
selected_rowid = 0

# Functions for GUI operations
def save_record():
    data.insertRecord(item_name.get(), item_amt.get(), transaction_date.get())
    clear_entries()
    refresh_data()

def set_date():
    date = dt.datetime.now()
    dopvar.set(f'{date:%d %B %Y}')

def clear_entries():
    if item_amt.get() == 0:  # Check if the item price is default
        item_amt.delete(0, tk.END)
    item_name.delete(0, tk.END)
    transaction_date.delete(0, tk.END)

def fetch_records():
    for item in tv.get_children():
        tv.delete(item)

    f = data.fetchRecord('SELECT rowid, * FROM expense_record')
    for rec in f:
        tv.insert(parent='', index='end', iid=rec[0], values=(rec[0], rec[1], rec[2], rec[3]))

def select_record(event):
    global selected_rowid
    selected = tv.focus()
    val = tv.item(selected, 'values')

    try:
        selected_rowid = val[0]
        namevar.set(val[1])
        amtvar.set(val[2])
        dopvar.set(val[3])
    except Exception as ep:
        pass

def update_record():
    global selected_rowid

    selected = tv.focus()
    # Update record
    try:
        data.updateRecord(namevar.get(), amtvar.get(), dopvar.get(), selected_rowid)
        tv.item(selected, text="", values=(namevar.get(), amtvar.get(), dopvar.get()))
    except Exception as ep:
        messagebox.showerror('Error', ep)

    # Clear entry boxes
    clear_entries()
    refresh_data()

def total_balance():
    f = data.fetchRecord(query="SELECT SUM(item_price) FROM expense_record")
    total_spent = 0
    for i in f:
        total_spent = i[0]
    remaining_balance = 5000 - total_spent
    messagebox.showinfo('Current Balance', f"Total Expense: {total_spent}\nBalance Remaining: {remaining_balance}")

def refresh_data():
    fetch_records()

def delete_row():
    global selected_rowid
    data.removeRecord(selected_rowid)
    refresh_data()

def generate_report():
    timestamp = dt.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"expenses_report_{timestamp}.xlsx"
    data.generate_excel_report(filename)
    messagebox.showinfo("Success", f"Expense report generated successfully!\nFilename: {filename}")

# Create the main window
ws = tk.Tk()
ws.title('Daily Expenses')

# Variables
f = ('Times new roman', 14)
namevar = tk.StringVar()
amtvar = tk.IntVar(value=0)  # Set default value to 0
dopvar = tk.StringVar()

# Frame widget
f2 = tk.Frame(ws)
f2.pack()

f1 = tk.Frame(
    ws,
    padx=10,
    pady=10,
)
f1.pack(expand=True, fill=tk.BOTH)

# Label widget
tk.Label(f1, text='ITEM NAME', font=f).grid(row=0, column=0, sticky=tk.W)
tk.Label(f1, text='ITEM PRICE', font=f).grid(row=1, column=0, sticky=tk.W)
tk.Label(f1, text='PURCHASE DATE', font=f).grid(row=2, column=0, sticky=tk.W)

# Entry widgets
item_name = tk.Entry(f1, font=f, textvariable=namevar)
item_amt = tk.Entry(f1, font=f, textvariable=amtvar)
transaction_date = tk.Entry(f1, font=f, textvariable=dopvar)

# Entry grid placement
item_name.grid(row=0, column=1, sticky=tk.EW, padx=(10, 0))
item_amt.grid(row=1, column=1, sticky=tk.EW, padx=(10, 0))
transaction_date.grid(row=2, column=1, sticky=tk.EW, padx=(10, 0))

# Action buttons
cur_date = tk.Button(
    f1,
    text='Current Date',
    font=f,
    bg='#04C4D9',
    command=set_date,
    width=15
)

submit_btn = tk.Button(
    f1,
    text='Save Record',
    font=f,
    command=save_record,
    bg='#42602D',
    fg='white'
)

clr_btn = tk.Button(
    f1,
    text='Clear Entry',
    font=f,
    command=clear_entries,
    bg='#D9B036',
    fg='white'
)

quit_btn = tk.Button(
    f1,
    text='Exit',
    font=f,
    command=ws.destroy,
    bg='#D33532',
    fg='white'
)

total_bal = tk.Button(
    f1,
    text='Total Balance',
    font=f,
    bg='#486966',
    command=total_balance
)

update_btn = tk.Button(
    f1,
    text='Update',
    bg='#C2BB00',
    command=update_record,
    font=f
)

del_btn = tk.Button(
    f1,
    text='Delete',
    bg='#BD2A2E',
    command=delete_row,
    font=f
)

gen_report_btn = tk.Button(
    f1,
    text='Generate Excel Report',
    bg='#5E5E5E',
    command=generate_report,
    font=f
)

# grid placement
cur_date.grid(row=3, column=0, sticky=tk.EW, padx=(10, 0), pady=(10, 5))
submit_btn.grid(row=0, column=2, sticky=tk.EW, padx=(10, 0), pady=(10, 5))
clr_btn.grid(row=1, column=2, sticky=tk.EW, padx=(10, 0), pady=(10, 5))
quit_btn.grid(row=2, column=2, sticky=tk.EW, padx=(10, 0), pady=(10, 5))
total_bal.grid(row=0, column=3, sticky=tk.EW, padx=(10, 0), pady=(10, 5))
update_btn.grid(row=1, column=3, sticky=tk.EW, padx=(10, 0), pady=(10, 5))
del_btn.grid(row=2, column=3, sticky=tk.EW, padx=(10, 0), pady=(10, 5))
gen_report_btn.grid(row=3, column=2, columnspan=2, sticky=tk.EW, padx=(10, 0), pady=(10, 5))

# Treeview widget
tv = ttk.Treeview(f2, columns=(1, 2, 3, 4), show='headings', height=8)
tv.pack(side="left")

# add heading to treeview
tv.column(1, anchor=tk.CENTER, stretch=tk.NO, width=70)
tv.column(2, anchor=tk.CENTER)
tv.column(3, anchor=tk.CENTER)
tv.column(4, anchor=tk.CENTER)
tv.heading(1, text="Serial no")
tv.heading(2, text="Item Name", )
tv.heading(3, text="Item Price")
tv.heading(4, text="Purchase Date")

# Vertical scrollbar
scrollbar = ttk.Scrollbar(f2, orient='vertical', command=tv.yview)
scrollbar.pack(side="right", fill="y")
tv.configure(yscrollcommand=scrollbar.set)

# calling function
fetch_records()

# Start the Tkinter event loop
ws.mainloop() '''