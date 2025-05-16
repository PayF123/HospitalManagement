import sqlite3

# Use the correct relative path
# conn = sqlite3.connect('D://Shyam Sir//TKINTER//BCI GUI//GUI//users.db')
conn = sqlite3.connect('D://Shyam Sir//TKINTER//BCI GUI//instance/HospitalData.db')
cursor = conn.cursor()


# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables in the database:", tables)

# Loop through and print data from each table
for table_name in tables:
    print(f"\nData from table: {table_name[0]}")
    cursor.execute(f"SELECT * FROM {table_name[0]}")
    rows = cursor.fetchall()
    for row in rows:
        print(row)

conn.close()

# import os
# print(os.path.exists('D://Shyam Sir//TKINTER//BCI GUI//GUI//users.db'))