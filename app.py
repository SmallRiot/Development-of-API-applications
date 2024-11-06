from flask import Flask, jsonify, request, abort
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)

taxi_fleet = []
next_id = 1

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
    return jsonify(taxi_fleet)

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
    global next_id
    if not request.json or 'number' not in request.json:
        abort(400)
    taxi = {
        'id': next_id,
        'number': request.json['number'],
        'driver': request.json.get('driver', "Unknown"),
        'status': request.json.get('status', "free")
    }
    next_id += 1
    taxi_fleet.append(taxi)
    return jsonify(taxi), 201

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
    taxis_with_status = [taxi for taxi in taxi_fleet if taxi['status'] == status]
    return jsonify(taxis_with_status)

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
    global taxi_fleet, next_id
    taxi_fleet = []
    next_id = 1
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
    taxi = next((t for t in taxi_fleet if t['id'] == taxi_id), None)
    if taxi is None:
        abort(404)
    if not request.json:
        abort(400)
    
    taxi['number'] = request.json.get('number', taxi['number'])
    taxi['driver'] = request.json.get('driver', taxi['driver'])
    taxi['status'] = request.json.get('status', taxi['status'])
    
    return jsonify(taxi)

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
    global taxi_fleet
    taxi_fleet = [t for t in taxi_fleet if t['id'] != taxi_id]
    return jsonify({'result': True})

if __name__ == '__main__':
    app.run(debug=True)
