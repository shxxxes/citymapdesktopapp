from ttkbootstrap import Style
from ttkbootstrap.constants import *
import ttkbootstrap as ttk
import tkinter as tk
from tkinter import messagebox
import mysql.connector
import view
from urllib.parse import urlparse


db_url = "mysql://root:cytxyYnjPyYDjsfkyKLEhPHsNyxumpkT@metro.proxy.rlwy.net:10106/railway"
parsed_url = urlparse(db_url)

DB_CONFIG = {
    'host': parsed_url.hostname,
    'user': parsed_url.username,
    'password': parsed_url.password,
    'database': parsed_url.path[1:],
    'port': parsed_url.port
}

def login_user():
    global current_user
    name = entry_name.get()
    password = entry_password.get()

    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        query = "SELECT id FROM users WHERE name = %s AND password = %s"
        cursor.execute(query, (name, password))
        user = cursor.fetchone()
        connection.close()

        if user:
            current_user = name
            messagebox.showinfo("Успех", "Вы успешно авторизировались!")
            root.withdraw()
            view.show_main_window(name, root)
        else:
            messagebox.showerror("Ошибка", "Неправильное имя или пароль.")
    except mysql.connector.Error as err:
        messagebox.showerror("Ошибка", f"Не удалось подключиться к базе данных: {err}")

def open_registration():
    registration_window = ttk.Toplevel(root)
    registration_window.title("Регистрация")
    registration_window.geometry("400x400")

    def register_user():
        name = reg_entry_name.get()
        email = reg_entry_email.get()
        password = reg_entry_password.get()

        if not name or not email or not password:
            messagebox.showwarning("Ошибка", "Заполните все поля!")
            return

        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor()
            query = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
            cursor.execute(query, (name, email, password))
            connection.commit()
            connection.close()
            messagebox.showinfo("Успех", "Вы успешно зарегистрировались!")
            registration_window.destroy()
        except mysql.connector.Error as err:
            messagebox.showerror("Ошибка", f"Ошибка базы данных: {err}")

    # Поля регистрации
    ttk.Label(registration_window, text="Имя:", font=("Arial", 14)).pack(pady=10)
    reg_entry_name = ttk.Entry(registration_window, font=("Arial", 14))
    reg_entry_name.pack()

    ttk.Label(registration_window, text="Email:", font=("Arial", 14)).pack(pady=10)
    reg_entry_email = ttk.Entry(registration_window, font=("Arial", 14))
    reg_entry_email.pack()

    ttk.Label(registration_window, text="Пароль:", font=("Arial", 14)).pack(pady=10)
    reg_entry_password = ttk.Entry(registration_window, show="*", font=("Arial", 14))
    reg_entry_password.pack()

    ttk.Button(registration_window, text="Зарегистрироваться", command=register_user, bootstyle="success").pack(pady=20)

# Главное окно
style = Style("cosmo")
root = style.master
root.title("Авторизация")
root.geometry("400x400")

# Поля авторизации
ttk.Label(root, text="Имя и фамилия:", font=("Arial", 14)).pack(pady=10)
entry_name = ttk.Entry(root, font=("Arial", 14))
entry_name.pack()

ttk.Label(root, text="Пароль:", font=("Arial", 14)).pack(pady=10)
entry_password = ttk.Entry(root, show="*", font=("Arial", 14))
entry_password.pack()

# Кнопки
ttk.Button(root, text="Войти", command=login_user, bootstyle="primary").pack(pady=20)
ttk.Button(root, text="Регистрация", command=open_registration, bootstyle="secondary").pack()

root.mainloop()