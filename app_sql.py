from flask import Flask, jsonify, request, abort
from flasgger import Swagger
import sqlite3

app = Flask(__name__)
swagger = Swagger(app)

def init_db():
    with sqlite3.connect("taxi_fleet.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS taxi_fleet (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                number TEXT NOT NULL,
                driver TEXT NOT NULL,
                status TEXT NOT NULL
            )
        ''')
        conn.commit()

init_db()

@app.route('/api/taxis', methods=['GET'])
def get_taxis():
    """
    Получить список всех такси
    ---
    responses:
      200:
        description: Список всех такси
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                example: 1
              number:
                type: string
                example: "123ABC"
              driver:
                type: string
                example: "Иван Иванов"
              status:
                type: string
                example: "free"
    """
    with sqlite3.connect("taxi_fleet.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM taxi_fleet")
        taxis = cursor.fetchall()
        return jsonify([{
            'id': row[0],
            'number': row[1],
            'driver': row[2],
            'status': row[3]
        } for row in taxis])

@app.route('/api/taxis', methods=['POST'])
def create_taxi():
    """
    Добавить новое такси
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            number:
              type: string
              example: "123ABC"
            driver:
              type: string
              example: "Иван Иванов"
            status:
              type: string
              example: "free"
    responses:
      201:
        description: Новое такси добавлено
        schema:
          type: object
          properties:
            id:
              type: integer
            number:
              type: string
            driver:
              type: string
            status:
              type: string
    """
    if not request.json or 'number' not in request.json:
        abort(400)
    with sqlite3.connect("taxi_fleet.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO taxi_fleet (number, driver, status) 
            VALUES (?, ?, ?)
        ''', (
            request.json['number'],
            request.json.get('driver', "Unknown"),
            request.json.get('status', "free")
        ))
        conn.commit()
        taxi_id = cursor.lastrowid
        return jsonify({
            'id': taxi_id,
            'number': request.json['number'],
            'driver': request.json.get('driver', "Unknown"),
            'status': request.json.get('status', "free")
        }), 201

@app.route('/api/taxis/status/<string:status>', methods=['GET'])
def get_taxis_by_status(status):
    """
    Получить список такси по статусу
    ---
    parameters:
      - name: status
        in: path
        required: true
        type: string
        description: Статус такси (например, 'free' или 'busy')
    responses:
      200:
        description: Список такси с указанным статусом
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                example: 1
              number:
                type: string
                example: "123ABC"
              driver:
                type: string
                example: "Иван Иванов"
              status:
                type: string
                example: "free"
    """
    with sqlite3.connect("taxi_fleet.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM taxi_fleet WHERE status = ?", (status,))
        taxis = cursor.fetchall()
        return jsonify([{
            'id': row[0],
            'number': row[1],
            'driver': row[2],
            'status': row[3]
        } for row in taxis])

@app.route('/api/taxis/reset', methods=['DELETE'])
def reset_taxi_fleet():
    """
    Сбросить информацию о таксопарке
    ---
    responses:
      200:
        description: Все данные таксопарка удалены
        schema:
          type: object
          properties:
            result:
              type: boolean
              example: true
    """
    with sqlite3.connect("taxi_fleet.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM taxi_fleet")
        conn.commit()
        return jsonify({'result': True})

@app.route('/api/taxis/<int:taxi_id>', methods=['PUT'])
def update_taxi(taxi_id):
    """
    Обновить информацию о такси по ID
    ---
    parameters:
      - name: taxi_id
        in: path
        required: true
        type: integer
        description: ID такси для обновления
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            number:
              type: string
              example: "123ABC"
            driver:
              type: string
              example: "Иван Иванов"
            status:
              type: string
              example: "в пути"
    responses:
      200:
        description: Информация о такси обновлена
        schema:
          type: object
          properties:
            id:
              type: integer
            number:
              type: string
            driver:
              type: string
            status:
              type: string
    """
    if not request.json:
        abort(400)
    with sqlite3.connect("taxi_fleet.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM taxi_fleet WHERE id = ?", (taxi_id,))
        taxi = cursor.fetchone()
        if not taxi:
            abort(404)

        cursor.execute('''
            UPDATE taxi_fleet
            SET number = ?, driver = ?, status = ?
            WHERE id = ?
        ''', (
            request.json.get('number', taxi[1]),
            request.json.get('driver', taxi[2]),
            request.json.get('status', taxi[3]),
            taxi_id
        ))
        conn.commit()
        return jsonify({
            'id': taxi_id,
            'number': request.json.get('number', taxi[1]),
            'driver': request.json.get('driver', taxi[2]),
            'status': request.json.get('status', taxi[3])
        })

@app.route('/api/taxis/<int:taxi_id>', methods=['DELETE'])
def delete_taxi(taxi_id):
    """
    Удалить такси по ID
    ---
    parameters:
      - name: taxi_id
        in: path
        required: true
        type: integer
        description: ID такси для удаления
    responses:
      200:
        description: Такси удалено
        schema:
          type: object
          properties:
            result:
              type: boolean
              example: true
    """
    with sqlite3.connect("taxi_fleet.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM taxi_fleet WHERE id = ?", (taxi_id,))
        if cursor.rowcount == 0:
            abort(404)
        conn.commit()
        return jsonify({'result': True})

if __name__ == '__main__':
    app.run(debug=True)
