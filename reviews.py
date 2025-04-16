from ttkbootstrap import Style
from ttkbootstrap.constants import *
import ttkbootstrap as ttk
from tkinter import messagebox
import mysql.connector
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


def show_reviews_window(location_id):
    style = Style()
    reviews_window = ttk.Toplevel()
    reviews_window.title("Отзывы о локации")
    reviews_window.geometry("600x400")
    reviews_window.configure(bg=style.colors.bg)

    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

        query = """
        SELECT reviews.rating, reviews.review_text, users.name 
        FROM reviews
        JOIN users ON reviews.user_id = users.id
        WHERE reviews.location_id = %s
        """
        cursor.execute(query, (location_id,))
        reviews_data = cursor.fetchall()

        connection.close()

        if not reviews_data:
            ttk.Label(reviews_window, text="Нет отзывов для этой локации.", font=("Arial", 12), bootstyle="info").pack(pady=10)
        else:
            for review in reviews_data:
                rating, review_text, username = review
                review_frame = ttk.Frame(reviews_window, padding=10)
                review_frame.pack(fill="x", pady=5)

                ttk.Label(review_frame, text=f"Оценка: {rating}/5", font=("Arial", 12, "bold")).pack(anchor="w")
                ttk.Label(review_frame, text=f"Отзыв: {review_text}", font=("Arial", 12)).pack(anchor="w")
                ttk.Label(review_frame, text=f"Пользователь: {username}", font=("Arial", 12, "italic")).pack(anchor="w")

        # Кнопка "Назад"
        def go_back():
            reviews_window.destroy()

        back_button = ttk.Button(reviews_window, text="Назад", command=go_back, bootstyle="secondary-outline")
        back_button.pack(pady=20)

        reviews_window.minsize(600, 400)
        reviews_window.mainloop()

    except mysql.connector.Error as err:
        messagebox.showerror("Ошибка", f"Не удалось получить отзывы: {err}")


# Функция для добавления отзыва
def show_add_review_window(location_id, username):
    style = Style()
    review_window = ttk.Toplevel()
    review_window.title("Добавить отзыв")
    review_window.geometry("600x400")
    review_window.configure(bg=style.colors.bg)

    # Поля для ввода отзыва
    ttk.Label(review_window, text="Оценка (1-5):", font=("Arial", 12)).pack(pady=10)
    rating_var = ttk.Combobox(review_window, values=[1, 2, 3, 4, 5], state="readonly")
    rating_var.pack(pady=5)
    rating_var.set(5)

    ttk.Label(review_window, text="Отзыв:", font=("Arial", 12)).pack(pady=10)
    review_text = ttk.Text(review_window, height=5, width=40)
    review_text.pack(pady=5)

    def save_review():
        review_content = review_text.get("1.0", "end-1c").strip()
        rating = rating_var.get()

        if not review_content:
            messagebox.showwarning("Ошибка", "Отзыв не может быть пустым.")
            return

        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor()

            query = """
            INSERT INTO reviews (location_id, user_id, rating, review_text)
            VALUES (%s, (SELECT id FROM users WHERE name = %s LIMIT 1), %s, %s)
            """
            cursor.execute(query, (location_id, username, rating, review_content))

            connection.commit()
            connection.close()

            messagebox.showinfo("Успех", "Ваш отзыв успешно добавлен.")
            review_window.destroy()
        except mysql.connector.Error as err:
            messagebox.showerror("Ошибка", f"Не удалось добавить отзыв: {err}")

    # Кнопка для сохранения отзыва
    ttk.Button(
        review_window,
        text="Отправить отзыв",
        command=save_review,
        bootstyle="success-outline",
        width=20
    ).pack(pady=20)

    # Кнопка "Назад"
    def go_back():
        review_window.destroy()

    back_button = ttk.Button(review_window, text="Назад", command=go_back, bootstyle="secondary-outline")
    back_button.pack(pady=10)

    review_window.minsize(500, 400)
    review_window.mainloop()