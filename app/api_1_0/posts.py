from ..api_1_0 import api
from ..models import Post
from flask import jsonify, request, g, url_for
from app import db

@api.route('/posts')
def get_posts():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.paginate(
        page, per_page=10, error_out=False
    )
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_posts', page=page-1, _external=True)

    next = None
    if pagination.has_next:
        next = url_for('api.get_posts', page=page+1, _external=True)
    return jsonify({'posts': [post.to_json() for post in posts],
                    'prev': prev,
                    'next': next,
                    'count': pagination.total
                    })
        
@api.route('/usertodos/<int:id>')
def get_user_posts(id):
    posts = Post.query.filter_by(author_id=id).all()
    return jsonify({'posts': [post.to_json() for post in posts]})

@api.route('/post/<int:id>')
def get_post(id):
    post = Post.query.get_or_404(id)
    return jsonify(post.to_json())

@api.route('/posts', methods=['POST'])
def new_post():
    post = Post.from_json(request.json)
    post.author_id = g.current_user.id
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json()), 201, {'Location': url_for('api.get_post', id=post.id, _external=True)}

