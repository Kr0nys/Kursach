import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Подключение к базе данных
def connect_to_db():
    try:
        global conn, cursor
        conn = mysql.connector.connect(
            host="localhost",  # Укажите ваш хост
            user="root",  # Имя пользователя MySQL
            password="767556Dima",  # Пароль пользователя
            database="motorcycleassembly"  # Имя вашей базы данных
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
menu_frame = tk.Frame(root, height=50, bg="#2c3e50", bd=1, relief="solid")
menu_frame.pack(side="top", fill="x")

# Создаем фрейм для отображения данных снизу
content_frame = tk.Frame(root, bg="#ecf0f1")
content_frame.pack(side="top", expand=True, fill="both")

# Глобальные фреймы
frames = {}
for name in ["suppliers", "stock", "motorcycle", "assembly", "employees", "parts_check", "categories", "check_result", "motorcycle_parts"]:
    frame = tk.Frame(content_frame, bg="#ecf0f1")
    frame.grid(row=0, column=0, sticky="nsew")
    frames[name] = frame

# Функция для переключения между фреймами
def switch_frame(frame):
    # Скрываем все фреймы
    for f in frames.values():
        f.grid_forget()  # Скрывает все фреймы
    frame.grid(row=0, column=0, sticky="nsew")  # Показывает нужный фрейм

# Функция для отображения данных
def show_data(frame, query, columns, table_name):
    for widget in frame.winfo_children():
        widget.destroy()
    # Модифицируем запрос для роли "Директор"
    if table_name == "Сотрудники" and user_role == "Директор":
        query = "SELECT ID_сотрудника, ФИО, Должность FROM Сотрудники"
        columns = ["ID_сотрудника", "ФИО", "Должность"]  # Исключаем "роль" и "пароль"
    try:
        cursor.execute(query)
        data = cursor.fetchall()

        tree = ttk.Treeview(frame, columns=columns, show="headings")
        tree.pack(expand=True, fill="both")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        for row in data:
            tree.insert("", "end", values=row)

        button_frame = tk.Frame(frame)
        button_frame.pack(fill="x")

        if user_role == "Администратор":
            tk.Button(button_frame, text="Добавить", command=lambda: add_data(frame, columns, table_name), bg="#3498db", fg="white", relief="flat",
                      font=("Helvetica", 12), width=15).pack(side="left", padx=5, pady=5)
            tk.Button(button_frame, text="Редактировать", command=lambda: edit_data(frame, tree, columns, table_name), bg="#f39c12", fg="white", relief="flat",
                      font=("Helvetica", 12), width=15).pack(side="left", padx=5, pady=5)
            tk.Button(button_frame, text="Удалить", command=lambda: delete_data(frame, tree, columns, table_name), bg="#e74c3c", fg="white", relief="flat",
                      font=("Helvetica", 12), width=15).pack(side="left", padx=5, pady=5)
        elif user_role == "Директор":
            tk.Button(button_frame, text="Добавить", command=lambda: add_data(frame, columns, table_name), bg="#3498db", fg="white", relief="flat",
                      font=("Helvetica", 12), width=15).pack(side="left", padx=5, pady=5)
            tk.Button(button_frame, text="Редактировать", command=lambda: edit_data(frame, tree, columns, table_name), bg="#f39c12", fg="white", relief="flat",
                      font=("Helvetica", 12), width=15).pack(side="left", padx=5, pady=5)
            tk.Button(button_frame, text="Удалить", command=lambda: delete_data(frame, tree, columns, table_name), bg="#e74c3c", fg="white", relief="flat",
                      font=("Helvetica", 12), width=15).pack(side="left", padx=5, pady=5)
        elif user_role == "Сотрудник":
            tk.Button(button_frame, text="Добавить", command=lambda: add_data(frame, columns, table_name), bg="#3498db", fg="white", relief="flat",
                      font=("Helvetica", 12), width=15).pack(side="left", padx=5, pady=5)
            tk.Button(button_frame, text="Редактировать", command=lambda: edit_data(frame, tree, columns, table_name), bg="#f39c12", fg="white", relief="flat",
                      font=("Helvetica", 12), width=15).pack(side="left", padx=5, pady=5)
    except mysql.connector.Error as err:
        messagebox.showerror("Ошибка", f"Ошибка при загрузке данных: {err}")


# Словарь связей между таблицами
related_fields = {
    "ID_поставщика": {"table": "Поставщики", "id_column": "ID_поставщика", "display_column": "Детали"},
    "ID_категории": {"table": "Категории", "id_column": "ID_категории", "display_column": "Название"},
    "ID_мотоцикла": {"table": "Мотоциклы", "id_column": "ID_мотоцикла", "display_column": "Модель"},
    "ID_сотрудника": {"table": "Сотрудники", "id_column": "ID_сотрудника", "display_column": "ФИО"},
    "ID_детали": {"table": "Склад", "id_column": "ID_детали", "display_column": "Название"},
}

def create_field(entry_window, col, current_value=None):
    if col in related_fields:  # Проверяем, есть ли поле в связях
        relation = related_fields[col]
        try:
            # Получаем данные из связанной таблицы
            cursor.execute(f"SELECT {relation['id_column']}, {relation['display_column']} FROM {relation['table']}")
            records = cursor.fetchall()

            # Формируем словарь {Отображаемое значение: ID}
            record_dict = {f"{row[1]} (ID: {row[0]})": row[0] for row in records}
            combobox = ttk.Combobox(entry_window, values=list(record_dict.keys()))
            if current_value:
                combobox.set([key for key, value in record_dict.items() if value == current_value][0])
            combobox.pack(pady=5)
            return combobox, record_dict  # Возвращаем ComboBox и словарь для маппинга
        except mysql.connector.Error as err:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные для поля {col}: {err}")
            return None, None
    else:  # Для обычных текстовых полей
        entry = tk.Entry(entry_window, font=("Helvetica", 10))
        if current_value:
            entry.insert(0, current_value)
        entry.pack(pady=5)
        return entry, None

# Функции для добавления, редактирования и удаления данных
def add_data(frame, columns, table_name):
    entry_values = []
    entry_window = tk.Toplevel(root)
    entry_window.title("Добавить запись")
    entry_window.configure(bg="#ecf0f1")

    non_key_columns = columns[1:]

    for col in non_key_columns:
        tk.Label(entry_window, text=col, bg="#ecf0f1", font=("Helvetica", 10)).pack(pady=5)
        field, mapping = create_field(entry_window, col)
        entry_values.append((field, mapping))

    def save_data():
        values = []
        for entry, mapping in entry_values:
            if mapping:
                selected_value = entry.get()
                values.append(mapping.get(selected_value, None))
            else:
                values.append(entry.get())

        # Проверка, что ID_мотоцикла уже не используется
        if "ID_мотоцикла" in non_key_columns:
            motorcycle_id_index = non_key_columns.index("ID_мотоцикла")
            motorcycle_id = values[motorcycle_id_index]

            query = "SELECT COUNT(*) FROM Сборка WHERE ID_мотоцикла = %s"
            cursor.execute(query, (motorcycle_id,))
            if cursor.fetchone()[0] > 0:
                messagebox.showerror("Ошибка", "Этот ID мотоцикла уже используется в другой сборке.")
                return

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

    tk.Button(entry_window, text="Сохранить", command=save_data, bg="#2ecc71", fg="white", relief="flat", font=("Helvetica", 12), width=20).pack(pady=10)

def edit_data(frame, tree, columns, table_name):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Ошибка", "Выберите запись для редактирования.")
        return

    values = tree.item(selected_item[0])['values']
    entry_values = []
    entry_window = tk.Toplevel(root)
    entry_window.title("Редактировать запись")
    entry_window.configure(bg="#ecf0f1")

    # Первичный ключ выводим только для отображения
    for i, col in enumerate(columns):
        tk.Label(entry_window, text=col, bg="#ecf0f1", font=("Helvetica", 10)).pack(pady=5)
        if i == 0:  # Первичный ключ (запрещено редактирование)
            entry = tk.Entry(entry_window)
            entry.insert(0, values[i])
            entry.config(state="disabled")
            entry.pack(pady=5)
            entry_values.append((entry, None))  # Сохраняем первичный ключ
        else:
            field, mapping = create_field(entry_window, col, current_value=values[i])
            entry_values.append((field, mapping))

    def update_data():
        new_values = []
        for i, (entry, mapping) in enumerate(entry_values):
            if i == 0:  # Пропускаем первичный ключ (он только для WHERE)
                continue
            if mapping:  # Если это ComboBox
                selected_value = entry.get()
                new_values.append(mapping.get(selected_value, None))
            else:  # Обычное текстовое поле
                new_values.append(entry.get())

        # Формируем запрос UPDATE
        set_clause = ", ".join([f"{col} = %s" for col in columns[1:]])  # Только non-key столбцы
        query = f"UPDATE {table_name} SET {set_clause} WHERE {columns[0]} = %s"

        try:
            # Добавляем значение первичного ключа в конце списка параметров
            cursor.execute(query, new_values + [values[0]])
            conn.commit()
            entry_window.destroy()
            show_data(frame, f"SELECT * FROM {table_name}", columns, table_name)
        except mysql.connector.Error as err:
            messagebox.showerror("Ошибка", f"Не удалось обновить запись: {err}")

    tk.Button(entry_window, text="Сохранить", command=update_data, bg="#2ecc71", fg="white", relief="flat", font=("Helvetica", 12), width=20).pack(pady=10)

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
    show_data(frames['suppliers'], "SELECT * FROM Поставщики", ["ID_поставщика", "Детали", "Срок_доставки", "Контактная_информация"], "Поставщики")
    switch_frame(frames['suppliers'])

def show_stock():
    show_data(frames['stock'], "SELECT * FROM Склад", ["ID_детали", "Название", "Цена", "Количество_на_складе", "Минимальный_запас", "ID_поставщика"], "Склад")
    switch_frame(frames['stock'])

def show_motorcycle():
    show_data(frames['motorcycle'], "SELECT * FROM Мотоциклы", ["ID_мотоцикла", "Модель", "Цвет", "ID_категории", "Дата_выпуска", "Фотография"], "Мотоциклы")
    switch_frame(frames['motorcycle'])

def show_assembly():
    show_data(frames['assembly'], "SELECT * FROM Сборка", ["ID_сборки", "Дата", "ID_мотоцикла", "ID_сотрудника", "Статус", "Статус_проверки"], "Сборка")
    switch_frame(frames['assembly'])

def show_employees():
    show_data(frames['employees'], "SELECT * FROM Сотрудники", ["ID_сотрудника", "ФИО", "Должность", "Контактная_информация", "Роль", "Пароль"], "Сотрудники")
    switch_frame(frames['employees'])

def check_parts():
    show_data(frames['parts_check'], "SELECT * FROM Детали_мотоцикла", ["ID_мотоцикла", "ID_детали", "Количество_для_сборки"], "Детали_мотоцикла")
    switch_frame(frames['parts_check'])

def show_categories():
    show_data(frames['categories'], "SELECT * FROM Категории", ["ID_категории", "Название", "Описание"], "Категории")
    switch_frame(frames['categories'])

def show_check_result():
    show_data(frames['check_result'], "SELECT * FROM Результат_проверки", ["ID_проверки", "Дата_проверки", "Статус_детали", "ID_детали", "ID_мотоцикла"], "Результат_проверки")
    switch_frame(frames['check_result'])

def show_motorcycle_parts():
    show_data(frames['motorcycle_parts'], "SELECT * FROM Детали_мотоцикла", ["ID_мотоцикла", "ID_детали", "Количество_для_сборки"], "Детали_мотоцикла")
    switch_frame(frames['motorcycle_parts'])

def show_motorcycle_assembly_report():
    # Очистка предыдущего содержимого фрейма
    for widget in frames['assembly'].winfo_children():
        widget.destroy()

    # Создание контейнера для данных и графика
    left_frame = tk.Frame(frames['assembly'], bg="#ecf0f1")
    left_frame.pack(side="left", fill="both", expand=True)

    right_frame = tk.Frame(frames['assembly'], bg="#ecf0f1", width=300)
    right_frame.pack(side="right", fill="y")

    # Создание заголовка отчета
    tk.Label(left_frame, text="Отчет по собранным мотоциклам", font=("Helvetica", 16), bg="#ecf0f1").pack(pady=10)

    # Создание элементов для выбора дат
    date_frame = tk.Frame(left_frame, bg="#ecf0f1")
    date_frame.pack(pady=10)

    tk.Label(date_frame, text="Дата начала (YYYY-MM-DD)", font=("Helvetica", 12), bg="#ecf0f1").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    start_date_entry = tk.Entry(date_frame, font=("Helvetica", 10))
    start_date_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(date_frame, text="Дата окончания (YYYY-MM-DD)", font=("Helvetica", 12), bg="#ecf0f1").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    end_date_entry = tk.Entry(date_frame, font=("Helvetica", 10))
    end_date_entry.grid(row=1, column=1, padx=5, pady=5)

    # Функция для генерации отчета
    def generate_report():
        start_date = start_date_entry.get()
        end_date = end_date_entry.get()

        if not start_date or not end_date:
            messagebox.showerror("Ошибка", "Пожалуйста, введите обе даты.")
            return

        try:
            # Запрос для получения данных
            query = """
            SELECT Дата, COUNT(*) 
            FROM Сборка
            WHERE Дата BETWEEN %s AND %s
            AND Статус = 'Завершен'
            GROUP BY Дата
            """
            cursor.execute(query, (start_date, end_date))
            results = cursor.fetchall()

            # Если данных нет
            if not results:
                messagebox.showinfo("Результат", "Нет данных для выбранного периода.")
                return

            # Построение графика
            dates = [row[0] for row in results]
            counts = [int(row[1]) for row in results]
            formatted_dates = [date.strftime("%d.%m.%Y") for date in dates]  # Форматирование дат

            fig, ax = plt.subplots(figsize=(6, 4))
            ax.bar(formatted_dates , counts, color='skyblue')
            ax.set_title("Количество собранных мотоциклов", fontsize=12)
            ax.set_xlabel("Дата", fontsize=10)
            ax.set_ylabel("Количество", fontsize=10)
            ax.tick_params(axis='x', rotation=45)

            # Очистка предыдущего графика
            for widget in right_frame.winfo_children():
                widget.destroy()

            # Отображение графика в правом фрейме
            canvas = FigureCanvasTkAgg(fig, master=right_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

        except mysql.connector.Error as err:
            messagebox.showerror("Ошибка", f"Ошибка при генерации отчета: {err}")

    # Кнопка для запуска генерации отчета
    tk.Button(left_frame, text="Генерировать отчет", command=generate_report, bg="#3498db", fg="white", relief="flat",
              font=("Helvetica", 12)).pack(pady=10)

    # Переключение на фрейм с отчетом
    switch_frame(frames['assembly'])

    def get_available_motorcycle_ids():
        try:
            cursor.execute("""
                SELECT ID_мотоцикла, Модель 
                FROM Мотоциклы 
                WHERE ID_мотоцикла NOT IN (SELECT ID_мотоцикла FROM Сборка)
            """)
            return cursor.fetchall()  # Возвращает список доступных ID и моделей
        except mysql.connector.Error as err:
            messagebox.showerror("Ошибка", f"Ошибка при загрузке доступных ID мотоциклов: {err}")
            return []

# Авторизация
def login():
    def authenticate():
        username = username_entry.get()
        password = password_entry.get()
        try:
            # Проверяем логин и пароль в базе
            query = "SELECT роль FROM Сотрудники WHERE ID_сотрудника = %s AND пароль = %s"
            cursor.execute(query, (username, password))
            result = cursor.fetchone()
            if result:
                global user_role
                user_role = result[0]
                messagebox.showinfo("Успех", f"Вы вошли как {user_role}")
                login_frame.destroy()
                main_menu()
            else:
                messagebox.showerror("Ошибка", "Неверный логин или пароль")
        except mysql.connector.Error as err:
            messagebox.showerror("Ошибка", f"Ошибка при авторизации: {err}")

    login_frame = tk.Frame(root, bg="#ecf0f1")
    login_frame.pack(fill="both", expand=True)

    tk.Label(login_frame, text="Логин", bg="#ecf0f1", font=("Helvetica", 14)).pack(pady=5)
    username_entry = tk.Entry(login_frame, font=("Helvetica", 12))
    username_entry.pack(pady=5)

    tk.Label(login_frame, text="Пароль", bg="#ecf0f1", font=("Helvetica", 14)).pack(pady=5)
    password_entry = tk.Entry(login_frame, show="*", font=("Helvetica", 12))
    password_entry.pack(pady=5)

    tk.Button(login_frame, text="Войти", command=authenticate, bg="#3498db", fg="white", relief="flat",
              font=("Helvetica", 14), width=20).pack(pady=10)
    tk.Button(login_frame, text="Выход", command=close_application, bg="#e74c3c", fg="white", relief="flat",
              font=("Helvetica", 14), width=20).pack(pady=10)
# Добавление кнопки в главное меню для отображения отчета
def main_menu():
    for widget in menu_frame.winfo_children():
        widget.destroy()

    if user_role == "Администратор":
        tk.Button(menu_frame, text="Категории", command=show_categories, bg="#2980b9", fg="white", relief="flat",
                  font=("Helvetica", 10), width=11).pack(side="left", padx=5, pady=5)
        tk.Button(menu_frame, text="Поставщики", command=show_suppliers, bg="#2980b9", fg="white", relief="flat",
                  font=("Helvetica", 10), width=11).pack(side="left", padx=5, pady=5)
        tk.Button(menu_frame, text="Склад", command=show_stock, bg="#2980b9", fg="white", relief="flat",
                  font=("Helvetica", 10), width=11).pack(side="left", padx=5, pady=5)
        tk.Button(menu_frame, text="Мотоциклы", command=show_motorcycle, bg="#2980b9", fg="white", relief="flat",
                  font=("Helvetica", 10), width=11).pack(side="left", padx=5, pady=5)
        tk.Button(menu_frame, text="Сборка", command=show_assembly, bg="#2980b9", fg="white", relief="flat",
                  font=("Helvetica", 10), width=11).pack(side="left", padx=5, pady=5)
        tk.Button(menu_frame, text="Отчет по сборке", command=show_motorcycle_assembly_report, bg="#2980b9", fg="white", relief="flat",
                  font=("Helvetica", 10), width=11).pack(side="left", padx=5, pady=5)
        tk.Button(menu_frame, text="Сотрудники", command=show_employees, bg="#2980b9", fg="white", relief="flat",
                  font=("Helvetica", 10), width=11).pack(side="left", padx=5, pady=5)
        tk.Button(menu_frame, text="Детали мотоцикла", command=show_motorcycle_parts, bg="#2980b9", fg="white", relief="flat",
                  font=("Helvetica", 10), width=13).pack(side="left", padx=5, pady=5)
        tk.Button(menu_frame, text="Результат проверки", command=show_check_result, bg="#2980b9", fg="white", relief="flat",
                  font=("Helvetica", 10), width=14).pack(side="left", padx=5, pady=5)
        tk.Button(menu_frame, text="Выход", command=close_application, bg="#e74c3c", fg="white", relief="flat",
                  font=("Helvetica", 10), width=9).pack(side="right", padx=5, pady=5)
    elif user_role == "Директор":
        tk.Button(menu_frame, text="Категории", command=show_categories, bg="#2980b9", fg="white", relief="flat",
                  font=("Helvetica", 10), width=11).pack(side="left", padx=5, pady=5)
        tk.Button(menu_frame, text="Поставщики", command=show_suppliers, bg="#2980b9", fg="white", relief="flat",
                  font=("Helvetica", 10), width=11).pack(side="left", padx=5, pady=5)
        tk.Button(menu_frame, text="Склад", command=show_stock, bg="#2980b9", fg="white", relief="flat",
                  font=("Helvetica", 10), width=11).pack(side="left", padx=5, pady=5)
        tk.Button(menu_frame, text="Мотоциклы", command=show_motorcycle, bg="#2980b9", fg="white", relief="flat",
                  font=("Helvetica", 10), width=11).pack(side="left", padx=5, pady=5)
        tk.Button(menu_frame, text="Сборка", command=show_assembly, bg="#2980b9", fg="white", relief="flat",
                  font=("Helvetica", 10), width=11).pack(side="left", padx=5, pady=5)
        tk.Button(menu_frame, text="Отчет по сборке", command=show_motorcycle_assembly_report, bg="#2980b9", fg="white", relief="flat",
                  font=("Helvetica", 10), width=11).pack(side="left", padx=5, pady=5)
        tk.Button(menu_frame, text="Сотрудники", command=show_employees, bg="#2980b9", fg="white", relief="flat",
                  font=("Helvetica", 10), width=11).pack(side="left", padx=5, pady=5)
        tk.Button(menu_frame, text="Детали мотоцикла", command=show_motorcycle_parts, bg="#2980b9", fg="white", relief="flat",
                  font=("Helvetica", 10), width=13).pack(side="left", padx=5, pady=5)
        tk.Button(menu_frame, text="Результат проверки", command=show_check_result, bg="#2980b9", fg="white", relief="flat",
                  font=("Helvetica", 10), width=14).pack(side="left", padx=5, pady=5)
        tk.Button(menu_frame, text="Выход", command=close_application, bg="#e74c3c", fg="white", relief="flat",
                  font=("Helvetica", 10), width=9).pack(side="right", padx=5, pady=5)
    elif user_role == "Сотрудник":
        tk.Button(menu_frame, text="Категории", command=show_categories, bg="#2980b9", fg="white", relief="flat",
                  font=("Helvetica", 10), width=11).pack(side="left", padx=5, pady=5)
        tk.Button(menu_frame, text="Склад", command=show_stock, bg="#2980b9", fg="white", relief="flat",
                  font=("Helvetica", 10), width=11).pack(side="left", padx=5, pady=5)
        tk.Button(menu_frame, text="Мотоциклы", command=show_motorcycle, bg="#2980b9", fg="white", relief="flat",
                  font=("Helvetica", 10), width=11).pack(side="left", padx=5, pady=5)
        tk.Button(menu_frame, text="Сборка", command=show_assembly, bg="#2980b9", fg="white", relief="flat",
                  font=("Helvetica", 10), width=11).pack(side="left", padx=5, pady=5)
        tk.Button(menu_frame, text="Детали мотоциклов", command=show_motorcycle_parts, bg="#2980b9", fg="white", relief="flat",
                  font=("Helvetica", 10), width=11).pack(side="left", padx=5, pady=5)
        tk.Button(menu_frame, text="Выход", command=close_application, bg="#e74c3c", fg="white", relief="flat",
                  font=("Helvetica", 10), width=9).pack(side="right", padx=5, pady=5)

def close_application():
    close_db_connection()
    root.destroy()

connect_to_db()
login()
root.protocol("WM_DELETE_WINDOW", close_db_connection)
root.mainloop()
