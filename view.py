import tkinter as tk
from tkinter import messagebox
from ttkbootstrap import Style
from ttkbootstrap.constants import *
import ttkbootstrap as ttk
from PIL import Image, ImageTk
import mysql.connector
import reviews
import locationedit
import locationadd
from map import show_map_window
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

def show_main_window(username, root):
    if not hasattr(show_main_window, "main_window") or not show_main_window.main_window.winfo_exists():
        style = Style("flatly")

        main_window = ttk.Toplevel(root)
        main_window.title("Главное окно")
        main_window.geometry("1440x920")
        main_window.configure(bg=style.colors.bg)

        show_main_window.main_window = main_window

        # Панель с информацией о пользователе
        header_frame = ttk.Frame(main_window, padding=10)
        header_frame.pack(fill="x", side="top", anchor="w")

        label_user = ttk.Label(header_frame, text=f"Авторизован: {username}", font=("Arial", 12),
                               background=style.colors.bg)
        label_user.pack(side="left", padx=10)

        # Кнопка выхода
        def logout():
            main_window.withdraw()
            root.deiconify()

        logout_button = ttk.Button(header_frame, text="Выйти", command=logout, bootstyle="danger-outline")
        logout_button.pack(side="right", padx=10)

        main_frame = ttk.Frame(main_window)
        main_frame.pack(fill="both", expand=True)

        menu_frame = ttk.Frame(main_frame, padding=10)
        menu_frame.pack(side="left", fill="y", padx=10, pady=10)

        search_label = ttk.Label(menu_frame, text="Поиск по названию:", font=("Arial", 12))
        search_label.pack(anchor="w", pady=5)

        search_entry = ttk.Entry(menu_frame)
        search_entry.pack(fill="x", pady=5)

        filter_label = ttk.Label(menu_frame, text="Фильтр по типу:", font=("Arial", 12))
        filter_label.pack(anchor="w", pady=5)

        def open_map_window():
            show_map_window(main_window, username)
        map_button = ttk.Button(header_frame, text="Перейти к карте", command=lambda: show_map_window(main_window, username), bootstyle="secondary-outline")
        map_button.pack(side="left", padx=10)

        def get_location_types():
            try:
                connection = mysql.connector.connect(**DB_CONFIG)
                cursor = connection.cursor()
                cursor.execute("SELECT DISTINCT type FROM locations")
                types = [row[0] for row in cursor.fetchall()]
                connection.close()
                return ["Все"] + types
            except mysql.connector.Error as err:
                messagebox.showerror("Ошибка", f"Не удалось загрузить типы локаций: {err}")
                return ["Все"]

        filter_options = get_location_types()
        filter_var = tk.StringVar(value="Все")
        filter_combobox = ttk.Combobox(menu_frame, textvariable=filter_var, values=filter_options, state="readonly")
        filter_combobox.pack(fill="x", pady=5)

        sort_label = ttk.Label(menu_frame, text="Сортировка:", font=("Arial", 12))
        sort_label.pack(anchor="w", pady=5)

        sort_options = ["По названию (А-Я)", "По названию (Я-А)", "По рейтингу (возр.)", "По рейтингу (убыв.)", "По дате добавления (новые)", "По дате добавления (старые)"]
        sort_var = tk.StringVar(value="По названию (А-Я)")
        sort_combobox = ttk.Combobox(menu_frame, textvariable=sort_var, values=sort_options, state="readonly")
        sort_combobox.pack(fill="x", pady=5)

        # Кнопка "Сбросить"
        def reset_filters():
            search_entry.delete(0, 'end')
            filter_var.set("Все")
            sort_var.set("По названию (А-Я)")
            show_locations()

        reset_button = ttk.Button(menu_frame, text="Сбросить", command=reset_filters, bootstyle="info")
        reset_button.pack(fill="x", pady=10)

        # Кнопка "Применить"
        def apply_filters():
            show_locations()

        apply_button = ttk.Button(menu_frame, text="Применить", command=apply_filters, bootstyle="primary")
        apply_button.pack(fill="x", pady=10)

        def add_location():
            locationadd.show_location_add_window(username, style)

        add_location_button = ttk.Button(menu_frame, text="Добавить локацию", command=add_location, bootstyle="success")
        add_location_button.pack(fill="x", pady=10)

        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side="left", fill="both", expand=True)

        canvas = tk.Canvas(right_frame, bg=style.colors.bg)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        canvas.config(yscrollcommand=scrollbar.set)

        frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=frame, anchor="nw")

        def show_locations():
            for widget in frame.winfo_children():
                widget.destroy()

            try:
                connection = mysql.connector.connect(**DB_CONFIG)
                cursor = connection.cursor()

                query = """
                    SELECT locations.id, locations.name, locations.type, locations.description, 
                           COALESCE(AVG(reviews.rating), 0) AS average_rating, locations.image_path, locations.created_at
                    FROM locations
                    LEFT JOIN reviews ON locations.id = reviews.location_id
                    """
                conditions = []

                selected_filter = filter_var.get()
                if selected_filter != "Все":
                    conditions.append(f"locations.type = '{selected_filter}'")

                search_text = search_entry.get().strip()
                if search_text:
                    conditions.append(f"locations.name LIKE '%{search_text}%'")

                if conditions:
                    query += " WHERE " + " AND ".join(conditions)

                query += " GROUP BY locations.id"

                selected_sort = sort_var.get()
                if selected_sort == "По названию (А-Я)":
                    query += " ORDER BY locations.name ASC"
                elif selected_sort == "По названию (Я-А)":
                    query += " ORDER BY locations.name DESC"
                elif selected_sort == "По рейтингу (возр.)":
                    query += " ORDER BY average_rating ASC"
                elif selected_sort == "По рейтингу (убыв.)":
                    query += " ORDER BY average_rating DESC"
                elif selected_sort == "По дате добавления (новые)":
                    query += " ORDER BY locations.created_at DESC"
                elif selected_sort == "По дате добавления (старые)":
                    query += " ORDER BY locations.created_at ASC"

                cursor.execute(query)
                locations = cursor.fetchall()
                connection.close()

                for index, location in enumerate(locations):
                    location_id, location_name, location_type, description, average_rating, image_path, created_at = location

                    location_frame = ttk.Frame(frame, padding=10, relief="solid")
                    location_frame.grid(row=index, column=0, pady=10, padx=20, sticky="ew")

                    frame.columnconfigure(0, weight=1)

                    ttk.Label(location_frame, text=location_name, font=("Arial", 14, "bold"), bootstyle="info").grid(
                        row=0, column=0, sticky="w")
                    ttk.Label(location_frame, text=f"Тип: {location_type}", font=("Arial", 12)).grid(row=1, column=0,
                                                                                                     sticky="w")
                    ttk.Label(location_frame, text=f"Описание: {description}", font=("Arial", 12)).grid(row=2, column=0,
                                                                                                        sticky="w")
                    ttk.Label(location_frame, text=f"Рейтинг: {average_rating:.2f}", font=("Arial", 12, "italic")).grid(
                        row=3, column=0, sticky="w")
                    ttk.Label(location_frame, text=f"Дата добавления: {created_at}", font=("Arial", 12, "italic")).grid(
                        row=4, column=0, sticky="w")

                    if image_path:
                        try:
                            img = Image.open(image_path)
                            img = img.resize((100, 100), Image.Resampling.LANCZOS)
                            img_tk = ImageTk.PhotoImage(img)

                            image_label = ttk.Label(location_frame, image=img_tk)
                            image_label.image = img_tk
                            image_label.grid(row=0, column=1, rowspan=4, padx=10)
                        except Exception as e:
                            print(f"Ошибка при загрузке изображения: {e}")
                            ttk.Label(location_frame, text="Ошибка загрузки фото", font=("Arial", 12, "italic")).grid(
                                row=0, column=1, rowspan=4, padx=10)

                    button_frame = ttk.Frame(location_frame)
                    button_frame.grid(row=5, column=0, columnspan=2, pady=5, sticky="w")

                    # Кнопка "Оставить отзыв"
                    review_button = ttk.Button(button_frame, text="Оставить отзыв",
                                               command=lambda loc_id=location_id: open_review_window(loc_id),
                                               bootstyle="success-outline")
                    review_button.grid(row=0, column=0, padx=5)

                    # Кнопка "Посмотреть отзывы"
                    view_reviews_button = ttk.Button(button_frame, text="Посмотреть отзывы",
                                                     command=lambda loc_id=location_id: open_reviews_window(loc_id),
                                                     bootstyle="info-outline")
                    view_reviews_button.grid(row=0, column=1, padx=5)

                    # Кнопка "Редактировать"
                    edit_button = ttk.Button(button_frame, text="Редактировать",
                                             command=lambda loc_id=location_id: open_edit_window(loc_id),
                                             bootstyle="primary-outline")
                    edit_button.grid(row=0, column=2, padx=5)

                frame.update_idletasks()
                canvas.config(scrollregion=canvas.bbox("all"))
            except mysql.connector.Error as err:
                messagebox.showerror("Ошибка", f"Не удалось получить локации: {err}")

        def open_reviews_window(location_id):
            reviews.show_reviews_window(location_id)

        def open_review_window(location_id):
            reviews.show_add_review_window(location_id, username)

        def open_edit_window(location_id):
            locationedit.show_location_edit_window(location_id)

        def on_mouse_wheel(event):
            canvas.yview_scroll(-1 * int(event.delta / 120), "units")

        main_window.bind_all("<MouseWheel>", on_mouse_wheel)
        show_locations()

    else:
        show_main_window.main_window.deiconify()

    root.withdraw()
