import tkinter as tk
from ttkbootstrap import Style
import ttkbootstrap as ttk
from tkinter import messagebox
from tkintermapview import TkinterMapView
import mysql.connector
import requests
import locationadd
import markerview
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

YANDEX_API_KEY = "d0de55f4-e8bb-4713-8587-49c440ed8cc8"

# Создание стиля для интерфейса
style = Style("flatly")

def show_map_window(root, username):
    map_window = ttk.Toplevel(root)
    map_window.title("Карта")
    map_window.geometry("1440x920")
    map_window.configure(bg=style.colors.bg)

    # Заголовок окна карты
    header_frame = ttk.Frame(map_window, padding=10)
    header_frame.pack(fill="x", side="top", anchor="w")

    ttk.Label(header_frame, text="Интерактивная карта", font=("Arial", 14, "bold"), background=style.colors.bg).pack(side="left", padx=10)

    # Кнопка "Назад" для возврата в главное окно
    def go_back():
        map_window.destroy()

    back_button = ttk.Button(header_frame, text="Назад", command=go_back, bootstyle="secondary-outline")
    back_button.pack(side="right", padx=10)

    # Карта
    map_frame = ttk.Frame(map_window)
    map_frame.pack(fill="both", expand=True, padx=10, pady=10)

    map_widget = TkinterMapView(map_frame, width=1400, height=800, corner_radius=0)
    map_widget.pack(fill="both", expand=True)

    # Центрируем карту на определенные координаты
    map_widget.set_position(55.751244, 37.618423)  # Москва, Россия
    map_widget.set_zoom(10)

    # Функция открытия информации о локации
    def open_location_info(loc_id, username):
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor()
            cursor.execute("SELECT name, address, description, image_path FROM locations WHERE id = %s", (loc_id,))
            location_info = cursor.fetchone()
            connection.close()

            if location_info:
                name, address, description, image_path = location_info + (None,) * (4 - len(location_info))
                markerview.show_marker_info_window(root, loc_id, name, address, description, image_path, username)
            else:
                messagebox.showwarning("Ошибка", "Локация не найдена")

        except mysql.connector.Error as err:
            messagebox.showerror("Ошибка", f"Не удалось получить информацию о локации: {err}")

    # Передача `username` в `marker.command`
    def load_markers_from_db(username):
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor()
            cursor.execute("SELECT id, name, latitude, longitude FROM locations")
            locations = cursor.fetchall()
            connection.close()

            for location_id, name, lat, lon in locations:
                if lat is not None and lon is not None:
                    marker = map_widget.set_marker(lat, lon, text=name)
                    marker.command = lambda m=marker, loc_id=location_id: open_location_info(loc_id, username)

        except mysql.connector.Error as err:
            messagebox.showerror("Ошибка", f"Не удалось загрузить локации: {err}")

    load_markers_from_db(username)

    # Поле ввода для поиска адреса
    search_frame = ttk.Frame(map_window, padding=10)
    search_frame.pack(fill="x", side="bottom", anchor="w")

    ttk.Label(search_frame, text="Введите адрес:", font=("Arial", 12)).pack(side="left", padx=5)
    address_entry = ttk.Entry(search_frame, width=50)
    address_entry.pack(side="left", padx=5)

    def search_address():
        address = address_entry.get().strip()
        if not address:
            messagebox.showwarning("Предупреждение", "Введите адрес для поиска!")
            return

        geocode_url = f"https://geocode-maps.yandex.ru/1.x/?apikey={YANDEX_API_KEY}&geocode={address}&format=json"
        try:
            response = requests.get(geocode_url)
            response.raise_for_status()
            data = response.json()
            geo_object = data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
            pos = geo_object["Point"]["pos"]
            lon, lat = map(float, pos.split())
            map_widget.set_position(lat, lon)
            map_widget.set_zoom(15)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось найти адрес: {e}")

    search_button = ttk.Button(search_frame, text="Найти", command=search_address, bootstyle="primary")
    search_button.pack(side="left", padx=5)

    def on_map_spacebar(event):
        lat, lon = map_widget.get_position()
        if lat is not None and lon is not None:
            reverse_geocode_url = f"https://geocode-maps.yandex.ru/1.x/?apikey={YANDEX_API_KEY}&geocode={lon},{lat}&format=json"
            try:
                response = requests.get(reverse_geocode_url)
                response.raise_for_status()
                data = response.json()
                geo_object = data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
                address = geo_object["name"]

                map_widget.set_marker(lat, lon)

                map_window.after(1000, lambda: locationadd.show_location_add_window(lat, lon, address, style))
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось получить адрес: {e}")

    map_window.bind("<Return>", on_map_spacebar)
    map_window.mainloop()