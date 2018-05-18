from flask import jsonify

def forbidden(message):
    response = jsonify({'error': 'forbidden', 'massage': message})
    response.status_code = 400
    return response

def unauthorized(message):
    response = jsonify({'error': 'Unauthorized', 'message': message})
    response.status_code = 401
    return response