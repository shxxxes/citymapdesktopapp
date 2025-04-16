import ttkbootstrap as ttk
from ttkbootstrap import Style
from tkinter import PhotoImage, messagebox
from PIL import Image, ImageTk
import os
import mysql.connector
from reviews import show_add_review_window  # Импорт функции открытия окна добавления отзыва
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

def show_marker_info_window(root, loc_id, name, address, description, image_path, username):

    # Создаём окно
    info_window = ttk.Toplevel(root)
    info_window.title("Информация о локации")
    info_window.geometry("650x750")
    info_window.configure(bg=Style().colors.bg)

    # Заголовок
    header_frame = ttk.Frame(info_window, padding=10)
    header_frame.pack(fill="x", side="top")
    ttk.Label(header_frame, text="Информация о локации", font=("Arial", 14, "bold"),
              background=Style().colors.bg).pack()

    # Основной фрейм
    content_frame = ttk.Frame(info_window, padding=10)
    content_frame.pack(fill="both", expand=True)

    # Поля информации
    def create_info_section(parent, label_text, value_text):
        frame = ttk.LabelFrame(parent, text=label_text, padding=10, bootstyle="primary")
        frame.pack(fill="x", padx=5, pady=5)
        ttk.Label(frame, text=value_text, font=("Arial", 12), wraplength=560).pack(anchor="w")

    create_info_section(content_frame, "Название", name)
    create_info_section(content_frame, "Адрес", address)
    create_info_section(content_frame, "Описание", description)

    # Фото (если есть)
    if image_path and os.path.exists(image_path):
        img_frame = ttk.LabelFrame(content_frame, text="Фото", padding=10, bootstyle="primary")
        img_frame.pack(fill="x", padx=5, pady=5)

        img = Image.open(image_path)
        img = img.resize((200, 150), Image.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)

        img_label = ttk.Label(img_frame, image=img_tk)
        img_label.image = img_tk  # Нужно сохранить ссылку, чтобы фото не пропадало
        img_label.pack()

    # Получаем отзывы
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        cursor.execute("""
            SELECT users.name, reviews.rating, reviews.review_text
            FROM reviews
            JOIN users ON reviews.user_id = users.id
            WHERE reviews.location_id = %s
        """, (loc_id,))
        reviews = cursor.fetchall()
        connection.close()

        if reviews:
            review_frame = ttk.LabelFrame(content_frame, text="Отзывы", padding=10, bootstyle="primary")
            review_frame.pack(fill="both", expand=True, padx=5, pady=5)

            # Для каждого отзыва создаём метку с данными
            for user_name, rating, review_text in reviews:
                review_text_display = f"Рейтинг: {rating}\nОтзыв: {review_text}"
                review_label = ttk.Label(review_frame, text=f"Пользователь: {user_name}\n{review_text_display}",
                                         font=("Arial", 12), wraplength=560, anchor="w")
                review_label.pack(padx=10, pady=5)

        else:
            # Если нет отзывов, выводим соответствующее сообщение
            no_reviews_label = ttk.Label(content_frame, text="Отзывов пока нет.", font=("Arial", 12),
                                         background=Style().colors.bg)
            no_reviews_label.pack(padx=10, pady=5)

    except mysql.connector.Error as err:
        messagebox.showerror("Ошибка", f"Не удалось получить отзывы: {err}")

    # Кнопки
    button_frame = ttk.Frame(info_window, padding=10)
    button_frame.pack(fill="x", side="bottom")

    # Функция для открытия окна с добавлением отзыва
    def leave_review():
        show_add_review_window(loc_id, username)

    review_button = ttk.Button(button_frame, text="Оставить отзыв", command=leave_review, bootstyle="success")
    review_button.pack(side="left", padx=5, pady=5)

    close_button = ttk.Button(button_frame, text="Закрыть", command=info_window.destroy, bootstyle="danger-outline")
    close_button.pack(side="right", padx=5, pady=5)

    info_window.mainloop()