from ..models import To_Do
from ..api_1_0 import api
from flask import jsonify

@api.route('/usertodos/<int:id>')
def get_user_todos(id):
    todos = To_Do.query.filter_by(author_id=id).all()
    return jsonify({'todos': [todo.to_json() for todo in todos]})

@api.route('/todo/<int:id>')
def get_todo(id):
    todo = To_Do.query.get_or_404(id)
    return jsonify(todo.to_json())