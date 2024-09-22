import tkinter as tk
from tkinter import messagebox
import psycopg2
import os

def apply_changes():
    conn_str = conn_str_entry.get()

    # Warning message
    if not messagebox.askokcancel("Warning", "This action will delete all existing tables in the public schema and cannot be undone. Do you want to proceed?"):
        return

    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(conn_str)
        cursor = conn.cursor()

        # Delete all tables in the public schema
        cursor.execute("""
            DO $$ DECLARE
            r RECORD;
            BEGIN
                FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
                    EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
                END LOOP;
            END $$;
        """)
        conn.commit()

        # Execute the SQL command located in /DDLs/latest.sql
        sql_file = '/DDLs/latest.sql'
        if os.path.exists(sql_file):
            with open(sql_file, 'r') as file:
                sql_commands = file.read()
                cursor.execute(sql_commands)
                conn.commit()
            messagebox.showinfo("Success", "Output Hub data structure successfully written to database")
        else:
            messagebox.showerror("Error", f"SQL file not found: {sql_file}")
        
        cursor.close()
        conn.close()

    except Exception as e:
        messagebox.showerror("Error", str(e))

# Create the GUI window
root = tk.Tk()
root.title("PostgreSQL Database Manager")

# Connection string label and entry
tk.Label(root, text="Enter PostgreSQL connection string:").pack(pady=10)
conn_str_entry = tk.Entry(root, width=50)
conn_str_entry.pack(pady=10)

# Apply button
apply_btn = tk.Button(root, text="Apply Changes", command=apply_changes)
apply_btn.pack(pady=20)

root.mainloop()
