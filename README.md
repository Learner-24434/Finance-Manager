# Life-Manager (OUTDATED)
## Overview
This is a python program that has GUI and CLI functionality. Its main purpose is to keep track of diary entries, financial transactions and provide simple statistics.

## Requirements
- customtkinter : Used to create the GUI
- argparse : Used to parse the command line arguments
- tabulate : Used to display information specifically tables in CLI
- pandas : Used for simple statistics

## Arguments for CLI
- `python project.py` : No argument creates a new account by taking the following parameters : Username, Password and Financial Balance
- `python project.py <-d/--delete>` : Deletes the account.
- `python project.py <-w/--write>` : Write a diary entry by taking in the following parameters : Date, Category and the diary entry itself.
- `python project.py <-r/--read>` : Takes a date as an input and displays the diary entry on that date.
- `python project.py <-f/--finance> <append/read>` : Shows all the financial transactions in a table or adds a transaction.
    - `python project.py <-f/--finance> append` : Adds a transaction taking the follwong paramaters : Date, detail, amount and debit/credit.
    - `python project.py <-f/--finances> read` : Displays a table of all the financial transactions using tabulate.



- `python project.py <-st/--stats>` : Provides the following statistics regarding the financila postion : 
    - Total money spent in a month
    - Total money recieved in a month
    - Item on which most money was spent
    - Most frequently bought item.
- `python project.py <-se/--search> <finance/diary>` 
    - `python project.py <-se/--search> finance` : Asks for some filter parameters (Date, Detail, Amount, Dr/Cr) and returns search reults in a table using tabulate.
    - `python project.py <-se/--search> diary` : Asks for some filter parameters (Date, Caategory) and returns search reults in a table using tabulate.
- `python project.py <-u/--gui>` : Acivates GUI mode.

The GUI demo has been given in this [video](https://youtu.be/JqWSV4M_jGY).
