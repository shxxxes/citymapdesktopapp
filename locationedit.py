from ttkbootstrap import Style
import ttkbootstrap as ttk
from tkinter import messagebox
from tkinter import filedialog
import mysql.connector
from PIL import Image, ImageTk
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

def show_location_edit_window(location_id):
    style = Style()
    edit_window = ttk.Toplevel()
    edit_window.title("Редактировать локацию")
    edit_window.geometry("500x500")
    edit_window.configure(bg=style.colors.bg)

    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

        cursor.execute("SELECT name, description, type, image_path FROM locations WHERE id = %s", (location_id,))
        location = cursor.fetchone()
        connection.close()

        if location:
            location_name, description, location_type, image_path = location

            # Поле для изменения названия
            ttk.Label(edit_window, text="Название:", font=("Arial", 12), bootstyle="info").pack(pady=10)
            name_entry = ttk.Entry(edit_window, font=("Arial", 12))
            name_entry.insert(0, location_name)
            name_entry.pack(pady=5)

            # Поле для изменения описания
            ttk.Label(edit_window, text="Описание:", font=("Arial", 12), bootstyle="info").pack(pady=10)
            description_entry = ttk.Entry(edit_window, font=("Arial", 12))
            description_entry.insert(0, description)
            description_entry.pack(pady=5)

            def get_location_types():
                try:
                    connection = mysql.connector.connect(**DB_CONFIG)
                    cursor = connection.cursor()
                    cursor.execute("SELECT DISTINCT type FROM locations")
                    types = [row[0] for row in cursor.fetchall()]
                    connection.close()
                    return types
                except mysql.connector.Error as err:
                    messagebox.showerror("Ошибка", f"Не удалось загрузить типы локаций: {err}")
                    return []

            ttk.Label(edit_window, text="Тип:", font=("Arial", 12), bootstyle="info").pack(pady=10)
            location_types = get_location_types()
            type_combobox = ttk.Combobox(edit_window, values=location_types, state="readonly", font=("Arial", 12))
            type_combobox.set(location_type)
            type_combobox.pack(pady=5)

            img_label = None
            if image_path:
                try:
                    img = Image.open(image_path)
                    img = img.resize((100, 100), Image.Resampling.LANCZOS)
                    img_tk = ImageTk.PhotoImage(img)

                    img_label = ttk.Label(edit_window, image=img_tk)
                    img_label.image = img_tk
                    img_label.pack(pady=10)
                except Exception as e:
                    print(f"Ошибка при загрузке изображения: {e}")
                    img_label = ttk.Label(edit_window, text="Ошибка загрузки фото", font=("Arial", 12, "italic"))
                    img_label.pack(pady=10)

            # Кнопка для изменения изображения
            def change_image():
                new_image_path = filedialog.askopenfilename(title="Выберите изображение", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
                if new_image_path:
                    try:
                        img = Image.open(new_image_path)
                        img = img.resize((100, 100), Image.Resampling.LANCZOS)
                        img_tk = ImageTk.PhotoImage(img)

                        img_label.config(image=img_tk)
                        img_label.image = img_tk
                        image_path = new_image_path
                    except Exception as e:
                        messagebox.showerror("Ошибка", f"Не удалось загрузить изображение: {e}")

            # Кнопка для изменения изображения
            ttk.Button(edit_window, text="Выбрать новое изображение", command=change_image, bootstyle="info-outline").pack(pady=10)

            # Функция для сохранения изменений
            def save_changes():
                new_name = name_entry.get().strip()
                new_description = description_entry.get().strip()
                new_type = type_combobox.get().strip()

                if not new_name or not new_description or not new_type:
                    messagebox.showwarning("Ошибка", "Все поля должны быть заполнены.")
                    return

                try:
                    connection = mysql.connector.connect(**DB_CONFIG)
                    cursor = connection.cursor()


                    update_query = """
                    UPDATE locations
                    SET name = %s, description = %s, type = %s, image_path = %s
                    WHERE id = %s
                    """
                    cursor.execute(update_query, (new_name, new_description, new_type, image_path, location_id))

                    connection.commit()
                    connection.close()

                    messagebox.showinfo("Успех", "Данные локации успешно обновлены.")
                    edit_window.destroy()
                except mysql.connector.Error as err:
                    messagebox.showerror("Ошибка", f"Не удалось обновить локацию: {err}")

            # Кнопка для сохранения изменений
            ttk.Button(edit_window, text="Сохранить", command=save_changes, bootstyle="success-outline", width=20).pack(pady=20)
        else:
            messagebox.showerror("Ошибка", "Локация не найдена.")

    except mysql.connector.Error as err:
        messagebox.showerror("Ошибка", f"Ошибка подключения к базе данных: {err}")

    edit_window.mainloop()