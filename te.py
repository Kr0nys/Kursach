import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

# Подключение к базе данных
def connect_to_db():
    try:
        global conn, cursor
        conn = mysql.connector.connect(
            host="localhost",  # Укажите ваш хост
            user="root",  # Имя пользователя MySQL
            password="767556Dima",  # Пароль пользователя
            database="motocycledb"  # Имя вашей базы данных
        )
        cursor = conn.cursor()
    except mysql.connector.Error as err:
        messagebox.showerror("Ошибка подключения", f"Не удалось подключиться к базе данных: {err}")
        exit()

# Закрытие соединения с базой данных
def close_db_connection():
    if cursor:
        cursor.close()
    if conn:
        conn.close()

# Главное окно приложения
root = tk.Tk()
root.title("ERP")
root.geometry("1100x600")

# Глобальные переменные
user_role = ""

# Создаем фрейм для меню сверху
menu_frame = tk.Frame(root, height=50, bg="lightgrey")
menu_frame.pack(side="top", fill="x")

# Создаем фрейм для отображения данных снизу
content_frame = tk.Frame(root)
content_frame.pack(side="top", expand=True, fill="both")

# Глобальные фреймы
frames = {}
for name in ["suppliers", "stock", "motorcycle", "assembly", "employees", "parts_check"]:
    frame = tk.Frame(content_frame)
    frame.grid(row=0, column=0, sticky="nsew")
    frames[name] = frame

# Функция для переключения между фреймами
def switch_frame(frame):
    frame.tkraise()

# Функция для отображения данных
def show_data(frame, query, columns, table_name):
    for widget in frame.winfo_children():
        widget.destroy()

    try:
        cursor.execute(query)
        data = cursor.fetchall()

        # Создаем контейнер с горизонтальной и вертикальной прокруткой
        scroll_container = tk.Frame(frame)
        scroll_container.pack(expand=True, fill="both")

        # Вертикальный скроллбар
        vsb = ttk.Scrollbar(scroll_container, orient="vertical")
        vsb.pack(side="right", fill="y")

        # Горизонтальный скроллбар
        hsb = ttk.Scrollbar(scroll_container, orient="horizontal")
        hsb.pack(side="bottom", fill="x")

        # Таблица с данными
        tree = ttk.Treeview(
            scroll_container, columns=columns, show="headings",
            yscrollcommand=vsb.set, xscrollcommand=hsb.set
        )
        tree.pack(expand=True, fill="both")

        vsb.config(command=tree.yview)
        hsb.config(command=tree.xview)

        # Установка заголовков и данных в таблице
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=150)

        for row in data:
            tree.insert("", "end", values=row)

        button_frame = tk.Frame(frame)
        button_frame.pack(fill="x", pady=5)

        if user_role in ["Администратор", "Директор", "Менеджер"]:
            tk.Button(button_frame, text="Добавить", command=lambda: add_data(frame, columns, table_name)).pack(side="left", padx=5)
            tk.Button(button_frame, text="Редактировать", command=lambda: edit_data(frame, tree, columns, table_name)).pack(side="left", padx=5)
            tk.Button(button_frame, text="Удалить", command=lambda: delete_data(frame, tree, columns, table_name)).pack(side="left", padx=5)
    except mysql.connector.Error as err:
        messagebox.showerror("Ошибка", f"Ошибка при загрузке данных: {err}")

# Функции для добавления, редактирования и удаления данных
def add_data(frame, columns, table_name):
    entry_values = []
    entry_window = tk.Toplevel(root)
    entry_window.title("Добавить запись")

    # Исключаем первый ключ из ввода
    non_key_columns = columns[1:]

    for col in non_key_columns:
        tk.Label(entry_window, text=col).pack()
        entry = tk.Entry(entry_window)
        entry.pack()
        entry_values.append(entry)

    def save_data():
        values = [entry.get() for entry in entry_values]
        placeholders = ", ".join(["%s"] * len(values))
        query = f"INSERT INTO {table_name} ({', '.join(non_key_columns)}) VALUES ({placeholders})"

        try:
            cursor.execute(query, values)
            conn.commit()
            entry_window.destroy()
            show_data(frame, f"SELECT * FROM {table_name}", columns, table_name)
        except mysql.connector.Error as err:
            messagebox.showerror("Ошибка", f"Не удалось добавить запись: {err}")
            entry_window.destroy()

    tk.Button(entry_window, text="Сохранить", command=save_data).pack()


def edit_data(frame, tree, columns, table_name):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Ошибка", "Выберите запись для редактирования.")
        return

    values = tree.item(selected_item[0])['values']
    entry_values = []
    entry_window = tk.Toplevel(root)
    entry_window.title("Редактировать запись")

    # Первичный ключ выводим только для отображения
    for i, col in enumerate(columns):
        tk.Label(entry_window, text=col).pack()
        entry = tk.Entry(entry_window)
        if i == 0:  # Первичный ключ (запрещено редактирование)
            entry.insert(0, values[i])
            entry.config(state="disabled")
        else:
            entry.insert(0, values[i])
        entry.pack()
        entry_values.append(entry)

    def update_data():
        # Собираем новые значения, исключая первичный ключ
        new_values = [entry.get() for i, entry in enumerate(entry_values) if i != 0]
        set_clause = ", ".join([f"{col} = %s" for col in columns[1:]])
        query = f"UPDATE {table_name} SET {set_clause} WHERE {columns[0]} = %s"

        try:
            # Добавляем первичный ключ как последний аргумент в запрос
            cursor.execute(query, new_values + [values[0]])
            conn.commit()
            entry_window.destroy()
            show_data(frame, f"SELECT * FROM {table_name}", columns, table_name)
        except mysql.connector.Error as err:
            messagebox.showerror("Ошибка", f"Не удалось обновить запись: {err}")

    tk.Button(entry_window, text="Сохранить", command=update_data).pack()


def delete_data(frame, tree, columns, table_name):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Ошибка", "Выберите запись для удаления.")
        return

    values = tree.item(selected_item[0])['values']
    query = f"DELETE FROM {table_name} WHERE {columns[0]} = %s"

    try:
        cursor.execute(query, (values[0],))
        conn.commit()
        show_data(frame, f"SELECT * FROM {table_name}", columns, table_name)
    except mysql.connector.Error as err:
        messagebox.showerror("Ошибка", f"Не удалось удалить запись: {err}")

# Функции отображения данных по таблицам
def show_suppliers():
    show_data(frames['suppliers'], "SELECT * FROM Поставщики", ["ID_поставщика", "Детали", "Стоимость"], "Поставщики")
    switch_frame(frames['suppliers'])

def show_stock():
    show_data(frames['stock'], "SELECT * FROM Склад", ["ID_компонента", "Название", "Цена", "Количество_на_складе", "ID_поставщика"], "Склад")
    switch_frame(frames['stock'])

def show_motorcycle():
    show_data(frames['motorcycle'], "SELECT * FROM Мотоцикл", ["ID_мотоцикла", "Модель", "Цвет", "Категория", "Дата_выпуска", "С_С_комплектующих", "Фотография"], "Мотоцикл")
    switch_frame(frames['motorcycle'])

def show_assembly():
    show_data(frames['assembly'], "SELECT * FROM Сборка", ["ID_сборки", "Дата", "ID_сотрудника", "ID_мотоцикла", "Цвет", "Статус"], "Сборка")
    switch_frame(frames['assembly'])

def show_employees():
    show_data(frames['employees'], "SELECT * FROM Сотрудник", ["ID_сотрудника", "ФИО", "Должность", "Контактная_информация"], "Сотрудник")
    switch_frame(frames['employees'])

def check_parts():
    show_data(frames['parts_check'], "SELECT * FROM Проверка_деталей_для_сборки", ["ID_мотоцикла", "ID_детали"], "Проверка_деталей_для_сборки")
    switch_frame(frames['parts_check'])

# Функция авторизации
def login():
    login_frame = tk.Frame(root)
    login_frame.pack(fill="both", expand=True)

    tk.Label(login_frame, text="Логин").pack(pady=5)
    username_entry = tk.Entry(login_frame)
    username_entry.pack(pady=5)

    tk.Label(login_frame, text="Пароль").pack(pady=5)
    password_entry = tk.Entry(login_frame, show="*")
    password_entry.pack(pady=5)

    def submit_login():
        username = username_entry.get()
        password = password_entry.get()

        if username == "admin" and password == "admin":
            global user_role
            user_role = "Администратор"
            login_frame.destroy()
            main_menu()
        else:
            messagebox.showerror("Ошибка", "Неверные логин или пароль")

    tk.Button(login_frame, text="Войти", command=submit_login).pack(pady=10)
    tk.Button(login_frame, text="Выход", command=close_application).pack(pady=10)

# Главное меню
def main_menu():
    tk.Button(menu_frame, text="Поставщики", command=show_suppliers).pack(side="left", padx=5)
    tk.Button(menu_frame, text="Склад", command=show_stock).pack(side="left", padx=5)
    tk.Button(menu_frame, text="Мотоциклы", command=show_motorcycle).pack(side="left", padx=5)
    tk.Button(menu_frame, text="Сборка", command=show_assembly).pack(side="left", padx=5)
    tk.Button(menu_frame, text="Сотрудники", command=show_employees).pack(side="left", padx=5)
    tk.Button(menu_frame, text="Проверка деталей", command=check_parts).pack(side="left", padx=5)
    tk.Button(menu_frame, text="Выход", command=close_application).pack(side="right", padx=5)

def close_application():
    close_db_connection()
    root.destroy()

connect_to_db()
login()
root.protocol("WM_DELETE_WINDOW", close_db_connection)
root.mainloop()
