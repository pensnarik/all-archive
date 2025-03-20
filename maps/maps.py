#!/usr/bin/env python3

from flask import Flask, jsonify
import psycopg
from psycopg.rows import dict_row  # Для получения данных в виде словаря

app = Flask(__name__)

# Параметры подключения к базе данных
DB_CONFIG = {
    "dbname": "allarchive",
    "user": "allarchive",
    "password": "allarchive",
    "host": "localhost",
    "port": 5432
}

def get_gps_coords():
    """
    Получает данные из таблицы gps_coords и возвращает их в виде списка словарей.
    """
    try:
        # Подключение к базе данных
        with psycopg.connect(**DB_CONFIG) as conn:
            with conn.cursor(row_factory=dict_row) as cursor:  # Используем dict_row для получения данных в виде словаря
                # Выполняем SQL-запрос
                query = "SELECT id, file_id, lat, lon FROM aa.gps_coords WHERE lat IS NOT NULL;"
                cursor.execute(query)
                results = cursor.fetchall()

        return results
    except Exception as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return []

@app.route('/gps-coords', methods=['GET'])
def gps_coords():
    """
    Возвращает координаты в формате JSON.
    """
    data = get_gps_coords()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
