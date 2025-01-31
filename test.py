import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import base64
from io import BytesIO

# Подключение к базе данных
def connect_to_db():
    try:
        global conn, cursor
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            port="3306",
            password="767556Dima",
            database="motorcycleassembly"
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
for name in ["suppliers", "stock", "motorcycles", "assembly", "employees", "parts_check", "motorcycle_parts"]:
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
    try:

        cursor.execute(query)
        data = cursor.fetchall()

        tree = ttk.Treeview(frame, columns=columns, show="headings")
        tree.pack(expand=True, fill="both")

        vsb = ttk.Scrollbar(tree, orient="vertical")
        vsb.pack(side='right', fill='y')

        # Горизонтальный Scrollbar
        hsb = ttk.Scrollbar(tree, orient="horizontal")
        hsb.pack(side='bottom', fill='x')

        # Создаем Treeview с привязкой к скроллбарам
        tree = ttk.Treeview(tree, columns=columns, show="headings", yscrollcommand=vsb.set,
                            xscrollcommand=hsb.set)
        tree.pack(expand=True, fill="both")

        # Привязываем скроллбары к Treeview
        vsb.config(command=tree.yview)
        hsb.config(command=tree.xview)

        # Настройка столбцов и заголовков
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        for row in data:
            tree.insert("", "end", values=row)

        button_frame = tk.Frame(frame)
        button_frame.pack(fill="x")

        if user_role == "Директор":
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

def show_photo(photo_data):
    if photo_data:
        try:
            # Декодируем изображение из base64
            image_data = base64.b64decode(photo_data)
            photo = tk.PhotoImage(data=image_data)

            photo = photo.subsample(2, 2)

            # Отображаем изображение в Label
            photo_label = tk.Label(photo_frame, image=photo)
            photo_label.image = photo  # Сохраняем ссылку на изображение
            photo_label.pack(pady=10)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить изображение: {e}")
    else:
        tk.Label(photo_frame, text="Фотография отсутствует", bg="#ecf0f1").pack(pady=10)

# Функция для загрузки фотографии
def upload_photo():
    from tkinter import filedialog
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")])
    if file_path:
        with open(file_path, "rb") as file:
            photo_data = base64.b64encode(file.read()).decode('utf-8')
        cursor.execute("UPDATE Motorcycles SET Photo = %s WHERE Motorcycle_ID = %s", (photo_data, selected_motorcycle[0]))
        conn.commit()
        show_photo(photo_data)
        messagebox.showinfo("Успех", "Фотография успешно загружена")

# Словарь связей между таблицами
related_fields = {
    "Supplier_ID": {"table": "Suppliers", "id_column": "Supplier_ID", "display_column": "Details"},
    "Motorcycle_ID": {"table": "Motorcycles", "id_column": "Motorcycle_ID", "display_column": "Model"},
    "Employee_ID": {"table": "Employees", "id_column": "Employee_ID", "display_column": "Full_Name"},
    "Part_ID": {"table": "Stock", "id_column": "Part_ID", "display_column": "Name"},
}

def create_field(entry_window, col, current_value=None):
    if col == "Role":
        values = ["Директор", "Сотрудник"]
        combobox = ttk.Combobox(entry_window, values=values, state='readonly')
        if current_value:
            combobox.set(current_value)
        combobox.pack(pady=5)
        return combobox, None
    elif col in ["Status", "Check_Status", "Part_Status"]:
        values = {
            "Status": ["Завершен", "В процессе сборки", "Сборка не начата"],
            "Check_Status": ["Проверено", "Не проверено"],
            "Part_Status": ["В наличии", "Отсутствует в наличии"]
        }
        combobox = ttk.Combobox(entry_window, values=values[col], state='readonly')
        if current_value:
            combobox.set(current_value)
        combobox.pack(pady=5)
        return combobox, None
    elif col == "Category":
        values = ["Спортбайк", "Классик", "Чоппер", "Туристический", "Квадроцикл", "Мопед"]
        combobox = ttk.Combobox(entry_window, values=values, state='readonly')
        if current_value:
            combobox.set(current_value)
        combobox.pack(pady=5)
        return combobox, None
    elif col in related_fields:
        relation = related_fields[col]
        try:
            cursor.execute(f"SELECT {relation['id_column']}, {relation['display_column']} FROM {relation['table']}")
            records = cursor.fetchall()
            record_dict = {f"{row[1]} (ID: {row[0]})": row[0] for row in records}
            combobox = ttk.Combobox(entry_window, values=list(record_dict.keys()))
            if current_value:
                combobox.set([key for key, value in record_dict.items() if value == current_value][0])
            combobox.pack(pady=5)
            return combobox, record_dict
        except mysql.connector.Error as err:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные для поля {col}: {err}")
            return None, None
    else:
        entry = tk.Entry(entry_window, font=("Helvetica", 10))
        if current_value:
            entry.insert(0, current_value)
        if col in ["Stock_Quantity", "Minimum_Stock", "Price", "Quantity_For_Assembly"]:
            def validate_input(new_value):
                # Позволяем ввод пустого значения
                if new_value == "":
                    return True
                # Проверяем, что значение является числом и больше или равно нулю
                try:
                    float_new_value = float(new_value)
                    return float_new_value >= 0
                except ValueError:
                    return False

            vcmd = (entry_window.register(validate_input), '%P')
            entry.config(validate='key', validatecommand=vcmd)
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
        part_id = None
        quantity_for_assembly = None
        for i, (entry, mapping) in enumerate(entry_values):
            if mapping:
                selected_value = entry.get()
                values.append(mapping.get(selected_value, None))
                if columns[i + 1] == "Part_ID":
                    part_id = mapping.get(selected_value, None)
            else:
                value = entry.get()
                if columns[i + 1] == "Quantity_For_Assembly":
                    quantity_for_assembly = int(value) if value else None
                values.append(value)

            # Проверка на наличие отрицательных значений для числовых полей
            if columns[i + 1] in ["Quantity_For_Assembly", "Stock_Quantity", "Minimum_Stock", "Price"]:
                if isinstance(values[i], str) and values[i].replace('.', '', 1).isdigit():
                    if float(values[i]) < 0:
                        messagebox.showerror("Ошибка",
                                             f"Значение в столбце '{columns[i + 1]}' не может быть отрицательным.")
                        return

        if table_name == "Motorcycle_Parts" and part_id and quantity_for_assembly:
            try:
                cursor.execute(f"SELECT Stock_Quantity FROM Stock WHERE Part_ID = %s", (part_id,))
                current_stock = cursor.fetchone()[0]
                if quantity_for_assembly > current_stock:
                    messagebox.showerror("Ошибка",
                                         f"На складе недостаточно деталей с ID {part_id}. Доступно {current_stock} шт.")
                    entry_window.destroy()
                    return
                new_stock = current_stock - quantity_for_assembly
                cursor.execute(f"UPDATE Stock SET Stock_Quantity = %s WHERE Part_ID = %s", (new_stock, part_id))
                conn.commit()
                cursor.execute(f"SELECT Minimum_Stock FROM Stock WHERE Part_ID = %s", (part_id,))
                min_stock = cursor.fetchone()[0]
                if new_stock <= min_stock:
                    messagebox.showwarning("Предупреждение",
                                           f"На складе минимальный уровень запаса для детали с ID {part_id}")
            except mysql.connector.Error as err:
                messagebox.showerror("Ошибка", f"Не удалось обновить данные на складе: {err}")

        placeholders = ", ".join(["%s"] * len(values))
        query = f"INSERT INTO {table_name} ({', '.join(non_key_columns)}) VALUES ({placeholders})"
        try:
            cursor.execute(query, values)
            conn.commit()
            print(f"Data saved to {table_name}")  # Отладка
            entry_window.destroy()
            show_data(frame, f"SELECT * FROM {table_name}", columns, table_name)

            # После добавления данных, обновляем фрейм с мотоциклами
            if table_name == "Motorcycles":
                show_motorcycles()  # Перезагружаем фрейм с мотоциклами
        except mysql.connector.Error as err:
            messagebox.showerror("Ошибка", f"Не удалось добавить запись: {err}")
            entry_window.destroy()

    tk.Button(entry_window, text="Сохранить", command=save_data, bg="#2ecc71", fg="white", relief="flat",
              font=("Helvetica", 12), width=20).pack(pady=10)


def edit_data(frame, tree, columns, table_name):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Ошибка", "Выберите запись для редактирования.")
        return
    values = tree.item(selected_item[0])['values']

    # Проверка, что количество значений совпадает с количеством столбцов
    if len(values) != len(columns):
        messagebox.showerror("Ошибка", "Количество значений не совпадает с количеством столбцов.")
        return

    entry_values = []
    entry_window = tk.Toplevel(root)
    entry_window.title("Редактировать запись")
    entry_window.configure(bg="#ecf0f1")

    for i, col in enumerate(columns):
        tk.Label(entry_window, text=col, bg="#ecf0f1", font=("Helvetica", 10)).pack(pady=5)
        if i == 0:
            entry = tk.Entry(entry_window)
            entry.insert(0, values[i])
            entry.config(state="disabled")
            entry.pack(pady=5)
            entry_values.append((entry, None))
        else:
            field, mapping = create_field(entry_window, col, current_value=values[i])
            entry_values.append((field, mapping))

    def update_data():
        new_values = []
        part_id = None
        quantity_for_assembly = None
        old_quantity_for_assembly = None
        for i, (entry, mapping) in enumerate(entry_values):
            if i == 0:
                continue
            if mapping:
                selected_value = entry.get()
                new_values.append(mapping.get(selected_value, None))
                if columns[i] == "Part_ID":
                    part_id = mapping.get(selected_value, None)
            else:
                value = entry.get()
                if columns[i] == "Quantity_For_Assembly":
                    quantity_for_assembly = int(value) if value else None
                new_values.append(value)

            if columns[i] in ["Quantity_For_Assembly", "Stock_Quantity", "Minimum_Stock", "Price"]:
                if isinstance(new_values[i - 1], str) and new_values[i - 1].replace('.', '', 1).isdigit():
                    if float(new_values[i - 1]) < 0:
                        messagebox.showerror("Ошибка",
                                             f"Значение в столбце '{columns[i]}' не может быть отрицательным.")
                        return

        if table_name == "Motorcycle_Parts" and part_id and quantity_for_assembly:
            try:
                cursor.execute(f"SELECT Quantity_For_Assembly FROM Motorcycle_Parts WHERE Motorcycle_Parts_ID = %s",
                               (values[0],))
                old_quantity_for_assembly = cursor.fetchone()[0]
                cursor.execute(f"SELECT Stock_Quantity FROM Stock WHERE Part_ID = %s", (part_id,))
                current_stock = cursor.fetchone()[0]
                new_stock = current_stock + old_quantity_for_assembly - quantity_for_assembly
                if quantity_for_assembly > current_stock + old_quantity_for_assembly:
                    messagebox.showerror("Ошибка",
                                         f"На складе недостаточно деталей с ID {part_id}. Доступно {current_stock} шт.")
                    return
                cursor.execute(f"UPDATE Stock SET Stock_Quantity = %s WHERE Part_ID = %s", (new_stock, part_id))
                conn.commit()
                cursor.execute(f"SELECT Minimum_Stock FROM Stock WHERE Part_ID = %s", (part_id,))
                min_stock = cursor.fetchone()[0]
                if new_stock <= min_stock:
                    messagebox.showwarning("Предупреждение",
                                           f"На складе минимальный уровень запаса для детали с ID {part_id}")
            except mysql.connector.Error as err:
                messagebox.showerror("Ошибка", f"Не удалось обновить данные на складе: {err}")

        set_clause = ", ".join([f"{col} = %s" for col in columns[1:]])
        query = f"UPDATE {table_name} SET {set_clause} WHERE {columns[0]} = %s"
        try:
            cursor.execute(query, new_values + [values[0]])
            conn.commit()
            entry_window.destroy()
            show_data(frame, f"SELECT * FROM {table_name}", columns, table_name)

            # После обновления данных, обновляем фрейм с фотографией
            if table_name == "Motorcycles":
                show_motorcycles()  # Перезагружаем фрейм с мотоциклами
        except mysql.connector.Error as err:
            messagebox.showerror("Ошибка", f"Не удалось обновить запись: {err}")
            entry_window.destroy()

    tk.Button(entry_window, text="Сохранить", command=update_data, bg="#2ecc71", fg="white", relief="flat",
              font=("Helvetica", 12), width=20).pack(pady=10)


def delete_data(frame, tree, columns, table_name):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Ошибка", "Выберите запись для удаления.")
        return
    values = tree.item(selected_item[0])['values']

    # Проверяем, есть ли столбец "Quantity_For_Assembly" в списке колонок
    if table_name == "Motorcycle_Parts":
        try:
            part_id_index = columns.index("Part_ID")
            part_id = values[part_id_index]

            # Проверяем наличие столбца "Quantity_For_Assembly"
            if "Quantity_For_Assembly" in columns:
                quantity_for_assembly_index = columns.index("Quantity_For_Assembly")
                quantity_for_assembly = values[quantity_for_assembly_index]

                try:
                    # Получаем текущее количество на складе
                    cursor.execute(f"SELECT Stock_Quantity FROM Stock WHERE Part_ID = %s", (part_id,))
                    current_stock = cursor.fetchone()[0]

                    # Восстанавливаем количество на складе
                    new_stock = current_stock + quantity_for_assembly
                    cursor.execute(f"UPDATE Stock SET Stock_Quantity = %s WHERE Part_ID = %s", (new_stock, part_id))
                    conn.commit()
                except mysql.connector.Error as err:
                    messagebox.showerror("Ошибка", f"Не удалось обновить данные на складе: {err}")
                    print(f"Error details: {err}")  # Отладочное сообщение
            else:
                # Если столбец "Quantity_For_Assembly" отсутствует, просто удаляем запись
                pass

        except ValueError as err:
            messagebox.showerror("Ошибка", f"Не удалось найти необходимые поля: {err}")
            print(f"Error details: {err}")  # Отладочное сообщение

    primary_key = columns[0]  # Предполагаем, что первый столбец - это первичный ключ
    query = f"DELETE FROM {table_name} WHERE {primary_key} = %s"
    try:
        cursor.execute(query, (values[0],))
        conn.commit()
        show_data(frame, f"SELECT * FROM {table_name}", columns, table_name)

        # После удаления данных, обновляем фрейм с мотоциклами
        if table_name == "Motorcycles":
            show_motorcycles()  # Перезагружаем фрейм с мотоциклами
    except mysql.connector.Error as err:
        messagebox.showerror("Ошибка", f"Не удалось удалить запись: {err}")
        print(f"Error details: {err}")  # Отладочное сообщение

# Функции отображения данных по таблицам
def show_suppliers():
    show_data(frames['suppliers'], "SELECT * FROM Suppliers", ["Supplier_ID", "Details", "Delivery_Time", "Contact_Info"], "Suppliers")
    switch_frame(frames['suppliers'])

def show_stock():
    show_data(frames['stock'], "SELECT * FROM Stock", ["Part_ID", "Name", "Price", "Stock_Quantity", "Minimum_Stock", "Supplier_ID"], "Stock")
    switch_frame(frames['stock'])

def show_motorcycles():
    # Очистка предыдущего содержимого фрейма
    for widget in frames['motorcycles'].winfo_children():
        widget.destroy()

    # Основной фрейм для таблицы
    table_frame = tk.Frame(frames['motorcycles'], bg="#ecf0f1")
    table_frame.pack(side="top", fill="both", expand=True)

    # Фрейм для фотографии (внизу) - увеличенная высота
    global photo_frame
    photo_frame = tk.Frame(frames['motorcycles'], bg="#ecf0f1", height=250)  # Увеличиваем высоту фрейма
    photo_frame.pack(side="bottom", fill="x")

    # Таблица с данными
    tree = ttk.Treeview(table_frame, columns=["Motorcycle_ID", "Model", "Color", "Category"], show="headings")
    tree.heading("Motorcycle_ID", text="ID")
    tree.heading("Model", text="Модель")
    tree.heading("Color", text="Цвет")
    tree.heading("Category", text="Категория")

    tree.column("Motorcycle_ID", width=50)
    tree.column("Model", width=150)
    tree.column("Color", width=100)
    tree.column("Category", width=100)

    tree.pack(expand=True, fill="both")

    # Заполнение таблицы данными
    cursor.execute("SELECT Motorcycle_ID, Model, Color, Category, Photo FROM Motorcycles")
    results = cursor.fetchall()

    for row in results:
        tree.insert("", "end", values=row[:4])

    # Глобальная переменная для хранения выбранного мотоцикла
    global selected_motorcycle
    selected_motorcycle = None

    # Функция для отображения фотографии
    def show_photo(photo_data):
        for widget in photo_frame.winfo_children():
            widget.destroy()

        if photo_data:
            try:
                # Декодируем изображение из base64
                image_data = base64.b64decode(photo_data)
                photo = tk.PhotoImage(data=image_data)

                # Задаем статичный размер для изображения
                target_width = 400  # Ширина изображения
                target_height = 225  # Высота изображения

                # Масштабируем изображение до заданных размеров
                photo = photo.subsample(
                    max(1, photo.width() // target_width),
                    max(1, photo.height() // target_height)
                )

                # Отображаем изображение в Label
                photo_label = tk.Label(photo_frame, image=photo)
                photo_label.image = photo  # Сохраняем ссылку на изображение
                photo_label.pack(pady=10)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить изображение: {e}")
        else:
            tk.Label(photo_frame, text="Фотография отсутствует", bg="#ecf0f1").pack(pady=10)

    # Обработка выбора мотоцикла
    def on_select(event):
        selected_item = tree.selection()
        if selected_item:
            global selected_motorcycle
            selected_motorcycle = tree.item(selected_item[0])['values']
            cursor.execute("SELECT Photo FROM Motorcycles WHERE Motorcycle_ID = %s", (selected_motorcycle[0],))
            photo_data = cursor.fetchone()[0]
            show_photo(photo_data)

    tree.bind("<<TreeviewSelect>>", on_select)

    # Фрейм для кнопок
    button_frame = tk.Frame(frames['motorcycles'], bg="#ecf0f1")
    button_frame.pack(side="top", fill="x")

    # Кнопки для взаимодействия с таблицей
    if user_role == "Директор":
        tk.Button(button_frame, text="Добавить", command=lambda: add_data(frames['motorcycles'], ["Motorcycle_ID", "Model", "Color", "Category"], "Motorcycles"), bg="#3498db", fg="white", relief="flat",
                  font=("Helvetica", 12), width=15).pack(side="left", padx=5, pady=5)
        tk.Button(button_frame, text="Редактировать", command=lambda: edit_data(frames['motorcycles'], tree, ["Motorcycle_ID", "Model", "Color", "Category"], "Motorcycles"), bg="#f39c12", fg="white", relief="flat",
                  font=("Helvetica", 12), width=15).pack(side="left", padx=5, pady=5)
        tk.Button(button_frame, text="Удалить", command=lambda: delete_data(frames['motorcycles'], tree, ["Motorcycle_ID", "Model", "Color", "Category"], "Motorcycles"), bg="#e74c3c", fg="white", relief="flat",
                  font=("Helvetica", 12), width=15).pack(side="left", padx=5, pady=5)
    elif user_role == "Сотрудник":
        tk.Button(button_frame, text="Добавить", command=lambda: add_data(frames['motorcycles'], ["Motorcycle_ID", "Model", "Color", "Category"], "Motorcycles"), bg="#3498db", fg="white", relief="flat",
                  font=("Helvetica", 12), width=15).pack(side="left", padx=5, pady=5)
        tk.Button(button_frame, text="Редактировать", command=lambda: edit_data(frames['motorcycles'], tree, ["Motorcycle_ID", "Model", "Color", "Category"], "Motorcycles"), bg="#f39c12", fg="white", relief="flat",
                  font=("Helvetica", 12), width=15).pack(side="left", padx=5, pady=5)

    # Кнопка для загрузки фотографии
    def upload_photo():
        if selected_motorcycle is None:
            messagebox.showerror("Ошибка", "Сначала выберите мотоцикл из таблицы.")
            return

        from tkinter import filedialog
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")])
        if file_path:
            with open(file_path, "rb") as file:
                photo_data = base64.b64encode(file.read()).decode('utf-8')
            cursor.execute("UPDATE Motorcycles SET Photo = %s WHERE Motorcycle_ID = %s", (photo_data, selected_motorcycle[0]))
            conn.commit()
            show_photo(photo_data)
            messagebox.showinfo("Успех", "Фотография успешно загружена")

    upload_button = tk.Button(button_frame, text="Загрузить фото", command=upload_photo, bg="#3498db", fg="white", relief="flat",
                              font=("Helvetica", 12))
    upload_button.pack(pady=10)

    # Переключение на фрейм с мотоциклами
    switch_frame(frames['motorcycles'])

def show_assembly():
    show_data(frames['assembly'], "SELECT * FROM assembly", ["Assembly_ID", "Date", "Motorcycle_ID", "Employee_ID", "Status", "Check_Status"], "assembly")
    switch_frame(frames['assembly'])

def show_employees():
    show_data(frames['employees'], "SELECT * FROM Employees", ["Employee_ID", "Full_Name", "Position", "Contact_Info", "Role", "Password"], "Employees")
    switch_frame(frames['employees'])

def show_motorcycle_parts():
    show_data(frames['motorcycle_parts'], "SELECT * FROM Motorcycle_Parts", ["Motorcycle_Parts_ID", "Motorcycle_ID", "Part_ID", "Quantity_For_Assembly"], "Motorcycle_Parts")
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
            SELECT Date, COUNT(*) 
            FROM Assembly
            WHERE Date BETWEEN %s AND %s
            AND Status = 'Завершен'
            GROUP BY Date
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

            fig, ax = plt.subplots(figsize=(7, 5))
            ax.bar(formatted_dates , counts, color='skyblue')
            ax.set_title("Количество собранных мотоциклов", fontsize=12)
            ax.set_xlabel("Дата", fontsize=10)
            ax.set_ylabel("Количество", fontsize=10)
            ax.tick_params(axis='x', rotation=45)

            fig.tight_layout()

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

def show_current_assembly():
    # Очистка предыдущего содержимого фрейма
    for widget in frames['assembly'].winfo_children():
        widget.destroy()

    # Создание контейнера для данных
    left_frame = tk.Frame(frames['assembly'], bg="#ecf0f1")
    left_frame.pack(side="left", fill="both", expand=True)

    right_frame = tk.Frame(frames['assembly'], bg="#ecf0f1", width=300)
    right_frame.pack(side="right", fill="y")  # Текст справа

    # Запрос для получения данных о текущей сборке
    try:
        query = """
        SELECT a.Assembly_ID, m.Model, a.Date, a.Status, a.Check_Status 
        FROM assembly a
        JOIN Motorcycles m ON a.Motorcycle_ID = m.Motorcycle_ID
        WHERE a.Date = CURDATE()
        """
        cursor.execute(query)
        results = cursor.fetchall()

        if not results:
            tk.Label(left_frame, text="Нет мотоциклов в текущей сборке.", font=("Helvetica", 12), bg="#ecf0f1").pack(pady=10)
            return

        # Отображение данных в Treeview
        tree = ttk.Treeview(left_frame, columns=["Assembly_ID", "Model", "Date", "Status", "Check_Status"], show="headings")
        tree.heading("Assembly_ID", text="Assembly_ID")
        tree.heading("Model", text="Model")
        tree.heading("Date", text="Date")
        tree.heading("Status", text="Status")
        tree.heading("Check_Status", text="Check_Status")

        tree.column("Assembly_ID", width=100)
        tree.column("Model", width=200)
        tree.column("Date", width=100)
        tree.column("Status", width=150)
        tree.column("Check_Status", width=120)

        tree.pack(expand=True, fill="both")

        for row in results:
            tree.insert("", "end", values=row)

    except mysql.connector.Error as err:
        messagebox.showerror("Ошибка", f"Ошибка при получении данных: {err}")

    # Добавляем текстовую метку справа
    label = tk.Label(right_frame, text="Мотоциклы, находящиеся в процессе сборки сегодня", font=("Helvetica", 16, "bold"), bg="#2c3e50", fg="#ffffff",
                     wraplength=400, justify="center", padx=20, pady=20, bd=2, relief="ridge")
    label.pack(pady=20, padx=10)

    # Переключение на фрейм с текущей сборкой
    switch_frame(frames['assembly'])

# Авторизация
def login():
    def authenticate():
        username = username_entry.get()
        password = password_entry.get()
        try:
            # Проверяем логин и пароль в базе
            query = "SELECT Role FROM Employees WHERE Employee_ID = %s AND Password = %s"
            cursor.execute(query, (username, password))
            result = cursor.fetchone()
            if result:
                global user_role
                user_role = result[0]
                messagebox.showinfo("Успех", f"Вы вошли как {user_role}")
                login_frame.destroy()
                main_menu()
                show_current_assembly()
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

    if user_role == "Директор":
        tk.Button(menu_frame, text="Поставщики", command=show_suppliers, bg="#2980b9", fg="white", relief="flat",
                  font=("Helvetica", 10), width=14).pack(side="left", padx=5, pady=5)
        tk.Button(menu_frame, text="Склад", command=show_stock, bg="#2980b9", fg="white", relief="flat",
                  font=("Helvetica", 10), width=14).pack(side="left", padx=5, pady=5)
        tk.Button(menu_frame, text="Мотоциклы", command=show_motorcycles, bg="#2980b9", fg="white", relief="flat",
                  font=("Helvetica", 10), width=14).pack(side="left", padx=5, pady=5)
        tk.Button(menu_frame, text="Сборка", command=show_assembly, bg="#2980b9", fg="white", relief="flat",
                  font=("Helvetica", 10), width=14).pack(side="left", padx=5, pady=5)
        tk.Button(menu_frame, text="Отчет по сборке", command=show_motorcycle_assembly_report, bg="#2980b9", fg="white", relief="flat",
                  font=("Helvetica", 10), width=14).pack(side="left", padx=5, pady=5)
        tk.Button(menu_frame, text="Сотрудники", command=show_employees, bg="#2980b9", fg="white", relief="flat",
                  font=("Helvetica", 10), width=13).pack(side="left", padx=5, pady=5)
        tk.Button(menu_frame, text="Детали мотоциклов", command=show_motorcycle_parts, bg="#2980b9", fg="white", relief="flat",
                  font=("Helvetica", 10), width=15).pack(side="left", padx=5, pady=5)
        tk.Button(menu_frame, text="Домой", command=show_current_assembly, bg="#66CD00", fg="white",
                                relief="flat").pack(side="left", padx=10, pady=5)
        tk.Button(menu_frame, text="Выход", command=close_application, bg="#e74c3c", fg="white", relief="flat",
                  font=("Helvetica", 10), width=12).pack(side="right", padx=5, pady=5)
    elif user_role == "Сотрудник":
        tk.Button(menu_frame, text="Склад", command=show_stock, bg="#2980b9", fg="white", relief="flat",
                  font=("Helvetica", 10), width=16).pack(side="left", padx=5, pady=5)
        tk.Button(menu_frame, text="Мотоциклы", command=show_motorcycles, bg="#2980b9", fg="white", relief="flat",
                  font=("Helvetica", 10), width=16).pack(side="left", padx=5, pady=5)
        tk.Button(menu_frame, text="Сборка", command=show_assembly, bg="#2980b9", fg="white", relief="flat",
                  font=("Helvetica", 10), width=16).pack(side="left", padx=5, pady=5)
        tk.Button(menu_frame, text="Детали мотоциклов", command=show_motorcycle_parts, bg="#2980b9", fg="white", relief="flat",
                  font=("Helvetica", 10), width=16).pack(side="left", padx=5, pady=5)
        tk.Button(menu_frame, text="Домой", command=show_current_assembly, bg="#66CD00", fg="white",
                  relief="flat").pack(side="left", padx=10, pady=5)
        tk.Button(menu_frame, text="Выход", command=close_application, bg="#e74c3c", fg="white", relief="flat",
                  font=("Helvetica", 10), width=9).pack(side="right", padx=5, pady=5)

def close_application():
    close_db_connection()
    root.destroy()

connect_to_db()
login()
root.protocol("WM_DELETE_WINDOW", close_db_connection)
root.mainloop()
