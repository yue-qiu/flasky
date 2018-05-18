from ..models import User
from ..api_1_0 import api
from flask import jsonify

@api.route('/users/')
def get_users():
    users = User.query.all()
    return jsonify({'users': [user.to_json() for user in users]})

@api.route('/user/<int:id>')
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.to_json())
