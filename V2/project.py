import sys
from argparse import ArgumentParser
import csv
from datetime import datetime, date as datetime_date
from customtkinter import *
import os
import shutil
import hashlib as hash
import functools
import tabulate as tab
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as StatCanvas
import matplotlib.pyplot as plt 

"""
Run the following command to install all dependencies:
pip install -r requirements.txt



Sample account with sample data:
Username : a
Password : 1
"""


def main():
    parser = ArgumentParser()
    parser.add_argument('-w', '--write', action = 'store_true')
    parser.add_argument('-r', '--read', action = 'store_true')
    parser.add_argument('-g', '--get', choices = ['category', 'date'])
    parser.add_argument('-u', '--gui', action = 'store_true')
    parser.add_argument('-d', '--delete', action = 'store_true')
    parser.add_argument('-f', '--finance', choices = ['read', 'append'])
    parser.add_argument('-st', '--stats', action = 'store_true')
    parser.add_argument('-se', '--search', choices = ['finance', 'diary'])
    parser.add_argument('-re', '--report', action = 'store_true')
    args = parser.parse_args()
    if args.gui:
        GUI()
    elif args.write:
        write(authenticate(input('Name : '),input('Password : ')), input('Date of diary entry(leave empty to input todays date) \nFormat : dd/mm/yyyy: '), input('Category: '), input_entry())
    elif args.read:
        read(authenticate(input('Name : '),input('Password : ')), input('Date of diary entry (dd/mm/yyyy):'))
    elif args.get:
        get_info(authenticate(input('Name : '),input('Password : ')), args.get)
    elif args.finance:
        finance(authenticate(input('Name : '),input('Password : ')), args.finance)
    elif args.delete:
        del_acc(authenticate(input('Name : '),input('Password : ')))
    elif args.stats:
        stats(authenticate(input('Name : '),input('Password : ')))
    elif args.search:
        search_cli(authenticate(input('Name : '),input('Password : ')), args.search)
    elif args.report:
        get_report(authenticate(input('Name : '),input('Password : ')))
    else:
        create_acc(input('Name : '),input('Enter password : '), input('Current balance : '))

def create_acc(name, password, bal, gui = False):
    password = hash.sha256(bytes(password, 'utf-8')).hexdigest()
    try:
        os.chdir(f'{name}')
        if gui:
            return 'Username is not available.'
        print('Username is not available.')
        return False
    except FileNotFoundError:
        try:
            with open('passwords.csv', 'r') as pwd:
                pass
            with open('passwords.csv', 'a') as pwd:
                writer = csv.DictWriter(pwd, fieldnames = ['username', 'password'])
                writer.writerow({'username': name, 'password': password})
        except FileNotFoundError:
            with open('passwords.csv', 'a') as pwd:
                writer = csv.DictWriter(pwd, fieldnames = ['username', 'password'])
                writer.writeheader()
                writer.writerow({'username': name, 'password': password})

        os.mkdir(f'{name}')
        os.chdir(f'{name}')
        with open(f'diary.csv', 'a') as db:
            d_writer = csv.DictWriter(db, fieldnames = ['date', 'category', 'entry'])
            d_writer.writeheader()
        with open('finance.csv', 'a') as fin:
            fin_writer = csv.DictWriter(fin, fieldnames = ['id', 'date', 'detail', 'category', 'amount', 'dr_cr',  'balance'])
            fin_writer.writeheader()
            fin_writer.writerow({'id':0,'date': datetime.now().today().strftime('%d-%m-%Y'), 'detail': 'Initial Balance', 'category' : '--', 'amount': bal, 'dr_cr': 'debit', 'balance': bal})
        os.chdir(os.pardir)
        return True

def del_acc(name):
    shutil.rmtree(f'{name}')
    with open('passwords.csv','r') as db:
        reader = csv.DictReader(db, fieldnames = ['username', 'password'])
        rows = []
        for row in reader:
            if row['username'] == name:
                continue
            rows.append(row)
    os.remove('passwords.csv')
    with open('passwords.csv','w') as db:
        writer = csv.DictWriter(db, fieldnames = ['username', 'password'])
        writer.writeheader()
        writer.writerows(rows[1::])

def input_entry():
    print("Entry (Type 'end' on a new line when done): \n\n")
    entry = ''
    while True:
        line = input()
        if line.lower().strip() != 'end':
            entry += '\n'+line
        else:
            break
    return entry

def authenticate(name, password, gui = False):
    access = False
    password = hash.sha256(bytes(password, 'utf-8')).hexdigest()
    try:
        with open('passwords.csv', 'r') as pwd:
            pass
    except FileNotFoundError:
        with open('passwords.csv', 'w') as pwd:
            writer = csv.DictWriter(pwd, fieldnames = ['username', 'password'])
            writer.writeheader()

    with open('passwords.csv', 'r') as pwd:
        reader = csv.DictReader(pwd)
        for row in reader:
            if row['username'] == name and row['password'] == password:
                access = True
        if access:
            if gui:
                return True
            return name
        else:
            if gui:
                return 'Wrong username or password.'
            print('Wrong username or password!')
            sys.exit()

def read(name, date):
    if convert_Date(date) == False:
        print('Invalid date.')
        return

    os.chdir(f'{name}')
    with open('diary.csv','r') as file:
        reader = csv.DictReader(file)
        entry = [row['entry'] for row in reader if row['date'] == date]
        if entry:
            print('\n', *entry)
            os.chdir(os.pardir)
            return entry
        else:
            print('\nNo entry on that date or invalid date.')
            os.chdir(os.pardir)

def write(name, date, category, entry, gui = False):
    os.chdir(name)
    with open('diary.csv', 'a') as file:
        writer = csv.DictWriter(file, fieldnames = ['date', 'category', 'entry'])
        if date:
            validation = convert_Date(date)
            if validation == False:
                if gui:
                    os.chdir(os.pardir)
                    return 'Invalid date.'
                else:
                    print('Invalid date.')
                    os.chdir(os.pardir)
                    return
        else:
            date = str(datetime.now().date().strftime('%d-%m-%Y'))
        if date in get_info(name, 'date', False):
            if gui:
                os.chdir(os.pardir)
                return 'Entry already exists on that date.'

            print('\nEntry already exists on that date.')
            os.chdir(os.pardir)
            return
        writer.writerow({'date': date, 'category': category, 'entry': entry})

        if gui:
            os.chdir(os.pardir)
            return True
        print('\nEntry added.')
        os.chdir(os.pardir)

def get_info(name, item, print_res = True):
    try:
        os.chdir(f'{name}')
        flag = True
    except FileNotFoundError:
        flag = False

    with open('diary.csv', 'r') as db:
        reader = csv.DictReader(db)
        items = [row[item] for row in reader ]
        items = set(items)

    if flag:
        os.chdir(os.pardir)

    if print_res:
        print(f'\n{item.title()}:')
        for i in items:
            print('   '+i)
        return
    return items

def finance(name, action = 'append', date = None, detail = None, category = None, amount = None, dr_cr = None, gui = False):
    os.chdir(name)
    with open('finance.csv', 'r') as file:
        reader = csv.DictReader(file)

        if action =='read':
            table_data = []
            for row in reader:
                table_data.append([row['date'], row['detail'], row['category'], row['amount'], row['dr_cr'].title(), row['balance']])
            if len(table_data) > 0:
                print(tab.tabulate(table_data, headers=['Date', 'Detail', 'Category', 'Amount', 'Dr/Cr', 'Balance'], tablefmt='grid'))
                return
            print('\nNo data available.')

        elif action == 'append':
            balance = float([row['balance'] for row in reader][-1])

            if not gui:
                date = input('Date: ')
                detail = input('Detail: ')
                categories = ['Loan', 'Education', 'Salary', 'Groceries', 'Utilities','Entertainment', 'Clothing', 'Transportation', 'Dining out', 'Miscellaneous']
                while True:
                    category = input('Choose from: \n' + '\n'.join(categories)+'\n'+'Category: ')
                    if category.title() in categories:
                        break
                    else:
                        print('Invalid category.')
                while True:
                    try:
                        amount = float(input('Amount: '))
                        
                        break
                    except:
                        print('Invalid amount.')
                dr_cr = input('Debit or credit: ')
                while dr_cr not in ['debit', 'credit']:
                    dr_cr = input('Debit or credit: ')
                if dr_cr == 'credit' and amount > balance:
                    print('\nInsufficient balance.')
                    return
            
            if convert_Date(date) == False:
                if gui:
                    os.chdir(os.pardir)
                    return 'Invalid date.'
                else:
                    os.chdir(os.pardir)
                    print('Invalid date.')
                    return
            
            
            if dr_cr == 'credit':
                if float(amount) > balance:
                    os.chdir(os.pardir)
                    return 'Insufficient balance.'
                balance-=float(amount)
            else:
                balance += float(amount)

            with open('finance.csv', 'a') as file:
                writer = csv.DictWriter(file, fieldnames = ['date', 'detail', 'category', 'amount', 'dr_cr', 'balance'])
                writer.writerow({'date': date, 'detail': detail, 'category' : category, 'amount': amount,'dr_cr': dr_cr, 'balance': balance})
            if gui:
                os.chdir(os.pardir)
                return 'Transaction added.'
            else:
                os.chdir(os.pardir)
                print('\nTransaction recorded.')

def convert_Date(date):
    try:
        return datetime_date(int(date.split('-')[2]), int(date.split('-')[1]), int(date.split('-')[0]))
    except:
        return False

def stats(name, gui = False):
    os.chdir(name)
    reader = list(csv.DictReader(open('finance.csv', 'r')))
    if len(reader) == 1:
        if gui:
            os.chdir(os.pardir)
            return 'No data available.'
        else:
            os.chdir(os.pardir)
            print('\nNo data available.')
            return

    items = set([row['detail'] for row in reader if row['detail'] != 'Initial Balance'])
    #Amount spent in a month is working 
    amount_month_cr = sum([int(row['amount']) for row in reader if (row['detail'] != 'Initial Balance') and (row['dr_cr'] == 'credit') and (datetime.now().date().month == convert_Date(row['date']).month) and (datetime.now().date().year == convert_Date(row['date']).year)])

    #Amount recieved in a month is working
    amount_month_dr = sum([int(row['amount']) for row in reader if (row['detail'] != 'Initial Balance') and (row['category'] != 'Loan')  and (row['dr_cr'] == 'debit') and (datetime.now().date().month == convert_Date(row['date']).month) and (datetime.now().date().year == convert_Date(row['date']).year)])

    items_amount = []
    for item in items:
        items_amount.append((item, sum([int(row['amount']) for row in reader if (row['detail'] == item) and (row['dr_cr'] == 'credit') and (datetime.now().date().month == convert_Date(row['date']).month) and (datetime.now().date().year == convert_Date(row['date']).year)] )))

    items_amount = [row['detail'] for row in reader if (row['dr_cr'] == 'credit') and (datetime.now().date().month == convert_Date(row['date']).month) and (datetime.now().date().year == convert_Date(row['date']).year)]

    item_count = [(str(i), items_amount.count(i)) for i in items ]
    most_frequent_item = []
    for item in item_count:
        if max([i[1] for i in item_count]) != 0 and item[1] == max([i[1] for i in item_count]):
            most_frequent_item.append((str(item[0]), max([i[1] for i in item_count])))

    categories = set([row['category'] for row in reader if row['category'] not in ['--', 'Loan', 'Salary']])
    categories = list(categories)
    amount_categories = {}
    for category in categories:
        amount = sum([int(row['amount']) for row in reader if (row['detail'] != 'Initial Balance') and (row['dr_cr'] == 'credit') and (datetime.now().date().month == convert_Date(row['date']).month) and (datetime.now().date().year == convert_Date(row['date']).year) and (row['category'] == category)])
        amount_categories[amount] = category

    most_spent_category = (max(amount_categories.keys()), amount_categories[max(amount_categories.keys())] )


    amount_items = {}
    for item in items:
        amount = sum([int(row['amount']) for row in reader if (row['detail'] != 'Initial Balance') and (row['dr_cr'] == 'credit') and (datetime.now().date().month == convert_Date(row['date']).month) and (datetime.now().date().year == convert_Date(row['date']).year) and (row['category'] == category)])
        amount_items[amount] = category

    items_Spent = [(row['detail'], row['amount']) for row in reader if (row['detail'] != 'Initial Balance') and (row['dr_cr'] == 'credit') and (datetime.now().date().month == convert_Date(row['date']).month) and (datetime.now().date().year == convert_Date(row['date']).year) ]

    transactions = len(reader)
    expensive_item = ('', 0)
    for i in items_Spent:
        if int(i[1]) > int(expensive_item[1]):
            expensive_item = (i[0], i[1])
    balance = [row['balance'] for row in reader][-1]
    if not gui:
        print(*items)
        print('Amount spent in this month :', amount_month_cr)
        print('Amount recieved in this month :', amount_month_dr)
        print('Most amount spent on an item in this month :', expensive_item[0], 'for', expensive_item[1])
        print("Most frequently bought items in this month :", *most_frequent_item)
        print("Category with highest spendings :", most_spent_category)
        os.chdir(os.pardir)
        return
    else:
        os.chdir(os.pardir)
        return {'Items': items, "Money spent": amount_month_cr, "Money recieved": amount_month_dr, "Most expensive item": expensive_item, "Most frequently bought item": most_frequent_item, "Category with highest spending" : most_spent_category, "Categories and amount spent": amount_categories, "Number of transactions" : transactions, "Balance" : balance}

def search_cli(name, domain,data = None, gui = False):
    os.chdir(name)

    if domain == 'diary':
        df = pd.read_csv('diary.csv')

        if not(gui):
            data = {'date' : input('Date (Leave empty for any) : '), 'category' : input('Category (Leave empty for any) : ')}

        query = ' & '.join([f"{key} == '{value}'" for key, value in data.items() if value])
        if query == '':
            os.chdir(os.pardir)
            return df
        res = df.query(query)
        if not(gui):
            print(f'{len(res)} Results\n----------------------------------')
            for i in range(len(res)):
                print(res.iloc[i,0])
                print(res.iloc[i,1], '\n')
                print(res.iloc[i,2], '\n----------------------------------')
            os.chdir(os.pardir)
            return
        os.chdir(os.pardir)
        return res
        
    else:
        df = pd.read_csv("finance.csv")

        if not(gui):
            try:
                data = {'date' : input('Date (Leave empty for any) : '), 'detail' : input('Detail (Leave empty for any) : '), 'amount' : int(input('Amount (Leave empty for any) : ')), 'dr_cr': input('Debit or Credit (Leave empty for any) : ')}
            except:
                sys.exit("Amount should be a number")
        query = []
        for key, value in data.items():
            if value!= '':
                if key == 'amount':
                    query.append(f"{key} == {value}")
                else:
                    query.append(f"{key} == '{value}'")
        query =' & '.join(query)

        if query == '':
            os.chdir(os.pardir)
            return df
        
        results = df.query(query)
        if gui:
            os.chdir(os.pardir)
            return results

        print(f'{len(results)} Results\n----------------------------------')
        print(tab.tabulate(results, tablefmt='grid', headers=["Sr NO.", "Date", "Detail", "Amount", "Dr/Cr", "Balance"]))

        os.chdir(os.pardir)
        return
        
def get_report(name, gui = False):
    items, spent, recieved, most_expensive, most_frequent, expensive_category, categories_amount, transactions, balance = stats(name, gui = True).values()
    report = f"In this month, {spent} has been spent and {recieved} has been recieved. "
    categories = ['Loan', 'Salary', 'Groceries', 'Utilities','Entertainment', 'Clothing', 'Transportation', 'Dining out', 'Miscellaneous']
    if expensive_category[1] in ['Entertainment', 'Dining out']:
        report += f" The category in which most money is spent is {expensive_category[1]}. This spendage is out of control and has to be reduced. "
    elif expensive_category[1]  == 'Clothing' and expensive_category[0] > 150:
        report += f"{expensive_category[0]} is spent on just clothing. This also has to be reduced. "
    elif expensive_category[1] == 'Groceries' and (expensive_category[0]*100) / spent >=  70:
        report += f"Groceries are being spent on a high percentage of the total spending. This should be reduced as much as possible. "
    else:
        report += f"{expensive_category[1]} with a total of {expensive_category[0]} is the category with most money spent. Its suggested to reduce the spendage in this category. "
    if float(balance) < 200:
        report += f"The balance is {balance}, which is very low. It is essential to maintain a balance above 200. "
    if gui:
        report1 = ""
        for i in range(len(report)):
            if i%66 == 0 and i != 0:
                if report[i].isalpha():
                    report1 += report[i] + '-\n'
                else:
                    report1 += report[i] + '\n'
            else:
                report1 += report[i]
        return report1
    print("Financial report of this month : \n", report)
    return 

def GUI():
    def close():
        plt.close('all')
        app.quit()
        app.destroy()

    app = CTk()
    app.geometry('1000x600')
    app.title('Life-Record')
    app.resizable(False, False)
    app.protocol("WM_DELETE_WINDOW", close)

    main = CTkFrame(app, width = 800, height = 600, corner_radius=0, border_color='#404040', border_width = 2)
    main.pack_propagate(False)
    main.place(x=200, y=0)

    global title
    title = CTkLabel(app, text = 'Log in', font = ('Georgia', 40), fg_color='#2b2b2b')
    title.pack(anchor = CENTER, pady = 10)

    global name
    name = None

    def login():
        global name
        for widget in main.winfo_children():
            if widget._name != '!ctklabel':
                widget.destroy()

        title.configure(text = 'Log in')
        CTkButton(main, text = '', width = 650, height = 450, fg_color = '#4d4b48', hover_color='#4d4b48').place(x=75, y=75)
        error = CTkLabel(main, text = '', font = ('georgia', 20), bg_color='#4d4b48')
        error.place(x=110, y= 240)
        CTkLabel(main, text = 'Username', font = ('georgia', 20), bg_color = '#4d4b48').place(x=100, y=100)
        CTkLabel(main, text = 'Password', font = ('georgia', 20),bg_color='#4d4b48').place(x=100, y=150)
        usr = CTkEntry(main, font = ('georgia', 20), bg_color='#4d4b48')
        usr.place(x=200, y=100)
        pwd = CTkEntry(main, show = '*' , font = ('georgia', 20), bg_color='#4d4b48')
        pwd.place(x=200, y=150)

        def done():
            global name
            res = authenticate(usr.get(), pwd.get(), gui = True)
            if res == True:
                name = usr.get()
                dashboard()
            else:
                error.configure(text = res)

        action = CTkButton(main, text = 'Log in', font = ('georgia',20), command = done, bg_color='#4d4b48')
        action.place(x=350, y=150)
        action_switch = CTkButton(main, text = 'Dont have an account', font = ('georgia',15), command = lambda : signup(usr, pwd, action, action_switch, error), bg_color='#4d4b48')
        action_switch.place(x=350, y=100)

    def signup(usr, pwd, action, action_switch, error):

        title.configure(text = 'Sign Up')
        action_switch.configure(text = 'Already have an account.', command = login, bg_color='#4d4b48')
        CTkLabel(main, text = 'Balance', font = ('georgia',20), bg_color='#4d4b48').place(x=100, y=200)
        global bal
        bal = CTkEntry(main, font = ('georgia',20), bg_color='#4d4b48')
        bal.place(x=200, y=200)

        def done():
            global name
            global bal
            try:
                bal = float(bal.get())
            except:
                error.configure(text = 'Balance should be a number.')
                return

            if usr.get() and pwd.get():
                res = create_acc(usr.get(), pwd.get(), bal, gui = True)
                if res == True:
                    name = usr.get()
                    dashboard()
                else:
                    error.configure(text = res)

            else:
                error.configure(text = 'All fields are required.')

        action.configure(text = 'Sign up', command = done)

    login()

    menu = CTkFrame(app, width = 200, height = 600, corner_radius = 0, border_color='#404040', border_width = 2)
    menu.pack_propagate(False)
    menu.place(x=0, y=0)

    def gui_write():
        for widget in main.winfo_children():
            widget.destroy()

        frame = CTkScrollableFrame(main, width = 800, height = 520, border_width=1 , fg_color='#4D4B48', border_radius = 0)
        frame.pack_propagate(False)
        frame.place(x=0, y=80)
        CTkLabel(frame, text = 'Date', font = ('georgia', 20)).grid(row = 2, column =1, sticky = W, padx = 5)
        date_entry = CTkEntry(frame,width = 200 , font = ('georgia', 20))
        date_entry.grid(row = 2, column = 2, sticky = W, padx = 10)

        CTkLabel(frame, text = 'Category', font = ('georgia', 20)).grid(row = 3, column =1, sticky = W, padx = 5, pady = 5)
        category_entry = CTkEntry(frame,width = 200 , font = ('georgia', 20))
        category_entry.grid(row = 3, column = 2, stick = W, padx = 10)

        CTkLabel(frame, text = 'Entry', font = ('georgia', 20)).grid(row = 4, column =1, sticky = W, padx = 5)
        entry_entry = CTkTextbox(frame, width = 670, height = 400, font = ('georgia', 20))
        entry_entry.grid(row = 4, column = 2, padx = 10, stick = N)

        def save():
            date = date_entry.get()
            category = category_entry.get()
            entry = entry_entry.get('1.0', END)
            if date == '' or category == '' or entry == '':
                error.configure(text = 'Please fill all fields.')
                return
            flag = write(name, date, category, entry, True)
            if flag != True:
                error.configure(text = flag)
            else:
                date_entry.delete(0, END)
                category_entry.delete(0, END)
                entry_entry.delete('1.0', END)
                error.configure(text = 'Entry added')

        CTkButton(frame, text = 'Save', font = ('georgia', 20), command = save).grid(row =5, column =2, sticky = E, padx=15, pady = 5)
        error = CTkLabel(frame, text = '', font = ('georgia', 20))
        error.place(x=100,y=480)
        
    def dashboard():
        global name
        global title
        if name == None:
            return

        for widget in main.winfo_children():
            widget.destroy()

        title.configure(text = 'Dashboard')
        CTkButton(main, text = '', width = 650, height = 450, fg_color = '#4d4b48', hover_color='#4d4b48').place(x=75, y=75)


        CTkButton(main, text = '', height = 100, width = 230, hover_color='#1F6AA5', fg_color = '#1F6AA5', bg_color="#4d4b48").place(x = 145, y = 100)
        CTkButton(main, text = '', height = 100, width = 230, hover_color='#1F6AA5', fg_color = '#1F6AA5', bg_color="#4d4b48").place(x = 425, y = 100)

        CTkLabel(main, text = 'Entries', font = ('roboto', 30), bg_color = '#1F6AA5').place(x=435, y=115)
        entries = CTkLabel(main, text = len(get_info(name, 'date', False)), font = ('roboto', 30), bg_color = '#1F6AA5')
        entries.place(x=435, y=150)

        CTkButton(main, text = '+', font = ('roboto', 20), width = 28,  fg_color = '#1E5994', bg_color = '#1F6AA5', command = gui_write).place(x=625, y=103)
        CTkButton(main, text = '+', font = ('roboto', 20), width = 28,  fg_color = '#1E5994', bg_color = '#1F6AA5', command = add_transaction).place(x=346, y=103)
        CTkLabel(main, text = 'Balance', font = ('roboto', 30), bg_color = '#1F6AA5').place(x=155, y=115)

        os.chdir(name)
        with open('finance.csv', 'r') as f:
            reader = csv.DictReader(f)
            bal = [row['balance'] for row in reader][-1]
        os.chdir(os.pardir)
        CTkLabel(main, text = bal, font = ('roboto', 30), bg_color = '#1F6AA5').place(x=155, y=155)

    def diary():
        if name == None:
            return
        for widget in main.winfo_children():
            widget.destroy()

        title.configure(text = 'Diary')

        frame = CTkScrollableFrame(main, width = 800, height = 515, fg_color='grey', corner_radius=0, border_width=1)

        frame.pack_propagate(False)
        frame.place(x=0, y = 95)

        def search():
            date = search_date.get()
            category = search_category.get()
            results = search_cli(name, 'diary', data = {'date' : date, 'category' : category}, gui = True)
            for widget in frame.winfo_children():
                widget.destroy()
            CTkLabel(frame, text = 'Date   ', font = ('georgia', 17)).grid(row = 1, column = 1, padx = 5)
            CTkLabel(frame, text = 'Category', font = ('georgia', 17)).grid(row = 1, column = 2, padx = 60)
            CTkLabel(frame, text = 'Entry', font = ('georgia', 17)).grid(row=1, column = 3)
            
            
            for i, row in enumerate(range(len(results)), start = 2):
                CTkLabel(frame, text = results.iloc[row,0], font = ('roboto', 15)).grid(row = i, column = 1, padx = 5)
                CTkLabel(frame, text = results.iloc[row,1], font = ('roboto', 15)).grid(row = i, column = 2, padx = 60)
                CTkButton(frame, text = 'Read', width = 100, height = 15, font = ('roboto', 15), command = functools.partial(gui_read, {'date' : results.iloc[row,0], 'category' : results.iloc[row, 1],  'entry' : results.iloc[row,2]})).grid(row = i, column = 3)
        

        CTkLabel(frame, text = 'Date   ', font = ('georgia', 17)).grid(row = 1, column = 1, padx = 5)
        CTkLabel(frame, text = 'Category', font = ('georgia', 17)).grid(row = 1, column = 2, padx = 60)
        CTkLabel(frame, text = 'Entry', font = ('georgia', 17)).grid(row=1, column = 3)

        CTkLabel(frame, text = '').grid(row = 1, column = 1)
        search_frame = CTkFrame(main, width = 800, height = 33, fg_color='#63666A',corner_radius=0, border_width=1)
        search_frame.place(x=0, y=62)
        search_frame.pack_propagate(False)
        CTkLabel(search_frame, text = 'Date', font = ('georgia', 17), bg_color='#63666A').pack(side = LEFT, padx = (30,10))
        search_date = CTkEntry(search_frame, font = ('georgia', 17), bg_color='#63666A', width = 120)
        search_date.pack(side = LEFT)
        
        CTkLabel(search_frame, text = 'Category', font = ('georgia', 17), bg_color='#63666A').pack(side = LEFT, padx = (30, 10))
        search_category = CTkEntry(search_frame, font = ('georgia', 17), bg_color='#63666A', width = 120)
        search_category.pack(side = LEFT)

        CTkButton(search_frame, text = '+', font = ('roboto', 17), width = 28,  fg_color = '#1E5994', bg_color = '#63666A', command = gui_write).pack(side = RIGHT, padx = 5)
        search_btn = CTkButton(search_frame, text = 'Search 🔎', font = ('georgia',17), width = 50, command = search)
        search_btn.pack(side = RIGHT, padx = 10)


        def gui_read(row):
            for widget in main.winfo_children():
                widget.destroy()

            entry_frame = CTkTextbox(main, font = ('georgia', 17), corner_radius = 0, width = 650, height = 500, fg_color = '#1E5994')
            entry_frame.place(x=0, y = 80)
            entry = row['entry'].split('\\n')
            entry_frame.insert('0.0', row['date']+'\n'+row['category']+'\n'+'\n'+'\n'.join(entry))
            entry_frame.configure(state = 'disabled')

        os.chdir(name)
        with open('diary.csv', 'r') as db:
            reader = csv.DictReader(db)
            for i, row in enumerate(reader, start = 3):
                CTkLabel(frame, text = row['date'], font = ('roboto', 15)).grid(row = i, column = 1, padx = 5)
                CTkLabel(frame, text = row['category'], font = ('roboto', 15)).grid(row = i, column = 2, padx = 60)
                CTkButton(frame, text = 'Read', width = 100, height = 15, font = ('roboto', 15), command = functools.partial(gui_read, row)).grid(row = i, column = 3)

        os.chdir(os.pardir)

    def add_transaction():
        for widget in main.winfo_children():
            widget.destroy()

        frame = CTkScrollableFrame(main, width = 800, height = 515, fg_color='#4D4B48', corner_radius=0)
        frame.pack_propagate(False)
        frame.place(x=0, y = 90)
        CTkLabel(frame, text = 'Date', font = ('georgia', 25)).grid(row=1, column =1, pady = 10)

        date = CTkEntry(frame, width = 200, font = ('georgia',25))
        date.grid(row = 1, column = 2)
        CTkLabel(frame, text = 'Detail', font = ('georgia', 25)).grid(row = 2, column = 1, padx = 5)
        detail = CTkEntry(frame, width = 200, font = ('georgia',25))
        detail.grid(row = 2, column = 2, padx = 10)
        CTkLabel(frame, text = 'Category', font = ('georgia', 25)).grid(row = 3, column = 1, padx = 5, pady = 10)
        category = CTkOptionMenu(frame, values = ['Groceries', 'Education', 'Salary', 'Loan', 'Utilities','Entertainment', 'Clothing', 'Transportation', 'Dining out', 'Miscellaneous'], width = 200, font = ('georgia',25))
        category.grid(row = 3, column = 2, padx = 5)
        CTkLabel(frame, text = 'Dr/Cr', font = ('georgia', 25)).grid(row = 4, column = 1, padx = 5)
        dr_cr = CTkOptionMenu(frame, values = ['Debit', 'Credit'], width = 200, font=  ('georgia',25))
        dr_cr.grid(row = 4, column = 2, padx = 10)
        CTkLabel(frame, text = 'Amount', font = ('georgia', 25)).grid(row =5, column = 1, padx = 5)
        amount = CTkEntry(frame, width = 200, font = ('georgia', 25))
        amount.grid(row =5, column = 2, pady = 10)
        error = CTkLabel(frame, text = '', font = ('georgia', 25), text_color = '#6b150f')
        error.place(x=7, y= 220)

        def enter():
            if date.get() == '' or detail.get() == '' or amount == '':
                error.configure(text = 'All fields are required.')
                return
            if status:=finance(name, 'append', date.get(), detail.get(), category.get(), amount.get(), dr_cr.get().lower(), gui = True):
                if status != 'Transaction added.':
                    error.configure(text = status, text_color = 'red')
                    return
                error.configure(text = status, text_color = '#2F4F4F')

        CTkButton(frame, text = 'Enter', font = ('georgia', 25), command = enter).grid(row =6, column = 5, sticky = E, padx = 10)
        
    def gui_finance():
        maxlen = 150
        if name == None:
            return
        for widget in main.winfo_children():
            widget.destroy()

        title.configure(text = 'Finance')

        frame = CTkScrollableFrame(main, width = 790, height = 515, fg_color='grey', corner_radius=0, border_width=1, scrollbar_button_color='dark grey')
        frame.pack_propagate(False)
        frame.place(x=0, y = 95)

        for i in range(1,6):
            frame.grid_columnconfigure(i, minsize = maxlen)

        CTkLabel(frame, text = 'Date', font = ('georgia', 17)).grid(row = 1, column = 1, sticky = 'nsew')
        CTkLabel(frame, text = 'Detail', font = ('georgia', 17)).grid(row = 1, column = 2, padx = 15)
        CTkLabel(frame, text = 'Category', font = ('georgia', 17)).grid(row = 1, column = 3)
        CTkLabel(frame, text = 'Amount', font = ('georgia', 17)).grid(row = 1, column = 4, padx = 30)
        CTkLabel(frame, text = 'Dr/Cr', font = ('georgia', 17)).grid(row = 1, column =5)

        def search():
            dr_cr = search_dr_cr.get()
            if dr_cr == 'Dr':
                dr_cr = 'debit'
            elif dr_cr == 'Cr':
                dr_cr = 'credit'
            else:
                dr_cr = ''
            data = {
                'date': search_date.get(),
                'detail': search_detail.get(),
                'category' : search_category.get(),
                'amount': search_amount.get(),
                'dr_cr': dr_cr,
                'balance': ''
            }

            results = search_cli(name, domain='finance', data = data, gui = True)
            
            for widget in frame.winfo_children():
                widget.destroy()
            for i in range(1,6):
                frame.grid_columnconfigure(i, minsize = maxlen)

            CTkLabel(frame, text = 'Date', font = ('georgia', 17)).grid(row = 1, column = 1, sticky = 'nsew')
            CTkLabel(frame, text = 'Detail', font = ('georgia', 17)).grid(row = 1, column = 2, padx = 15)
            CTkLabel(frame, text = 'Category', font = ('georgia', 17)).grid(row = 1, column = 3)
            CTkLabel(frame, text = 'Amount', font = ('georgia', 17)).grid(row = 1, column = 4, padx = 30)
            CTkLabel(frame, text = 'Dr/Cr', font = ('georgia', 17)).grid(row = 1, column =5)

            for i, row in enumerate(range(len(results)), start = 2):
                CTkLabel(frame, text = results.iloc[row,0], font = ('roboto', 15), wraplength = maxlen).grid(row = i, column = 1, padx = 5)
                CTkLabel(frame, text = results.iloc[row,1], font = ('roboto', 15), wraplength = maxlen).grid(row = i, column = 2, padx = 5)
                CTkLabel(frame, text = results.iloc[row,2], font = ('roboto', 15), wraplength = maxlen).grid(row = i, column = 3, padx = 5)
                CTkLabel(frame, text = results.iloc[row,3], font = ('roboto', 15), wraplength = maxlen).grid(row = i, column = 4, padx = 5)
                CTkLabel(frame, text = results.iloc[row,4], font = ('roboto', 15), wraplength = maxlen).grid(row = i, column = 5, padx = 5)
            CTkButton(frame, text = '+', font = ('roboto', 15), width = 28,  fg_color = '#1E5994', bg_color = 'grey', command = add_transaction).place(x=602, y=2)


        CTkLabel(frame, text = '').grid(row = 1, column = 1)
        search_frame = CTkFrame(main, width = 800, height = 33, fg_color='#63666A',corner_radius=0)
        search_frame.place(x=0, y=62)
        search_frame.pack_propagate(False)
        CTkLabel(search_frame, text = 'Date', font = ('georgia', 16), bg_color='#63666A').pack(side = LEFT, padx  =(10,10))
        search_date = CTkEntry(search_frame, font = ('roboto', 16), width = 100, bg_color='#63666A')
        search_date.pack(side = LEFT, padx = (0,10))

        CTkLabel(search_frame, text = 'Detail', font = ('georgia', 16), bg_color='#63666A').pack(side = LEFT, padx = (0,10))
        search_detail = CTkEntry(search_frame, font = ('roboto', 16), bg_color='#63666A', width = 100)
        search_detail.pack(side = LEFT, padx = (0,10))

        CTkLabel(search_frame, text = 'Category', font = ('georgia', 16), bg_color='#63666A').pack(side = LEFT, padx = (0,10))
        search_category = CTkEntry(search_frame, font = ('roboto', 16), bg_color='#63666A', width = 100)
        search_category.pack(side = LEFT, padx = (0,7))
        CTkLabel(search_frame, text = 'Amount', font = ('georgia', 16), bg_color='#63666A').pack(side = LEFT, padx = (0,10))
        search_amount = CTkEntry(search_frame, font = ('roboto', 16), bg_color='#63666A', width = 50)
        search_amount.pack(side = LEFT, padx = (0,10))

        search_dr_cr = CTkOptionMenu(search_frame, font = ('roboto', 16), bg_color='#63666A', width = 50,values=['Any', 'Dr', 'Cr'])
        search_dr_cr.pack(side = LEFT, padx = (0,10))
        search_btn = CTkButton(search_frame, text = 'Search🔎', font = ('georgia',17), width = 50, command = search)
        search_btn.pack(side = LEFT, padx = (0,10))

        CTkButton(frame, text = '+', font = ('roboto', 15), width = 28,  fg_color = '#1E5994', bg_color = 'grey', command = add_transaction).place(x=760, y=2)

        os.chdir(name)
        with open('finance.csv', 'r') as db:
            reader = csv.DictReader(db)
            for i, row in enumerate(reader, start = 2):
                CTkLabel(frame, text = row['date'], font = ('roboto', 15), wraplength = maxlen).grid(row = i, column = 1, padx = 5)
                CTkLabel(frame, text = row['detail'], font = ('roboto', 15), wraplength = maxlen).grid(row = i, column = 2, padx = 5)
                CTkLabel(frame, text = row['category'], font = ('roboto', 15), wraplength = maxlen).grid(row = i, column = 3, padx = 5)
                CTkLabel(frame, text = row['amount'], font = ('roboto', 15), wraplength = maxlen).grid(row = i, column = 4, padx = 5)
                CTkLabel(frame, text = row['dr_cr'], font = ('roboto', 15), wraplength = maxlen).grid(row = i, column = 5, padx = 5)
        os.chdir(os.pardir)

    def gui_del_acc(name):
        if name != None:
            del_acc(name)
            name = None
            login()

    def gui_stats():
        if name == None:
            return
        for widget in main.winfo_children():
            widget.destroy()

        title.configure(text = 'Statistics')

        data = stats(name, gui = True)
        
        frame = CTkScrollableFrame(main, width = 780, height =515 ,fg_color='grey')
        frame.pack_propagate(False)
        frame.place(x=0, y=85)

        if type(data) == str:
            CTkLabel(frame, text = data, font = ('roboto', 15)).grid(row = 1, column =1)
            
        else:
            fig, ax = plt.subplots(figsize = (4,4))
            plt.tight_layout()
            fig.patch.set_color('grey')
            for text in ax.texts:
                text.set_fontsize(5)
                text.set_position([text.get_position()[0], text.get_position()[1] - 0.15])
            wedges, texts, autotexts = ax.pie(data["Categories and amount spent"].keys(), labels = data['Categories and amount spent'].values(), startangle=90, autopct= '%1.1f%%', colors = ["#FF7F50", "#FFD700", "#87CEFA", "#32CD32", "#FF69B4", "#00CED1", "#EE82EE", "#FFA500", "#7FFF00", "#FF4500", "#ADFF2F"])
            plt.setp(wedges, edgecolor='black', linewidth=1.5)
            ax.axis('equal')


            CTkLabel(frame, text = "Month", font = ("Roboto", 20)).grid(row = 1, column = 1, sticky = W)
            CTkLabel(frame, text = datetime.now().strftime("%B"), font = ("Roboto", 20)).grid(row = 1, column = 2, padx = 10)
            CTkLabel(frame, text = "Money spent", font = ("Roboto", 20)).grid(row = 2, column = 1, sticky = W)
            CTkLabel(frame, text = data['Money spent'], font = ("Roboto", 20)).grid(row = 2, column = 2)
            CTkLabel(frame, text = "Money recieved (Loans excluded)", font = ("Roboto", 20)).grid(row = 3, column = 1, sticky = W)

            CTkLabel(frame, text = data['Money recieved'], font = ("Roboto", 20)).grid(row = 3, column = 2)
            CTkLabel(frame, text = '', font = ("Roboto", 20)).grid(row = 4, column = 1)

            CTkLabel(frame, text = "Category with most spending", font = ("Roboto", 20)).grid(row = 5, column = 1, sticky = W)
            CTkLabel(frame, text = "Category", font = ("Roboto", 20)).grid(row = 6, column = 1, sticky = W)
            CTkLabel(frame, text = data["Category with highest spending"][1], font = ("Roboto", 20)).grid(row = 6, column = 2)
            CTkLabel(frame, text = "Amount", font = ("Roboto", 20)).grid(row = 7, column = 1, sticky = W)
            CTkLabel(frame, text = data["Category with highest spending"][0], font = ("Roboto", 20)).grid(row = 7, column = 2)
            
            CTkLabel(frame, text = '\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n').grid(row = 8,column = 1)

            canvas = StatCanvas(fig, master=frame)
            canvas.draw()
            canvas.get_tk_widget().place(x=20,y=290)
            CTkLabel(frame, text = "Most expensive item", font = ("Roboto", 20)).grid(row = 10, column = 1, sticky = W)
            CTkLabel(frame, text = f"{data["Most expensive item"][1]} for {data["Most expensive item"][0]}", font = ("Roboto", 20)).grid(row = 10, column = 2)
            CTkLabel(frame, text = "Number of transactions", font = ("Roboto", 20)).grid(row = 11, column = 1, sticky = W)
            CTkLabel(frame, text = data['Number of transactions'], font = ("Roboto", 20)).grid(row = 11, column = 2)

            report =  get_report(name, gui = True)
            CTkLabel(frame, text = '').grid(row = 12,column = 1)
            CTkLabel(frame, text = report, font = ('Roboto', 20)).place(x=0, y=580)
            CTkLabel(frame, text = 'Financial report', font = ("Roboto", 20)).grid(row = 13,column = 1, sticky = W)
            CTkLabel(frame, text = '').grid(row = 14,column = 1)
            CTkLabel(frame, text = '').grid(row = 15,column = 1)
            CTkLabel(frame, text = '').grid(row = 16,column = 1)
            CTkLabel(frame, text = '').grid(row = 17,column = 1)

    CTkLabel(menu, text = 'Menu', font = ('Georgia', 35)).pack(anchor = CENTER, pady = 10)

    dash_btn = CTkButton(menu, text = 'Dashboard', width = 120, height = 40,font = ('georgia',20), command = dashboard)
    dash_btn.pack(anchor = CENTER, pady = 30)

    diary_btn = CTkButton(menu, text = 'Diary', width = 120, height = 40, font = ('georgia',20), command = diary)
    diary_btn.pack(anchor = CENTER)

    finance_btn = CTkButton(menu, text = 'Finance', width = 120, height = 40, font = ('georgia',20), command = gui_finance)
    finance_btn.pack(anchor = CENTER, pady = 30)

    stats_btn = CTkButton(menu, text = 'Stats', width = 120, height = 40, font = ('georgia',20), command = gui_stats)
    stats_btn.pack(anchor = CENTER)

    del_acc_btn = CTkButton(menu, text = 'Delete Account', fg_color = 'red', hover_color='#701010', width = 100, font = ('georgia',15), command = lambda : gui_del_acc(name))
    del_acc_btn.place(x=5, y=565)

    app.mainloop()

if __name__ == '__main__':
    main()
