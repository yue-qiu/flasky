from ..api_1_0 import api
from .authentication import auth
from ..models import Post
from flask import jsonify, request, g, url_for
from app import db

@api.route('/posts/')
def get_posts():
    posts = Post.query.all()
    return jsonify({'posts': [post.to_json() for post in posts]})

@api.route('/post/<int:id>/')
def get_post(id):
    post = Post.query.get_or_404(id)
    return jsonify(post.to_json())

@api.route('/posts/', method=['POST'])
def new_post():
    post = Post.from_json(request.json)
    post.author_id = g.current_user.id
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json()), 201, {'Location': url_for('api.get_post', id=post.id, _external=True)}

